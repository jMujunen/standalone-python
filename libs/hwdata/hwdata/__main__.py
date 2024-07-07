#!/usr/bin/env python3
"""__main__.py - Command-line interface for HWINFO"""

import sys
import argparse
from . import __init__ as hwdata_init
from .CPU import CpuData
from .GPU import GpuData
from .DISK import Disk
from .SYS import Temp, RAM, Misc
from .NET import Interface


def main():
    parser = argparse.ArgumentParser(description="Query hardware information.")
    subparsers = parser.add_subparsers(dest="command")

    # CPU command
    cpu_parser = subparsers.add_parser("cpu", help="Display CPU information.")

    # GPU command
    gpu_parser = subparsers.add_parser("gpu", help="Display GPU information.")

    # Disk command
    disk_parser = subparsers.add_parser("disk", help="Display disk usage information.")
    disk_parser.add_argument("mountpoint", type=str, help="The mount point of the disk to query.")

    # RAM command
    ram_parser = subparsers.add_parser("ram", help="Display RAM information.")
    ram_parser.add_argument(
        "--swap", action="store_true", help="Query swap memory instead of physical RAM."
    )
    ram_parser.add_argument("--usage", action="store_true", help="Query RAM usage as a percent.")

    # Network interface command
    net_parser = subparsers.add_parser("net", help="Display network interface information.")
    net_parser.add_argument(
        "--interface", type=str, default="wlan0", help="Specify the network interface to query."
    )

    # Temperature command
    temp_parser = subparsers.add_parser("temp", help="Display temperature information.")

    # Parse arguments and execute commands
    args = parser.parse_args()

    if hasattr(args, "command"):
        hwdata_init()  # Ensure the package is initialized

        if args.command == "cpu":
            cpu = CpuData()
            print(f"CPU Name: {cpu.name}")
            print(f"Max Clock Speed: {cpu.max_clock()} MHz")
            print(f"Average Temperature: {cpu.average_temp}°C")

        elif args.command == "gpu":
            gpu = GpuData()
            print(f"GPU Name: {gpu.name}")
            print(f"Temperature: {gpu.temp()}°C")

        elif args.command == "disk":
            disk = Disk(args.mountpoint)
            print(f"{disk.friendly_name or args.mountpoint}: {disk.percent_used()}% used")

        elif args.command == "ram":
            ram = RAM()
            print(f"Total RAM: {ram.total / (1024 ** 3)} GB")
            print(f"Available RAM: {ram.available / (1024 ** 3)} GB")

        elif args.command == "net":
            net = Interface(args.interface)
            print(f"Interface: {net.interface}")
            print(f"Online Status: {net.online}")
            if net.online == "online":
                addresses = net.addresses()
                for ip, netmask in addresses:
                    print(f"IP Address: {ip}, Netmask: {netmask}")

        elif args.command == "temp":
            temp = Temp()
            print("CPU Temperatures:")
            for core, temperature in temp.cpu_temps().items():
                print(f"Core {core}: {temperature}°C")
            print("\nGPU Temperature:")
            print(f"Temperature: {temp.gpu_temp()}°C")

        else:
            parser.print_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
t
