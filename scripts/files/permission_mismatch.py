#!/usr/bin/env python3

import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from Color import cprint, fg, style
from ExecutionTimer import ExecutionTimer
from fsutils import Dir, Exe, File, Git
from ProgressBar import ProgressBar

SPECS = {
    File: 644,
    Dir: 755,
    Exe: 755,
    Git: 444,
}


def get_permissions(file: File) -> tuple[File, bool, int, int] | None:
    """Set permissions for file or directory"""
    if not os.path.exists(file.path):
        cprint(f"{file.path} does not exist", fg.red)
        return
    mode = file.mode
    if file.__class__ in list(SPECS.keys()):
        preferred_mode = SPECS.get(file.__class__, 644)
    else:
        preferred_mode = 644

    if mode != preferred_mode:
        return file, False, mode, preferred_mode
    return file, True, mode, preferred_mode


def main(path: Dir) -> None:
    num_files = len(path)
    num_flagged = 0
    flagged = []
    with ProgressBar(num_files) as p:
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(get_permissions, f): f for f in path.objects}
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result and not result[1]:
                        file, is_good, mode, preffered = result
                        # print(f"{file.path:<80} ({file.mode}, {preffered})")
                        num_flagged += 1
                        flagged.append((file, mode, preffered))
                    elif not result:
                        cprint(result, fg.yellow)
                except Exception as e:
                    cprint(f"{future}: {e}", fg.red)
                finally:
                    p.increment()
    for file, mode, preffered in flagged:
        print(
            f"{file.path:<80} ({fg.red}{mode}{style.reset}, {fg.green}{preffered}{style.reset}, {(file.__class__.__name__)})"
        )
    print("\n\n")
    print(f"{style.bold}{num_flagged}/{num_files}{style.reset} have mismatched permissions")


if __name__ == "__main__":
    with ExecutionTimer():
        if len(sys.argv) == 2 and os.path.isdir(sys.argv[1]):
            path = Dir(sys.argv[1])
            print(f'{"Path":<80} (current mode, preffered mode)')
            main(path)
        else:
            print("Usage: python3 perm_mismatch.py <directory>")
            sys.exit(1)
        sys.exit(0)
