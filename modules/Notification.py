#!/usr/bin/env python3

import subprocess
from typing import Optional


class Notification:
    def __init__(self, **kwargs):
        self.title = kwargs.get("title", "")
        self.msg = kwargs.get("message", "")

    def notify(self, icon: str | None = "kitty", app_name: str | None = "kitty") -> None:
        self.args = ["notify-send", self.title, self.msg]

        self.args.extend([a for a in (icon, app_name) if a])

    def send(self):
        return subprocess.run(self.args, check=True)
