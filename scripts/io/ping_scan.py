#!/usr/bin/env  python3
from ThreadPoolHelper import Pool
import subprocess
import re
import sys
import os
import argparse
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
    result = subprocess.getoutput(f"nmap -O {host} --osscan-limit --host-timeout=15s")
    # Parse the output using regular expressions and list comprehension
    return host, *(
        y[0] if y is not None else "" for y in (re.search(x, result) for x in NMAP_REGEX)
    )


def main(target: str) -> int:
    hosts = subprocess.getoutput(
        rf"nmap -n -sn --min-parallelism=64 {target} | grep -oP '\d+\.\d+\.\d+.\d+'"
    ).splitlines()

    if not hosts:
        print("No hosts found.")
        return 1

    template = "{:<15}|{:<50}|{:<60}|{}"
    pool = Pool()
    print(template.format("Host", "Name", "OS", "TYPE"))
    print(template.format("-" * 15, "-" * 30, "-" * 20, "-" * 4))

    for result in pool.execute(os_detect, hosts, progress_bar=False):
        print(template.format(*result))
    return 0

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Nmap os-detect parallelized using python threads"
    )
    parser.add_argument(
        "target",
        help="""Target to scan. Can either be a single host (0.0.0.0)
        or a range (0.0.0.0/24)""",)
    return parser.parse_args()

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("This script must be run as root.")
        sys.exit(1)
    args = parse_args()
    sys.exit(main(args.target))
