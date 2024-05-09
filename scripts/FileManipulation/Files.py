#!/usr/bin/env python3

# find_duplicate_files.py - Find duplicate files in two directories

import os
import argparse
import glob
import sys

from ProgressBar import ProgressBar

def parse_arguments():
    parser = argparse.ArgumentParser(description="Find duplicate files in two directories",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("dir1", help="Path to the first directory")
    parser.add_argument("dir2", help="Path to the second directory")
    parser.add_argument("-o", "--output", help="Path to the output file", default="common_files.md")
    # Add option for recursive mode
    #parser.add_argument("-r", "--recursive", action="store_true", help="Enable recursive mode")
    return parser.parse_args()

class CompareFiles():
    def __init__(self, dir1, dir2):
        self.dir1 = dir1
        self.dir2 = dir2
        self.progress = ProgressBar()
        self.common_files = self.get_common_files(dir1, dir2)

    # Function to compare two directories and return a list of common files
    def get_common_files(self, directory1, directory2):
        """
        Retrieve the common files present in two directories.

        Returns:
            list: A list of common files found in the two directories.
        """
        self.common_files = []
        print("Iterating through directories...")
        try:
            paths1 = [os.path.join(root, file) for root, _, files in os.walk(directory1) for file in files]
            filenames1 = [os.path.basename(file) for file in paths1]

            paths2 = [os.path.join(root, file) for root, _, files in os.walk(directory2) for file in files]
            filenames2 = [os.path.basename(file) for file in paths2]

            jobs = len(paths1)

            print(f"\nFound {jobs} files")

            print('\n'.join(paths1))
            print('\n'.join(paths2))

            print("Comparing files...")
            pb = ProgressBar(jobs)
            
            for path in paths1:
                pb.increment()
                # Check for null/corrupt files
                if os.path.getsize(path) == 0:
                        continue
                filename = os.path.basename(path)
                try:
                    if filename in filenames2:
                        file1_size = os.path.getsize(path)
                        file2_size = os.path.getsize(os.path.join(directory2, filename))
                        self.common_files.append(filename)

                except Exception as e:
                    # Continue if exception while reading file (e.g. permission denied, corrupt file, etc.)
                    print(f"Error: {e}")
                    continue
        except Exception as e:
            print(f"Error: {e}")
            return 1

        return self.common_files

    # Function to print a list to a file
    def write_data_to_file(self, output):
        """ Writes data to the specified file. """
        try:
            # Check if there are common files
            if len(self.common_files) == 0:
                print("No common files found")
                return 1
            else:
                # Open the file and write data to it
                with open(output, 'w') as f:
                    f.write('\n'.join(self.common_files))
                return 0
        except Exception as e:
            # Handle any error writing to the file
            print('Error: ', e)

    def __str__(self):
        return '\n'.join(self.common_files)

# Example usage
if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    directory1 = args.dir1
    directory2 = args.dir2
    output_file = args.output
    
    # Find common files
    common_files = CompareFiles(directory1, directory2)
    print(common_files)
    common_files.write_data_to_file(output_file)
