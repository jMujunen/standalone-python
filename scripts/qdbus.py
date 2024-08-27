#!/usr/bin/env python3
"""A simple wrapper around qdbus6 for querying the D-Bus"""

import subprocess

from Color import cprint, fg, style

IGNORED_METHODS = [
    "method QDBusVariant org.freedesktop.DBus.Properties.Get(QString interface_name, QString property_name)",
    "method QVariantMap org.freedesktop.DBus.Properties.GetAll(QString interface_name)",
    "method void org.freedesktop.DBus.Properties.Set(QString interface_name, QString property_name, QDBusVariant value)",
    "method QString org.freedesktop.DBus.Introspectable.Introspect()",
    "method QString org.freedesktop.DBus.Peer.GetMachineId()",
    "method void org.freedesktop.DBus.Peer.Ping()",
]


class Bus:
    def __init__(self, service: str) -> None:
        self.service = service

    def objects(self) -> list:
        """Return a list of available services on the bus."""
        return [
            service.strip()
            for service in subprocess.run(
                f"qdbus6 {self.service}", shell=True, capture_output=True, text=True, check=False
            ).stdout.split("\n")
            if "org" in service and service != ""
        ]

    def methods(self, obj: str, short=True) -> list:
        """Return a list of available methods on the given service."""
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
        if short:
            return [method.split(".")[-1].split("(")[0] for method in methods]

    def all_methods(self):
        for obj in self.objects():
            yield from [(obj, method) for method in self.methods(obj)]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} (service={self.service}, num_objects={len(self.objects())}, num_methods={sum([len(self.methods(obj)) for obj in self.objects()])})"


def services():
    yield from (
        bus.strip()
        for bus in subprocess.run("qdbus6", shell=True, capture_output=True, text=True, check=False)
        .stdout.strip()
        .split("\n")
        if "org" in bus
    )


"""
Service = org.freedesktop.Notifications
Objects = /org/freedesktop/Notifications/0, /org/freedesktop/Notifications/1
methods = org.kde.Solid.PowerManagement.Actions.BrightnessControl.brightness

"""


def main() -> None:
    for service in services():
        cprint(service, style.bold)
        b = Bus(service)
        objects = b.objects()
        for obj in objects:
            print("\tObject : ", obj)
            methods = b.methods(obj)
            for method in methods:
                print("\t\tMethod : ", method)
        print("---")
    return None


if __name__ == "__main__":
    main()
