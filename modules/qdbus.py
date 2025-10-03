#!/usr/bin/env python3
"""A simple wrapper around qdbus6 for querying the D-Bus."""

import argparse
import subprocess

from Color import cprint, fg, style
from ThreadPoolHelper import Pool

IGNORED_METHODS = [
    "method QDBusVariant org.freedesktop.DBus.Properties.Get(QString interface_name, QString property_name)",
    "method QVariantMap org.freedesktop.DBus.Properties.GetAll(QString interface_name)",
    "method void org.freedesktop.DBus.Properties.Set(QString interface_name, QString property_name, QDBusVariant value)",
    "method QString org.freedesktop.DBus.Introspectable.Introspect()",
    "method QString org.freedesktop.DBus.Peer.GetMachineId()",
    "method void org.freedesktop.DBus.Peer.Ping()",
]
from dataclasses import dataclass, field
from enum import Enum


class Bus:
    def __init__(self, service):
        """Initialize a new Bus object for interacting with a specific D-Bus service.
        service (str): The name of the D-Bus service to interact with.
        """
        self.service = service
        self.num_objects = len(self.objects())
        self.num_methods = sum([len(self.methods(obj)) for obj in self.objects()])

    def objects(self) -> list:
        """Return a list of available services on the bus.

        Example:
        --------
        >>> bus = Bus("org.kde.plasmashell")
            bus.objects()
            ['/org','/org/freedesktop', '/org/freedesktop/Notifications', '/org/kde/plasmashell']

        """
        return [
            service.strip()
            for service in subprocess.getoutput(f"qdbus6 {self.service}").split("\n")
            if service != ""
        ]

    def methods(self, obj: str, verbose=False) -> list:
        """Return a list of available methods on the given D-Bus object.

        Example:
        --------
        >>> bus = Bus("org.kde.plasmashell")
            bus.methods("/org/kde/plasmashell")

        >>> ["Activate", "ActivateAction", "Open", "CommandLine", "PropertiesChanged"]
        """
        if "methods" not in self.__dict__:
            methods = {}

        methods = [
            method.strip()
            for method in subprocess.run(
                ["qdbus6", self.service, obj],
                capture_output=True,
                text=True,
                check=False,
            ).stdout.split("\n")
            if method != "" and method not in IGNORED_METHODS
        ]
        if not verbose:
            return [method.split(".")[-1].split("(")[0] for method in methods]
        return methods

    def all_methods(self, verbose=False) -> dict[str, list[str]]:
        """Generate a sequence of tuples containing object and method pairs."""
        return {obj: list(self.methods(obj, verbose)) for obj in self.objects()}

    def get_properties(self, obj: str):  # -> dict[str, str]:
        """Return a dictionary of properties with their values for the given D-Bus object."""
        for method in self.methods(obj, verbose=True):
            if method.split(" ")[0] == "property":
                try:
                    method_type, _, return_type, method = method.split(" ")
                    method_value = subprocess.run(
                        ["qdbus6", self.service, obj, method],
                        capture_output=True,
                        text=True,
                        check=False,
                    ).stdout.strip()
                    yield (method.split("(")[0].split(".")[-1], method_value)
                except Exception:
                    pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(service={self.service}, num_objects={len(self.objects())}, num_methods={sum([len(self.methods(obj)) for obj in self.objects()])})"

    @staticmethod
    def __iter__(bus: "Bus"):
        return Bus(bus).all_methods()


def services():
    """Yield all available D-Bus services."""
    yield from (
        bus.strip()
        for bus in subprocess.run("qdbus6", shell=True, capture_output=True, text=True, check=False)
        .stdout.strip()
        .split("\n")
        if "org" in bus and "systemd1" not in bus and "InputDevice" not in bus
    )


def muliprocessing(bus: Bus, verbose: bool):
    return bus.all_methods(verbose), bus.service


def main(scope: list[str], verbose: bool) -> None:
    # Get a list of all available D-Bus objects on this each service
    pool = Pool()
    print(len(scope))
    if len(scope) <= 1:
        busses = [Bus(service) for service in services()]
    else:
        busses = [Bus(service) for service in scope]
    for result in pool.execute(muliprocessing, busses, verbose, progress_bar=False):
        if result:
            mapping, service = result
            cprint(f"\n{service}", style.bold)
            print("--------------------------")
            for obj, methods in mapping:
                if methods:
                    cprint(obj, style.bold, style.underline)
                    for method in methods:
                        print(f"\t{method}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List all available D-Bus objects and methods")
    parser.add_argument(
        "SERVICES",
        nargs="*",
        help="""Service name to list. If no service is specified, then all services will be listed.""",
        default=[""],
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
        default=False,
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.SERVICES, args.verbose)


"""
Service = org.freedesktop.Notifications
Objects = /org/freedesktop/Notifications/0, /org/freedesktop/Notifications/1
methods = org.kde.Solid.PowerManagement.Actions.BrightnessControl.brightness

"""
