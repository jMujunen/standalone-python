#!/usr/bin/env  python3
from ThreadPoolHelper import Pool
import subprocess
import re
import sys
import os

# OS, DEV_TYPE, DEV_NAME regex patterns for parsing nmap output
NMAP_REGEX = [
    re.compile(r"(?<=(?:\w{2}:){5}\w{2}\s)\((.*)\)"),
    re.compile(r"(?<=Running: ).*"),
    re.compile(r"(?<=Device type: ).*"),
]


def os_detect(host: str) -> tuple[str, ...]:
    """Detect the operating system of a host using nmap.

    Args:
        host (str): The IP address or hostname to scan.

    Returns:
        tuple[str, str, str]: A tuple containing (OS, DEV_TYPE, DEV_NAME)
    """

    # Run the nmap command to detect the OS
    result = subprocess.getoutput(f"nmap -O {host} --host-timeout=15s")
    # Parse the output using regular expressions and list comprehension
    return host, *(
        y[0] if y is not None else "" for y in (re.search(x, result) for x in NMAP_REGEX)
    )


def main() -> None:
    hosts = subprocess.getoutput(
        r"nmap -n -sn --min-parallelism=64 10.0.0.0/24 | grep -oP '\d+\.\d+\.\d+.\d+'"
    ).splitlines()

    if not hosts:
        print("No hosts found.")
        return

    template = "{:<15}|{:<50}|{:<60}|{}"
    pool = Pool()
    print(template.format("Host", "Name", "OS", "TYPE"))
    print(template.format("-" * 15, "-" * 30, "-" * 20, "-" * 4))

    for result in pool.execute(os_detect, hosts, progress_bar=False):
        print(template.format(*result))


if __name__ == "__main__":
    if os.geteuid() != 0:
        print("This script must be run as root.")
        sys.exit(1)
    main()
    sys.exit(0)
