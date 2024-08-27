#!/usr/bin/env python3

import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from Color import cprint, fg, style
from ProgressBar import ProgressBar


def set_permissions(path: str, fix) -> tuple[str, str, str, bool] | None:
    """Set permissions for file or directory"""
    if not os.path.exists(path):
        cprint(f"{path} does not exist", fg.red)
        return
    fixed = False
    original_mode = os.stat(path).st_mode
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
    new_mode = os.stat(path).st_mode
    fixed = new_mode != original_mode
    return path, oct(original_mode)[-3:], oct(new_mode)[-3:], fixed


def count_items(directory):
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


def main(path: str, dry_run: bool) -> None:
    num_files = count_items(path)
    real_files = []
    print(f"Found {num_files} files")
    with ProgressBar(num_files) as pb:
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(set_permissions, os.path.join(root, file), not dry_run): file
                for root, dirs, files in os.walk(path)
                for file in files
            }
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        path, mode, new_mode, fixed = result
                        real_files.append((path, mode, new_mode, fixed))
                        # if fixed:

                except Exception as e:
                    cprint(f"{future}: {e}", fg.red)
                finally:
                    pb.increment()
    num_fixed = 0
    for path, mode, new_mode, fixed in real_files:
        if fixed:
            num_fixed += 1
            print(
                f"{path.split("/")[-1]} ({fg.red}{mode}{style.reset} -> \
                    {fg.green}{new_mode}{style.reset})"
            )
    cprint(f"{num_fixed}/{len(real_files)} need fixing", style.bold)


if __name__ == "__main__":
    target = os.getcwd() if len(sys.argv) == 1 else sys.argv[1]
    dry_run = "dry-run" in sys.argv
    cprint(f"Dry-run: {dry_run}", fg.yellow)
    if os.path.isdir(target):
        main(target, dry_run)

    else:
        print("Usage: python3 get-mode.py <directory>")
