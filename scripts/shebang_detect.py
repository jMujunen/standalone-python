#!/usr/bin/env python3

# shebang_detect.py - Detect and modify shebangs
# Usage: python3 shebang_detect.py <directory>

import sys
import os
import re
import argparse

from MetaData import ExecutableObject, DirectoryObject
from ProgressBar import ProgressBar
from Color import *

SHEBANG_REGEX = re.compile(r"#!.*")


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
    # Options for modifying shebangs
    # 1. Add shebangs to files with missing shebangs
    # 2. Mofidy python to python3
    # 3. Modify bash to sh
    parser.add_argument(
        "-c",
        "--convert",
        help="Convert `#!/bin/bash to `#!/bin/sh and #!/usr/bin/python to #!/usr/bin/python3",
        action="store_true",
        required=False,
    )

    return parser.parse_args()


def main(args):
    directory = DirectoryObject(args.directory)
    for item in directory:
        if (
            item.is_file
            and item.is_executable
            and item.extension.strip(".") == args.file
        ):
            try:
                shebang = item.shebang
                if args.verbose:
                    cprint(item.path, fg.yellow)
                    cprint(f"{shebang}\n", fg.green)

                if args.convert:
                    if shebang == "#!/bin/bash":
                        item.shebang = "#!/bin/sh"
                    elif shebang == "#!/usr/bin/env python":
                        item.shebang = "#!/usr/bin/env python3"

                if args.missing and not SHEBANG_REGEX.match(shebang):
                    if args.file == "sh":
                        item.shebang = f"#!/bin/sh\n{shebang}"
                    elif args.file == "py":
                        item.shebang = f"#!/usr/bin/env python3\n{shebang}"

            except Exception as e:
                cprint(e, bg.red)


if __name__ == "__main__":
    args = parse_args()
    main(args)
