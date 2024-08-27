#!/usr/bin/env python3
import sys


def hex_to_dec(hex_code):
    return int(hex_code, 16)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: hex2dec.py HEX_CODE")
        sys.exit(1)
    hex_code = sys.argv[1]
    dec_value = hex_to_dec(hex_code)
    print(dec_value)
