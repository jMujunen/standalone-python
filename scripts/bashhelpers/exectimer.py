#!/usr/bin/env python3
"""exetimer.py - Runs a command and prints the execution time."""

import sys
import argparse
import subprocess
import threading
from typing import IO

from ExecutionTimer import ExecutionTimer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a command and print the execution time")
    parser.add_argument("prog", help="Program to run")

    parser.add_argument("args", help="Command arguments", nargs=argparse.REMAINDER)
    parser.add_argument("--no-header", help="Show header", action="store_false")
    return parser.parse_args()


def output_reader(stream: IO[str], tag: str = "") -> None:
    if stream is None:
        return
    for line in stream:
        print(f"{tag}{line}", end="")


def main(prog: str, *args) -> int:
    output = subprocess.Popen(
        rf"{prog} {' '.join(args)}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )

    # Theading for preserving output order
    stdout_thread = threading.Thread(target=output_reader, args=(output.stdout, ""))
    stderr_thread = threading.Thread(target=output_reader, args=(output.stderr, "stderr:"))
    stdout_thread.start()
    stderr_thread.start()

    # Wait for completion
    stdout_thread.join()
    stderr_thread.join()

    # Return exit code
    return 0


# Example usage
if __name__ == "__main__":
    main("")
    import sys

    try:
        # Start execution timer
        with ExecutionTimer():
            args = parse_args()
            if args.no_header:
                print(f"\033[1m{args.prog}\033[0m \033[3m{' '.join(args.args)}\033[0m")

            sys.exit(main(args.prog, *args.args))

    except Exception as e:
        print(f"\033[31mException occurred:\033[0m {e}")
        sys.exit(1)
