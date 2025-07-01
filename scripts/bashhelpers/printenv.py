#!/usr/bin/env python3

import os
from Color import fg, style

if __name__ == "__main__":
    for var, val in os.environ.items():
        print(f"{fg.red}{var:<40}{style.reset}{fg.orange}{val}{style.reset}")
