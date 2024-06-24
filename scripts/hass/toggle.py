#!/usr/bin/env python3
"""Client for interfacting with Home Assistant API"""

from requests import post, get
from requests import HTTPError


class Client:
    """Base class for interacting with the Home Assistant API"""

    def __init__(self, host, token):
        self.base_url = f"http://{host}:8123/api"
        self.services = host + "/services"
        self._token = token

    def call_service(self, domain, service, entity_id=None, **kwargs):
        """Call a service"""
        url = f"{self.base_url}/{domain}/{service}"
        self.headers = {"Authorization": "Bearer " + self._token}
        data = {"entity_id": entity_id} if entity_id else {}
        return post(url, headers={"Authorization": "Bearer " + self._token}, json=data)

    def set_access_token(self, token):
        """Set the access token to be used for API requests"""
        self.token = token
        return get(f"{self.base_url}/services").json()


# Example usage:
if __name__ == "__main__":
    token = TOKEN = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9 eyJpc3MiOiJjN2ZkNDYzNTQ1ZmU0MTBiOTI5OTdjMzc5MWE4Nzk5YSIsImlhdCI6MTcxODgyNTE4NiwiZXhwIjoyMDM0MTg1MTg2fQ.Yc-CZ8aLKSIq8FAcDh20t8Xa-dQQ7spEYfnBPv3oARc"
    )
    client = Client("10.0.0.50", token)
    client.call_service("")

    # def __setattr__(self, name: str, value, /) -> None:
    #     """Override __setattr__ to handle setting new property attributes"""
    #     if name == "_Client__token":
    #         self.__dict__["_Client__token"] = value
    #         super().__setattr__(name, value)
    #         self._token = value
    #     else:
    #         super().__setattr__(name, value)

    # def get_states(self):
    #     """Get the current states of all entities"""
    #     return get(
    #         f"{self.base_url}/states", headers={"Authorization": "Bearer " + self._Client__token}
    #     ).json()

    # @property
    # def token(self):
    #     """Return the access token"""
    #     return self._Client__token

    # @token.setter
    # def token(self, value):
    #     """Set the access token and update headers"""
    #     self.__dict__["_Client__token"] = value
    #     self.headers = {"Authorization": "Bearer " + value}
