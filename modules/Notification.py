#!/usr/bin/env python3

# Notification.py - Resuable notification class

import gi.repository
gi.require_version('Notify', '0.7')
from gi.repository import Notify

class Notification:
    def __init__(self, title, msg):
        self.title = title
        self.msg = msg
        Notify.init(self.title)
        self.notification = Notify.Notification.new(self.title, self.msg)

    def show(self):
        self.notification.show()

if __name__ == "__main__":
    n = Notification("Your Title Here", "Your Message Here")
    n.show()
