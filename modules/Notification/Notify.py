#!/usr/bin/env python3

import subprocess
from typing import Optional


class NotificationBus:
    def __init__(self, **kwargs):
        self.title = kwargs.get("title", "")
        self.msg = kwargs.get("message", "")

    def notify(self, icon: Optional[str] = "kitty", app_name: Optional[str] = "kitty"):
        self.args = ["notify-send", self.title, self.msg]

        self.args.extend([a for a in (icon, app_name) if a])

    def send(self):
        return subprocess.run(self.args, check=True)
