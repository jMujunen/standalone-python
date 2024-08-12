#!/usr/bin/env python3
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from Color import cprint, fg, style
from fsutils import Dir, File
from ProgressBar import ProgressBar

# from ThreadPoolHelper import Pool


def parser_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find duplicate files of all types")
    parser.add_argument("PATH", help="First directory to compare against")
    parser.add_argument("OTHER_PATH", help="Second directory to compare against")
    args = parser.parse_args()
    return args


def process_file(file: File, second: Dir) -> tuple[str, str] | None:
    try:
        if file.exists and file in second:
            other = second.file_info(file.basename)
            if other and file == other:
                return other.path, file.path
    except Exception as e:
        cprint(e, fg.red)


def main(first: Dir, second: Dir) -> None:
    dupes = []
    # pool = Pool()
    with ProgressBar(len(second)) as p:
        with ThreadPoolExecutor() as executer:
            futures = [executer.submit(process_file, file, second) for file in first]
            for future in as_completed(futures):
                p.increment()
                result = future.result()
                if result:
                    dupes.append(result)
                if len(dupes) % 100 == 0:
                    cprint(f"Dupes: {len(dupes)}", style.bold, style.underline)
                    with open(f"{first.path}-DUPES.log", "a") as f:
                        f.write("\n".join(dupes))
                        dupes = []


if __name__ == "__main__":
    args = parser_args()
    first = Dir(args.PATH)
    second = Dir(args.OTHER_PATH)
    dupes = main(first, second)
    # with open("dupes.log", "w") as f:
