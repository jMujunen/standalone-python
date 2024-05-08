#!/usr/bin/env python3

# dadjoke2sms.py - Send dad jokes on a somewhat regular basis

import os
import sys
import subprocess


""" class Joke:
    def __init__(self):
        pass

    def __setattr__(self, name, value):
        try:
            if name == "my_property":
                self._my_property = value
            else:
                super().__setattr__(name, value)
        except Exception as e:
            return e """

def main():
    dad_joke = subprocess.run(
        "curl -s https://icanhazdadjoke.com/",
        shell=True,
        capture_output=True,
        text=True
    ).stdout.strip()

    send_sms(dad_joke)

if __name__ == '__main__':
    main()