#!/usr/bin/env python3
import argparse
import multiprocessing
import subprocess


def search_directory(directory: str, pattern: str) -> str:
    """Run a find command with multiprocessing."""
    cmd = f"find {directory} -type f -name '{pattern}'"
    return subprocess.check_output(cmd, shell=True).decode("utf-8")


def main(directory: str, pattern: str) -> None:
    # Create a pool of worker processes
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.starmap(search_directory, [(directory, pattern)])

    # Concatenate the results from each process
    all_results = "".join(results)

    print(all_results)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("DIR", help="Directory to search")
    parser.add_argument(
        "-p", "--pattern", help="Pattern to match in filenames", default="*"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    directory = args.DIR
    pattern = args.pattern

    main(directory, pattern)
