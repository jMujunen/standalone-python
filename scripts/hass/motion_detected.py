#!/usr/bin/env python3

from datetime import datetime
from os import environ
from sys import exit

from requests import post

HOST = environ.get("HASS_HOST", "")
TOKEN = environ.get("HASS_TOKEN", "")


def main(host: str, token: str) -> str:
    headers = {"Authorization": f"Bearer {token}", "content-type": "application/json"}
    url = f"http://{host}:8123/api/states/input_datetime.motion_detected"
    data = {"state": str(datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))}
    return post(url, headers=headers, json=data).text


if __name__ == "__main__":
    exit(main(HOST, TOKEN))
