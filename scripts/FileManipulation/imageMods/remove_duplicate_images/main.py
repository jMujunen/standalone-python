#!/usr/bin/env python3

# rm_img_dupe/main.py - A script that removes duplicate images

import os
import subprocess
import argparse

from PIL import Image
from PIL import UnidentifiedImageError
import imagehash

from pb import ProgressBar

ERRORS = []

# Parse args
def parse_args():
    parser = argparse.ArgumentParser(description='Remove duplicate images from a directory')
    parser.add_argument(
        'directory',
        type=str, 
        help='The directory to search for duplicate images'
        )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Only print the duplicate images that would be removed'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose mode'
    )
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Recursively search for duplicate images in subdirectories'
    )
    return parser.parse_args()


# Calculate the average hash of an image. The resulting hash can then be compared to the hash value of other images.
# If two images have the same hash, they are likely duplicates.
def calculate_hash(image_path):
    try:
        with Image.open(image_path) as img:
            hash_value = imagehash.average_hash(img)
            return hash_value
    except UnidentifiedImageError as e:
        ERRORS.append(image_path)
        #print(f"Error: {e}")

# Remove duplicate images based on their average hash.
def find_and_remove_duplicates(args):
    directory = args.directory
    dry_run = args.dry_run
    verbose = args.verbose

    # Create a dictionary to store the average hash values and the corresponding file paths    
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
        if dry_run:
            print(f"\033[1;32mDry-Run: Removing {duplicate_pair[0]}\033[0m")
        else:
            print(f"\033[1;31mRemoving {duplicate_pair[0]}\033[0m")
            #os.remove(duplicate_pair[0])
def recursive_find_and_remove_duplicates(args):
    directory = args.directory
    dry_run = args.dry_run
    verbose = args.verbose

    # Create a dictionary to store the average hash values and the corresponding file paths    
    image_hashes = {}
    duplicates = []

    print('Finding files...')

    files = subprocess.run(
        f'find {args.directory} -name "*.jpg" -or -name "*.png" -or -name "*.jpeg" -or -name "*.JPG" -or -name "*.PNG" -or -name "*.JPEG"',
        shell=True,
        capture_output=True,
        text=True
    ).stdout.strip()

    # Initialize the first progress bar
    number_of_files = len(files.split('\n'))
    print(f'Found {number_of_files} files')
    pb = ProgressBar(number_of_files)

    # Iterate through the files and calculate the average hash for each image
    for file in files.split('\n'):
        hash_value = calculate_hash(file)
        file_size = os.stat(file).st_size
        if hash_value in image_hashes:
            if file_size != os.stat(image_hashes[hash_value]).st_size:
                print(f"\033[1;33mWarning: {file} and {image_hashes[hash_value]} have different sizes ({file_size} and {os.stat(image_hashes[hash_value]).st_size})\033[0m")
            duplicates.append((file, image_hashes[hash_value]))
        else:
            image_hashes[hash_value] = file

        pb.increment()

    # Provide an update. Useful for long running operations
    number_of_duplicates = len(duplicates)

    # Initialize the second progress bar for manual removal
    #pb = ProgressBar(number_of_duplicates)
    #print(f'Found {number_of_duplicates} duplicates')

    # Display duplicates
    for duplicate_pair in duplicates:
        '''
        # Display img in terminal
        try:
            subprocess.run(
                f'kitty +kitten icat "{duplicate_pair[0]}"',
                shell=True
            )
        except Exception as e:
            print(e)
        try:
            subprocess.run(
                f'kitty +kitten icat "{duplicate_pair[1]}"',
                shell=True
            )
        print(f'{duplicate_pair[0]} \n {duplicate_pair[1]}')
        pb.increment()
        except Exception as e:
            print(e)
        
        # This option is for manual removal of each file. Recommanded for important files
        while True:
            wait = input('Enter to continue or Delete (1/2): ')
            try:
                if wait == '1':
                    os.remove(duplicate_pair[0])
                    print(f'\033[1;32mRemoved {duplicate_pair[0]}\033[0m')
                    break
                elif wait == '2':
                    os.remove(duplicate_pair[1])
                    print(f'\033[1;31mRemoved {duplicate_pair[1]}\033[0m')
                    break
                elif wait == '':
                    break
                else:
                    print('Invalid input')
            except Exception as e:
                print(e)
                break
        os.system('clear')
        '''

        file_size1, filesize2 = os.stat(duplicate_pair[0]).st_size, os.stat(duplicate_pair[1]).st_size

        if file_size1 == filesize2:
            if dry_run:
                print(f"\033[1;32mDry-Run: Removing {duplicate_pair[0]}\033[0m", end='\r')
            else:
                print(f"\033[1;31mRemoving {duplicate_pair[0]}\033[0m", end='\r')
                #os.remove(duplicate_pair[0])
        else:
            smaller_file = duplicate_pair[0] if file_size1 < filesize2 else duplicate_pair[1]
            if dry_run:
                print(f"\033[1;32mDry-Run: Removing {smaller_file}. File size difference: {file_size1 - filesize2}\033[0m", end='\r')
            else:
                print(f"\033[1;31mRemoving {smaller_file}. File size difference: {file_size1 - filesize2}\033[0m", end='\r')
                #os.remove(smaller_file)

        with open ('duplicates.txt', 'a') as f:
            f.write(f'{duplicate_pair}\n')
    print(f'Duplicates found: {number_of_duplicates}')
    
    if ERRORS:
        with open('errors.txt', 'w') as f:
            f.write('\n'.join(ERRORS))
        print(f'Found {len(ERRORS)} errors. See {os.getcwd()}/errors.txt')



# Example usage
if __name__ == "__main__":
    args = parse_args()
    if args.recursive:
        recursive_find_and_remove_duplicates(args)
    else:
        find_and_remove_duplicates(args)