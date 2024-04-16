#!/usr/bin/env python3

# rm_img_dupe/main.py - A script that removes duplicate images

import os
import argparse

from PIL import Image
from PIL import UnidentifiedImageError
import imagehash

from pb import ProgressBar

# Parse args
def parse_args():
    parser = argparse.ArgumentParser(description='Remove duplicate images from a directory')
    parser.add_argument('directory', type=str, help='The directory to search for duplicate images')
    return parser.parse_args()


# Calculate the average hash of an image. The resulting hash can then be compared to the hash value of other images.
# If two images have the same hash, they are likely duplicates.
def calculate_hash(image_path):
    try:
        with Image.open(image_path) as img:
            hash_value = imagehash.average_hash(img)
            return hash_value
    except UnidentifiedImageError as e:
        print(f"Error: {e}")

# Remove duplicate images based on their average hash.
def find_and_remove_duplicates(directory):
    image_hashes = {}
    duplicates = []

    # Initialize the progress bar
    files = [item for item in os.listdir(directory) if item.endswith(('.JPG', '.jpeg', '.png', '.PNG', '.jpg', '.JPEG'))]
    number_of_files= len(files)
    pb = ProgressBar(number_of_files)

    # Iterate through the files and calculate the average hash for each image
    for filename in files:
        file_path = os.path.join(directory, filename)
        hash_value = calculate_hash(file_path)

        if hash_value in image_hashes:
            duplicates.append((file_path, image_hashes[hash_value]))
        else:
            image_hashes[hash_value] = file_path

        pb.increment()

    for duplicate_pair in duplicates:
        print(f"Removing duplicate: {duplicate_pair[0]}")
        os.remove(duplicate_pair[0])

# Example usage
if __name__ == "__main__":
    directory = parse_args().directory
    find_and_remove_duplicates(directory)