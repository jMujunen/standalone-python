#!/usr/bin/env python3
"""This script takes an image as input, calculates the hash,
and compares it to the hashes of all images in a directory.
Finally, it prints out the names of any images that have a similar hash."""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import imagehash
from Color import cprint, fg
from fsutils.compiled._DirNode import Dir, Img
from ProgressBar import ProgressBar


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("IMG", help="Image to compare")
    parser.add_argument("DIR", help="Directory to compare against")
    return parser.parse_args()


def process_img(img: Img) -> tuple[imagehash.ImageHash | None, str, str]:
    if img.suffix in (".nef", ".heic"):
        return (None, "", "")
    resized = img.resize()
    return (resized.calculate_hash(), img.path, resized.encode())


def main(reference_img: Img, output: Dir) -> list[tuple[imagehash.ImageHash | None, str, str]]:
    """Compare an image with all images in a directory and print out similar images."""
    ref = reference_img.calculate_hash()
    similar_images = []

    with ProgressBar(len(output)) as pb, ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_img, img) for img in output.images}
        for future in as_completed(futures):
            try:
                result = future.result()
                pb.increment()
                if result and result[0] == ref:
                    similar_images.append(result)
            except Exception as e:
                print(f"\n{e}")
    return similar_images


if __name__ == "__main__":
    args = parse_args()
    similar_images = main(Img(args.IMG), Dir(args.DIR))
    cprint("\n=========================\n", fg.deeppink)
    for img in similar_images:
        ahash, path, base = img
        print(f"{path:<100}{path:<40}")
