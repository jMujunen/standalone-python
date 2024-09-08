#!/usr/bin/env python3

# rng.py - Random number generator

import random
import sys


def main() -> None:
    if len(sys.argv) == 1:
        print(random.randint(0, 1000))

    elif len(sys.argv) == 2:
        print(random.randint(int(sys.argv[1])))

    """
    TODO:
    * Add option for character
    elif len(sys.argv) == 3:
        for arg in sys.argv[1:]:
            if arg in ["-a", "--alpha", "alpha", "letters", "a"]:
                print(chr(random.randint(ord('a'), ord('z'))))
    """


if __name__ == "__main__":
    main()
