#!/usr/bin/env python3
import subprocess
import os

from Color import cprint, fg, style


def update_tools() -> int:
    try:
        subprocess.run(["uv", "tool", "upgrade", "--all"], check=True)
        cprint("Successfully updated uv tools.", fg.green)
        return 0
    except subprocess.CalledProcessError as e:
        cprint(f"Failed to update uv tools: {e}", fg.red)
        return 1


def update_pipx() -> int:
    try:
        subprocess.run(["pipx", "upgrade-all"], check=True)
        cprint("Successfully updated pipx.", fg.green)
        return 0
    except subprocess.CalledProcessError as e:
        cprint(f"Failed to update pipx: {e}", fg.red)
        return 1


def update_pip_packages(target: str = "./") -> int:
    print(target)
    os.chdir(target)
    subprocess.run(["source .venv/bin/activate"], shell=True, check=False)
    outdated = subprocess.getoutput(
        "uv pip list --outdated | awk '{print $1}' | grep -oP '^[a-z0-9_]+(-?[a-z0-9]+)?'"
    )
    if not outdated:
        cprint("All pip packages are up to date.", fg.green)
        return 0
    print(outdated)
    outdated = outdated.splitlines()
    print(f"Updating {len(outdated)} packages in {target} ...")

    for package in outdated:
        cprint.info(f"Updating package: {package}...")
        try:
            result = subprocess.run(
                ["uv", "pip", "install", "--directory", target, "-U", package],
                check=True,
                capture_output=True,
                text=True,
            )
            cprint(f"Successfully updated {package}.", fg.green)
        except subprocess.CalledProcessError as e:
            print(f"{fg.red}Error{style.reset}: {e.stderr}")
            continue
    return 0


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Update uv, pipx, and pip package.")
    parser.add_argument("--pip", action="store_true", help="Only update pip packages")
    parser.add_argument(
        "--target",
        "-t",
        type=str,
        default="./",
        help="Location to the package virtual environment. Updates all pip packages in this directory.",
    )
    args = parser.parse_args()

    if args.pip:
        sys.exit(update_pip_packages(args.target))

    sys.exit(update_pipx() or update_pip_packages())
