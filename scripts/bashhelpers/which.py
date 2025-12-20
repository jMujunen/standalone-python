#!/usr/bin/env python3

import subprocess
import sys


def main(cmd: str) -> int:
    result = subprocess.getoutput(
        f'zsh -c "source /home/joona/.dotfiles/.bash_aliases; which {command}"'
    )
    print(result.replace("\\n", "\n").replace("\\t", "\n\t"))
    return 0


if __name__ == "__main__":
    command = " ".join(sys.argv[1:])
    sys.exit(main(command))
