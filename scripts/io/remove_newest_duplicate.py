#!/usr/bin/env python3

import itertools
import os
from sys import exit

from Color import cprint, fg
from fsutils.dir import Dir, obj
from ThreadPoolHelper import Pool


def gen_stat(lst):
    for pair in itertools.combinations(lst, 2):
        pair = obj(pair[0]), obj(pair[1])
        yield zip(*(p.stat()[-3:] for p in pair), strict=False)


def determine_originals(file_paths: list[str], num_keep: int) -> set[str]:
    """Given a list of file paths and the number of duplicates to keep,
    return a list of file paths that should be kept.

    Parameters
    -----------
        - `file_paths (list[str])`: A list of file paths.
        - `num_keep (int)`: The number of duplicates to keep
    """
    oldest_to_newest = sorted(file_paths, key=lambda x: os.path.getmtime(x), reverse=False)
    keep = []
    remove = []
    for i, path in enumerate(oldest_to_newest):
        if i < num_keep:
            keep.append(path)
        else:
            for st_result in gen_stat(oldest_to_newest):
                for st in st_result:
                    if st[0] != st[1] and st[0] < st[1]:
                        break
                remove.append(path)
    return set(remove)


def main(path: Dir, num_keep: int) -> int:
    db = path.load_database()
    pool = Pool()
    for result in pool.execute(
        determine_originals, db.values(), progress_bar=False, num_keep=num_keep
    ):
        if result:
            cprint(f"Removing{'\n'.join(result)}", fg.red)
            print()
    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser("Remove newest files for duplicates found in <PATH>")
    parser.add_argument("path", help="Path to start search from")
    parser.add_argument("-n", "--num", default=1, type=int, help="Number of duplicates to keep")
    args = parser.parse_args()
    dir_object = Dir(args.path)
    if not dir_object.exists():
        print("Path does not exist.")
        exit(1)
    exit(main(dir_object, args.num))
