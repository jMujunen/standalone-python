#!/usr/bin/env python3

# TODO: Add an support for sorting (by name, size, date installed, ect..)

import sys
import importlib
import csv
import json

# Functions for returning every native, thrid party and or custom module, script, library, ect..


def get_modules():
    return sys.modules


def get_modules_as_list():
    return list(sys.modules)


def get_modules_as_dict():
    return dict(sys.modules)


def get_modules_as_json():
    return json.dumps(sys.modules)


def get_modules_as_csv():
    return csv.writer(sys.modules)


# Example usage
if __name__ == "__main__":
    for module in get_modules():
        print(module)
