#!/usr/bin/env python3

# exetimer.py - Runs a command and prints the execution time

import argparse
import subprocess
import threading

from ExecutionTimer import ExecutionTimer


def parse_args():
    parser = argparse.ArgumentParser(description="Run a command and print the execution time")
    parser.add_argument("command", help="Command to run")

    parser.add_argument("args", help="Command arguments", nargs="*", default=[])
    return parser.parse_args()


def output_reader(stream, tag):
    try:
        for line in stream:
            print(f"{line}", end="")
    except Exception:
        pass


def main(args):
    output = subprocess.Popen(
        f'{args.command} {" ".join(args.args)}',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    try:
        # Theading for preserving output order
        stdout_thread = threading.Thread(target=output_reader, args=(output.stdout, "stdout"))
        stderr_thread = threading.Thread(target=output_reader, args=(output.stderr, "stderr"))
        stdout_thread.start()
        stderr_thread.start()

        # Wait for completion
        stdout_thread.join()
        stderr_thread.join()
    except Exception:
        pass
    # Return exit code
    # return process.wait()


# Example usage
if __name__ == "__main__":
    try:
        # Start exceution timer
        with ExecutionTimer():
            args = parse_args()
            main(args)
            exit(0)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
