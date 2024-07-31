#!/usr/bin/env python3
"""Client for interfacting with Home Assistant API"""

import json
import subprocess
from os import environ
from typing import Any, Dict, List

import requests

TOKEN = environ["HASS_TOKEN"]
HOST = environ["HASS_HOST"]


def call_service(domain: str, service: str, entity_id=None, **kwargs) -> requests.Response:
    """Call a service on the Home Assistant API."""
    base_url = f"http://{HOST}:8123/api/services"
    url = f"{base_url}/{domain}/{service}"
    data = {"entity_id": entity_id} if entity_id else {}
    headers = {"Authorization": "Bearer " + TOKEN}
    print(base_url)
    print(url)
    print(data)
    response = requests.post(
        url,
        headers=headers,
        json=data,
    )
    return response


def domains() -> List[str]:
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
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        # for domain in Client():
        for domain in ["switch", "weather", "service"]:
            setattr(cls, domain, DomainDispatcher(cls, domain))


class Client(metaclass=MetaClient):
    """Base class for interacting with the Home Assistant API"""

    def __init__(self, host=HOST, token=TOKEN) -> None:
        self.base_url = f"http://{host}:8123/api/services"
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
    def head(self) -> Dict[str, str]:
        return {"Authorization": "Bearer " + self.token}

    @property
    def api_reference(self) -> Dict[str, str]:
        self.head["content-type"] = "application/json"
        response = requests.get(self.base_url, headers=self.head)
        self._domains = json.loads(response.content)
        self.response = response.status_code
        return self._domains

    @property
    def domains(self) -> List[str]:
        """Get a list of all available domains."""
        return [domain for domain in self._dict.keys()]

    @property
    def entities(self):
        # TODO: Integrate this
        # Extract all unique domains and entities
        entities = set()
        for item in self.api_reference:
            for service in item["services"]:
                if (
                    "target" in item["services"][service]
                    and "entity" in item["services"][service]["target"]
                ):
                    for entity in item["services"][service]["target"]["entity"]:
                        entities.add((item["domain"], service, entity))
        print("All Entities:", list(entities))

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

        Returns:
        ---------
            requests.Response: The response object from the POST request made to the Home Assistant API.

        Raises:
        --------
            HTTPError: If an error occurs during the HTTP request, it will raise an HTTPError.
        """
        base_url = f"http://{kwargs.get("host")}:8123/api/services"
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
        return self.domains


# Example usage:
if __name__ == "__main__":
    client = Client(HOST, TOKEN)
    domains = client.domains
    client.switch.toggle("office_lamp")
