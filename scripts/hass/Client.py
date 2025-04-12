#!/usr/bin/env python3
"""Client for interfacting with Home Assistant API."""

import json
import subprocess
from enum import Enum
from os import environ
from typing import Any, Dict, List, Tuple
from dataclasses import dataclass, field
import requests

TOKEN: str = environ["HASS_TOKEN"]
HASS_HOST: str = environ["HASS_HOST"]
BASE_URL: str = f"http://{HASS_HOST}:8123/api"
SERVICES_URL: str = f"{BASE_URL}/services"
STATES_URL: str = f"{BASE_URL}/states"


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

    entity_id: str = field(default_factory=str)
    state: str = field(default_factory=str)
    attributes: dict = field(default_factory=dict)
    last_changed: str = field(default_factory=str)
    last_updated: str = field(default_factory=str)

    def __post_init__(self) -> None:
        if isinstance(self.entity_id, dict):
            self.__dict__.update(self.entity_id)


def call_service(domain: str, service: str, entity_id=None, **kwargs) -> requests.Response:
    """Call a service on the Home Assistant API."""
    base_url = f"http://{HASS_HOST}:8123/api/services"
    url = f"{base_url}/{domain}/{service}"
    data = {"entity_id": entity_id} if entity_id else {}
    headers = {"Authorization": "Bearer " + TOKEN}
    print(base_url)
    print(url)
    print(data)
    return requests.post(
        url,
        headers=headers,
        json=data,
    )


def domains() -> list[str]:
    """Get a list of all domains available on the Home Assistant API."""
    return []


class DomainDispatcher:
    def __init__(self, client_instance, domain):
        self.client = client_instance
        self.domain = domain

    def __getattr__(self, service):
        return ServiceDispatcher(self.client, self.domain, service)


class ServiceDispatcher:
    def __init__(self, client_instance: "Client", domain: str, service: str):
        self.client = client_instance
        self.domain = domain
        self.service = service

    def __call__(self, entity_id):
        return call_service(
            self.domain,
            self.service,
            entity_id,
        )


class MetaClient(type):
    """Metaclass for creating a client with domain dispatchers."""

    def __new__(cls, name, bases, dct):
        new_class = super().__new__(cls, name, bases, dct)
        new_class._initialize_domains()
        return new_class

    @classmethod
    def _initialize_domains(cls) -> None:
        for domain in ["switch", "weather", "service"]:
            setattr(cls, domain, DomainDispatcher(None, domain))


class MetaClientV2(type):
    """Metaclass for creating a client with domain dispatchers."""

    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        # for domain in Client():
        for domain in ["switch", "weather", "service"]:
            setattr(cls, domain, DomainDispatcher(cls, domain))


class Client(metaclass=MetaClient):
    """Base class for interacting with the Home Assistant API."""

    _domains: dict[dict[str, str], str]

    def __init__(self, host=HASS_HOST, token=TOKEN) -> None:
        """Initialize a new Client instance.

        Args:
            host (str, optional): The hostname or IP address of the Home Assistant instance.
            token (str, optional): The access token for authentication. Defaults to TOKEN.
        """
        self.url = f"http://{host}:8123/api"
        self.base_url = f"http://{host}:8123/api/services"
        self.headers = {"Authorization": f"Bearer {token}", "content-type": "application/json"}
        self.host = host
        self.token = token
        self._api_reference = []
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
        response = requests.get(self.base_url, headers=self.head)
        self._domains = json.loads(response.content)
        self.response = response.status_code
        return self._domains

    @property
    def domains(self) -> list[str]:
        """Get a list of all available domains."""
        return list(self._dict.keys())

    @property
    def entities(self) -> list[tuple[str, ...]]:
        entities = []
        for item in self.api_reference:
            for service in item["services"]:
                if (
                    "target" in item["services"][service]
                    and "entity" in item["services"][service]["target"]
                ):
                    for entity in item["services"][service]["target"]["entity"]:
                        entities.append((item["domain"], service, entity))
        return entities

    @property
    def _dict(self) -> dict:
        nested_dict = {}
        for item in self.api_reference:
            if item["domain"] not in nested_dict:
                nested_dict[item["domain"]] = {"services": {}}
            for service in item["services"]:
                nested_dict[item["domain"]]["services"][service] = item["services"][service]
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
        data = {"entity_id": entity_id} if entity_id else {}
        response = requests.post(
            url,
            headers=kwargs.get("headers"),
            json=data,
        )
        self.response = response.status_code
        return response

    def commands(self, domain: str) -> list:
        """Get a list of all available services for the specified domain."""
        for item in self.api_reference:
            if item["domain"] == domain:
                return list(item["services"].keys())
        return []

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

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        for domain in self.domains:
            attribute = setattr(self, domain)
            yield attribute(*args, **kwds)
        # return self.domains

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
        return Entity(self.get_state(entity_id))

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


class HomeAssistantClient:
    """Client for interacting with the Home Assistant API."""

    def __init__(self, host: str = HASS_HOST, token: str = TOKEN) -> None:
        self.host = host
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self._domains = None
        self.response = None

    @property
    def alive(self) -> bool:
        """Check the status of the client connection."""
        return (
            subprocess.run(
                ["ping", "-c", "1", "-w", "3", "-W", "3", "-t", "3", "-q", self.host],
                stdout=subprocess.DEVNULL,
                check=False,
            ).returncode
            == 0
        )

    def _api_call(
        self, url: str, method: str = "GET", data: dict | None = None
    ) -> requests.Response:
        """Make an API call to Home Assistant."""
        if method == "GET":
            response = requests.get(url, headers=self.headers)
        elif method == "POST":
            response = requests.post(url, headers=self.headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        response.raise_for_status()
        return response

    def _get_api_reference(self) -> list[dict]:
        """Get the API reference from Home Assistant."""
        if self._domains is None:
            response = self._api_call(SERVICES_URL)
            self._domains = response.json()
        return self._domains

    @property
    def domains(self) -> list[str]:
        """Get a list of all available domains."""
        return [domain["domain"] for domain in self._get_api_reference()]

    @property
    def entities(self) -> list[tuple[str, str, str]]:
        """Get a list of all entities."""
        entities = []
        for domain_info in self._get_api_reference():
            for service_name, service_info in domain_info["services"].items():
                if "target" in service_info and "entity" in service_info["target"]:
                    for entity_id in service_info["target"]["entity"]:
                        entities.append((domain_info["domain"], service_name, entity_id))
        return entities

    def call_service(
        self, domain: str, service: str, entity_id: str | None = None, **kwargs
    ) -> requests.Response:
        """Call a service on the Home Assistant API."""
        url = f"{SERVICES_URL}/{domain}/{service}"
        data = {"entity_id": entity_id} if entity_id else {}
        data.update(kwargs)
        return self._api_call(url, method="POST", data=data)

    def commands(self, domain: str) -> list[str]:
        """Get a list of all available services for the specified domain."""
        for domain_info in self._get_api_reference():
            if domain_info["domain"] == domain:
                return list(domain_info["services"].keys())
        return []

    def domain_api(self, domain: str) -> list[tuple[str, str]]:
        """Get a list of all API calls for the specified domain."""
        api_calls = []
        for domain_info in self._get_api_reference():
            if domain_info["domain"] == domain:
                for service_name in domain_info["services"]:
                    api_calls.append((domain_info["domain"], service_name))
        return api_calls

    def get_state(self, entity_id: str) -> dict[str, Any]:
        """Get the state of an entity."""
        url = f"{STATES_URL}/{entity_id}"
        response = self._api_call(url)
        return response.json()

    def set_state(self, entity_id: str, value: Any, attributes: dict | None = None) -> str:
        """Set the state of an entity."""
        url = f"{STATES_URL}/{entity_id}"
        data = {"state": value}
        if attributes:
            data["attributes"] = attributes
        response = self._api_call(url, method="POST", data=data)
        return str(response.status_code)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(host={self.host}, response={self.response}, alive={self.alive})".format(
            **vars(self)
        )


# Example usage:
if __name__ == "__main__":
    client = HomeAssistantClient(HASS_HOST, TOKEN)
    domains = client.domains
    print(f"Available domains: {domains}")
    client.call_service("switch", "toggle", entity_id="office_lamp")
