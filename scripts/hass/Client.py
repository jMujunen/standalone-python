#!/usr/bin/env python3
"""Client for interfacting with Home Assistant API."""

import json
import subprocess
from enum import Enum
from os import environ
from dataclasses import dataclass, field
import requests
from BaseClient import BaseClient
from typing import Any
import datetime

import re

TOKEN: str = environ["HASS_TOKEN"]
HASS_HOST: str = environ["HASS_HOST"]
BASE_URL: str = f"http://{HASS_HOST}:8123/api"
SERVICES_URL: str = f"{BASE_URL}/services"
STATES_URL: str = f"{BASE_URL}/states"


class Convert(Enum):
    """Entity state type conversion specifiers."""

    DATETIME = (
        re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{6})?\+\d{2}:\d{2}$"),
        datetime.datetime.fromisoformat,
    )
    FLOAT = (re.compile(r"^[-+]?\d*\.\d+$"), float)
    INT = (re.compile(r"^[-+]?\d+$"), int)
    BOOL = (re.compile(r"^(True|False)$"), bool)
    NONE = (re.compile(r"^unavailable|unknown$"), lambda x: None)

    def __init__(self, pattern: re.Pattern, type_: Any):
        """Initialize the conversion specifier."""
        self.pattern = pattern
        self.type = type_

    def __call__(self, value: Any) -> Any:
        """Convert the given value to the specified type."""
        if self.pattern.match(value):
            return self.type(value)
        return value


class StatusCode(Enum):
    OK = 200
    OK_CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    BAD_AUTHENTICATION = 403
    NOT_FOUND = 404
    BAD_METHOD = 405
    INTERNAL_ERROR = 500


@dataclass
class Entity:
    """Represents an entity in Home Assistant."""

    entity_id: str
    state: str
    last_changed: datetime.datetime
    last_reported: datetime.datetime
    last_updated: datetime.datetime
    attributes: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Post-initialization hook."""
        for k, v in self.__dict__.items():
            if isinstance(v, str):
                for c in Convert:
                    if c.pattern.match(v):
                        setattr(self, k, c.type(v))
                        break


class Client(BaseClient):
    """Base class for interacting with the Home Assistant API."""

    _domains: dict[dict[str, str], str]

    def __init__(self, host=HASS_HOST, token=TOKEN) -> None:
        """Initialize a new Client instance.

        Args:
            host (str, optional): The hostname or IP address of the Home Assistant instance.
            token (str, optional): The access token for authentication. Defaults to TOKEN.
        """

        self.url = f"http://{host}:8123/api"
        super().__init__(self.url, api_key=token)

        # self.base_url = f"http://{host}:8123/api"
        # self.headers = {"Authorization": f"Bearer {token}", "content-type": "application/json"}
        self.host = host
        self.token = token
        self.response = None

    @property
    def alive(self) -> bool:
        """Check the status of the client connection."""
        return not bool(
            subprocess.run(
                ["ping", "-c 1", "-w 3", "-W 3", "-t 3", "-q", self.host],
                stdout=subprocess.DEVNULL,
                check=False,
            ).returncode
        )

    @property
    def head(self) -> dict[str, str]:
        return {"Authorization": "Bearer " + self.token}

    @property
    def api_reference(self) -> dict[dict[str, str], str]:
        self.head["content-type"] = "application/json"
        url = f"{self.base_url}/services"
        response = requests.get(url, headers=self.head)
        self._domains = json.loads(response.content)
        self.response = response.status_code
        return self._domains

    @property
    def states(self) -> list[Entity]:
        """Get a list of all available states."""
        return [Entity(**result) for result in self.res("GET", "states").json()]

    @property
    def domains(self) -> list[str]:
        """Get a list of all available domains."""
        return list(self._dict.keys())

    @property
    def _dict(self) -> dict:
        nested_dict = {}
        for item in self.api_reference:
            if item["domain"] not in nested_dict:
                nested_dict[item["domain"]] = {"services": {}}
            for service in item["services"]:
                nested_dict[item["domain"]]["services"][service] = item["services"][
                    service
                ]
        return nested_dict

    def call_service(
        self, domain: str, service: str, entity_id=None, **kwargs
    ) -> requests.Response:
        """Call a service on the Home Assistant API.

        Paramters:
        ---------
            domain (str): The domain of the service to be called. (switch, sensor)
            service (str): The specific service within the domain to be called.
            entity_id (str, optional): The ID of the entity for which the service is intended. Defaults to None.
            **kwargs: Additional keyword arguments that will be included in the request payload.

        Returns
        ---------
            requests.Response: The response object from the POST request made to the Home Assistant API.

        Raises
        --------
            HTTPError: If an error occurs during the HTTP request, it will raise an HTTPError.
        """
        base_url = f"http://{kwargs.get('host')}:8123/api/services"
        url = f"{base_url}/{domain}/{service}"
        print(f"POST {url} {kwargs}")
        print(base_url)
        data = {"entity_id": entity_id} if entity_id else {}
        response = requests.post(
            url,
            headers=kwargs.get("headers"),
            json=data,
        )
        self.response = response.status_code
        return response

    def domain_api(self, domain) -> list:
        api_calls = []
        for item in self.api_reference:
            if item["domain"] == domain:
                for service in item["services"]:
                    api_calls.append((item["domain"], service))
        return api_calls

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(host={self.host}, base_url={self.base_url}, response={self.response}, alive={self.alive})".format(
            **vars(self)
        )

    def get_state(self, entity_id: str) -> dict[str, Any]:
        """Get the state of an entity.

        Parameters
        -----------
            entity_id (str): The ID of the entity (e.g., sensor.temperature_1).

        Returns
        --------
            dict | str : The state data as a dictionary if successful, else the reason for failure.
        """
        url = f"{self.url}/states/{entity_id}"
        response = requests.get(url, headers=self.headers)
        return (
            response.json()
            if response.status_code == StatusCode.OK.value
            else {"error:": response.reason}
        )

    def entity(self, entity_id: str) -> Entity:
        """Retrieve an entity by its ID."""
        return Entity(**self.get_state(entity_id))

    def set_state(self, entity_id: str, value: Any, attributes: Any = None) -> str:
        """Set the state of an entity.

        Paramters:
        ----------
            entity_id (str): The entity id of the Home Assistant instance.
            value (Any): The new state of the entity.

        Returns
        ---------
            int: The HTTP status code of the request.
        """
        url = f"{self.url}/states/{entity_id}"
        data = {"state": value}
        if attributes:
            data["attributes"] = attributes
        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code != StatusCode.OK.value:
            return f"{response.status_code}: {response.reason}"
        return f"{response.status_code}"


# Example usage:
if __name__ == "__main__":
    client = Client(HASS_HOST, TOKEN)
    domains = client.domains
    print(f"Available domains: {domains}")
    client.call_service("switch", "toggle", entity_id="office_lamp")
