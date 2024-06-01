#!/usr/bin/env python3

# clipboard_striplines.py - strips a character from each line,
# using the clipboard as I/O source

import re
import sys
import pyperclip
import argparse

PRESETS = {
    "multiline": lambda x: " ".join(i.strip() for i in x.split("\n")),
    "whitespace": None,
    # TODO - add presets for common patterns
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Strips a character or string from each line, using the clipboard as I/O",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
        python3 clipboard_striplines.py --preset=multiline

            alsa-card-profiles      |
            ca-certificates-mozilla |
            dict                   |-> alsa-card-profiles ca-certificates-mozilla dict filesystem geoclue
            filesystem              |
            geoclue                 |
            

        python3 clipboard_striplines.py --pattern=wlan0 --replace=wlan1

        wlan0: authenticate        ->  wlan1: authenticate
        wlan0: send auth to        ->  wlan1: send auth to
        wlan0: authenticated       ->  wlan1: authenticated
        wlan0: associate with      ->  wlan1: associate with
        wlan0: RX AssocResp from   ->  wlan1: RX AssocResp from
        wlan0: associated          ->  wlan1: associated
""",
    )
    parser.add_argument(
        "-r",
        "--replace",
        help="Replace character with this instead of stripping.",
        default="",
    )
    parser.add_argument(
        "--pattern",
        help="PCRE - Perl compatiable regex patterns to search for",
        default=" ",
    )

    parser.add_argument(
        "--lstrip", help="Only strip from the left", action="store_true"
    )

    parser.add_argument(
        "--rstrip", help="Only strip from the right", action="store_true"
    )
    parser.add_argument("-l", "--list", help="List presets", action="store_true")
    parser.add_argument(
        "-p",
        "--preset",
        choices=["multiline", "ipy"],
        required=False,
        help="""Presets for common patterns:
        Multiline: Turn a multiline string into a single line""",
        default=["multiline"]
        # Example:
        # -----------------
        #  pyside6-tools-wrappers
        #  python-aiosql
        #  python-clipboard
        #  python-imagehash
        #  python-imageio   --> pyside6-tools-wrappers python-aiosql python-clipboard python-imagehash python-imageio
        # TODO: Add presets for other common patterns
    )

    return parser.parse_args()


def main(char, replacement):
    try:
        pattern = re.compile(char)
        text = pyperclip.paste()
        lines = text.split("\n")
        output = []
        for line in lines:
            output.append(re.sub(pattern, replacement, line))
        text = "\n".join(output)
        pyperclip.copy(text)
        print(text)
        return 0
    except Exception as e:
        print(e)
        return 1


# Example usage:
if __name__ == "__main__":
    args = parse_args()
    main(args.pattern, args.replace)

#     # With preset
#     input = """alsa-card-profiles
# ca-certificates-mozilla
# dict
# filesystem
# geoclue
# ghc-libs
# gssproxy
# gst-plugin-pipewire
# haskell-aeson-pretty
# haskell-bitvec
# haskell-bsb-http-chunked
# haskell-comonad
# haskell-fast-logger
# haskell-haddock-library
# haskell-hslua-repl
# haskell-http-types
# haskell-indexed-traversable
# haskell-ipynb
# haskell-pandoc-types
# haskell-regex-tdfa
# haskell-semigroupoids
# haskell-servant
# haskell-time-manager
# haskell-toml-parser
# haskell-unordered-containers
# haskell-vault
# haskell-wai
# intel-ucode
# lib32-nss
# libpipewire
# libutempter
# nmap
# nss
# ollama-cuda
# pacman-contrib
# pipewire-jack
# warning: python-pdfrw: mtree data not available (Success)
# warning: python-pybtex: mtree data not available (Success)
# warning: python-pynvim: mtree data not available (Success)
# shadow
# systemd
# vlc"""
#     print(PRESETS["multiline"](input))
