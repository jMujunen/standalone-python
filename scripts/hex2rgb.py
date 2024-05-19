#!/usr/bin/env python3

import sys
def hex_to_rgb(hex):
  return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

# Example
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(hex_to_rgb(sys.argv[1]))
        sys.exit(0)
    else:
        print("Usage: python hex2rgb.py <hex code>")
        sys.exit(1)
