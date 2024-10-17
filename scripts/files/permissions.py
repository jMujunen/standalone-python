#!/usr/bin/env python3

import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from Color import cprint, fg, style
from ProgressBar import ProgressBar
from ThreadPoolHelper import Pool


def set_permissions(path: str, fix) -> tuple[str, str, str, bool] | None:
    """Set permissions for file or directory."""
    if not os.path.exists(path):
        cprint(f"{path} does not exist", fg.red)
        return None
    fixed = False
    original_mode = Path.stat(path).st_mode
    mode = original_mode
    if os.path.isdir(path):
        # Read and execute for user; read only for others
        mode |= 0o750
    # Full access for the user, read and execute for others
    elif os.path.isfile(path) and path.endswith((".sh", ".py")):
        mode |= 0o755
    else:
        # No execution bits for regular files (read and write only)
        mode &= ~(0o111)
    if fix:
        os.chmod(path, mode)
    else:
        return path, oct(original_mode)[-3:], oct(mode)[-3:], original_mode != mode
    new_mode = Path.stat(path).st_mode
    fixed = new_mode != original_mode
    return path, oct(original_mode)[-3:], oct(new_mode)[-3:], fixed


def count_items(directory):
    """Count the total number of items in a directory recursively.

    Handles cases where entries may not be accessible due to permissions issues or other OS errors by counting them as well.

    Args:
        directory (str): The path to the directory to count items in.

    Returns:
        int: Total number of items in the directory and its subdirectories.
    """
    total = 0
    for entry in os.scandir(directory):
        try:
            # print(entry)
            total += 1
            if entry.is_symlink():
                continue
            if entry.is_dir():
                # recursively read subdirectories
                total += count_items(entry.path)
        except PermissionError:
            total += 1
        except OSError:
            continue
    return total


def check_and_fix_permissions(real_files, fix=True):
    """Check and fix permissions for a list of files or directories.

    This function checks the current permissions of each item in `real_files` and attempts to fix them if requested. It prints warnings or errors based on the status of each file/directory.

    Parameters
    ------------
        real_files (list): A list of paths to files or directories whose permissions are to be checked and potentially fixed.
        fix (bool, optional): If True, attempt to fix the permissions if they do not match expected values. Defaults to True.

    Returns
    --------
        tuple: A tuple containing:
            - int: The number of items that needed fixing.
            - list: A list of paths that were checked and potentially fixed.

    """
    num_fixed = 0
    checked_paths = []
    for path in real_files:
        original_mode = Path.stat(path).st_mode
        mode = original_mode
        if os.path.isdir(path):
            # Read and execute for user; read only for others
            mode |= 0o750
        elif os.path.isfile(path) and path.endswith((".sh", ".py")):
            # Full access for the user, read and execute for others
            mode |= 0o755
        else:
            # No execution bits for regular files (read and write only)
            mode &= ~(0o111)
        checked_paths.append(path)
        if fix:
            os.chmod(path, mode)
            new_mode = Path.stat(path).st_mode
            fixed = new_mode != original_mode
            num_fixed += int(fixed)
    return num_fixed, checked_paths


if __name__ == "__main__":
    target = os.getcwd() if len(sys.argv) == 1 else sys.argv[1]
    dry_run = "dry-run" in sys.argv
    cprint(f"Dry-run: {dry_run}", fg.yellow)
    if os.path.isdir(target):
        main(target, dry_run)

    else:
        print("Usage: python3 get-mode.py <directory>")
