#!/usr/bin/env python3
"""shebang_detect.py - Detect and modify shebangs
Usage: python3 shebang_detect.py <directory>"""

import argparse
import re

from Color import cprint, fg
from fsutils import Dir, Exe

SHEBANG_REGEX = re.compile(r"#!.*")

spec = {
    "py": r"#!/usr/bin/env python",
    "sh": r"#!/bin/bash",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Detect and modify shebangs",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("directory", type=str, help="Directory to search")
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="Limit search to specific extension",
        choices=["py", "sh"],
        default="py",
        required=False,
    )
    parser.add_argument(
        "-m",
        "--missing",
        action="store_true",
        help="Add shebangs to files with missing shebangs",
        required=False,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print each file name and shebang",
        default=False,
        required=False,
    )

    # TODO: Options for modifying shebangs
    # * Add shebangs to files with missing shebangs
    # * Mofidy python to python3
    # * Modify bash to sh
    parser.add_argument(
        "-c",
        "--convert",
        help=r"Convert #!/bin/sh` to `#!/bin/bash and #!/usr/bin/python to #!/usr/bin/python3",
        action="store_true",
        required=False,
    )

    return parser.parse_args()


def main(args):
    directory = Dir(args.directory)
    for item in directory:
        if isinstance(item, Exe) and item.extension.strip(".") == args.file:
            shebang = item.shebang
            new_shebang = SHEBANG_REGEX.sub(spec.get(args.file, ""), shebang)  # Convert to python3
            if args.verbose:
                # Print the file name and shebang
                cprint(item.basename, fg.yellow)
                cprint(f"{shebang}\n", fg.green)

            print(args.file)
            if args.convert:
                item.shebang = new_shebang

            if not SHEBANG_REGEX.match(shebang) and args.missing:  # Add the shebang if it's missing
                item.shebang = new_shebang


if __name__ == "__main__":
    args = parse_args()
    main(args)
