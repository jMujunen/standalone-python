#!/usr/bin/env python3

# find_duplicate_files.py - Find duplicate files in two directories

import os
import argparse
import glob
import sys

from pb import ProgressBar

def parse_arguments():
    parser = argparse.ArgumentParser(description="Find duplicate files in two directories")
    parser.add_argument("dir1", help="Path to the first directory")
    parser.add_argument("dir2", help="Path to the second directory")
    parser.add_argument("output", help="Path to the output file")
    # Add option for recursive mode
    parser.add_argument("-r", "--recursive", action="store_true", help="Enable recursive mode")
    return parser.parse_args()

class Files():
    def __init__(self, dir1, dir2, output, recursive):
        self.dir1 = dir1
        self.dir2 = dir2
        self.output = output
        self.recursive = recursive
        self.progress = ProgressBar()
        self.common_files = self.get_common_files()

    # Function to iterate files in a directory and return a list of file names
    def get_files_in_directory(self, directory):
        """
        Get the list of files in the specified directory.
        Args:
        directory (str): The directory path.
        Returns:
        list: List of files in the directory.
        """
        try:
            self.files = []
            self.files_verbose = []

            if self.recursive:
                for root, _, filenames in os.walk(directory):
                    for filename in filenames:
                        self.progress.increment(0.0001)
                        if os.path.isfile(os.path.join(root, filename)):
                            # Standard output
                            self.files.append(str(filename).replace('_output', ''))
                            # Verbose output
                            self.files_verbose.append(os.path.join(root, filename))
                return self.files, self.files_verbose

            else:
                self.files_in_directory = glob.glob(os.path.join(directory, '*'))
                for file in self.files_in_directory:
                    self.progress.increment(0.0001)
                    if os.path.isfile(file):
                        self.files.append(str(os.path.basename(file)).replace('_output', ''))
                return self.files, self.files_verbose
        except Exception as e:
            """
            Handle the exception when the directory is not found.
            """
            print(f"Error: {e}")
            return 2

    # Function to compare two directories and return a list of common files
    def get_common_files(self):
        """
        Retrieve the common files present in two directories.

        Returns:
        list: A list of common files found in the two directories.
        """

        try:
            self.common_files = []
            if self.recursive:
                # Get files in the first directory
                self.files1, self.files1_verbose = self.get_files_in_directory(directory1)
                self.progress.set_value(30)
                # Get files in the second directory
                self.files2, self.files2_verbose = self.get_files_in_directory(directory2)
                self.progress.set_value(60)
                # Find common files
                for file1 in self.files1:
                    self.progress.increment(0.0001)
                    if file1 in self.files2:
                        self.common_files.append(os.path.basename(file1))
                return self.common_files

            else:
                # Get files in the first directory
                self.files1 = self.get_files_in_directory(directory1)
                # Get files in the second directory
                self.files2 = self.get_files_in_directory(directory2)
                # Find common files
                for file1 in self.files1:
                    self.progress.increment(0.001)
                    if file1 in self.files2:   
                        self.common_files.append(os.path.basename(file1))       
                return self.common_files

        except Exception as e:
            print(f"Error: {e}")
            return 1

    # Function to print a list to a file
    def write_data_to_file(self, filepath):
        """
        Writes data to the specified file.

        Parameters:
            self (object): The object itself.
            filepath (str): The file path to write the data to.

        Returns:
            int: 1 if no common files are found, 0 if data is successfully written, or 2 if an exception occurs.
        """
        # Set the progress value to 90
        self.progress.set_value(90)
        try:
            # Check if there are common files
            if len(self.common_files) == 0:
                print("No common files found")
                return 1
            else:
                # Open the file and write data to it
                with open(filepath, 'w') as f:
                    for item in self.common_files:
                        # Increment the progress
                        self.progress.increment(0.0001)
                        f.write(f"{item}\n")
                # Set the progress value to 100
                self.progress.set_value(100)
                return 0
        except:
            # Handle any error writing to the file
            print('Error writing to file')
            return 2

    def verbose_output_to_markdown_table(self, markdown_filepath):
        # Ensure file is saved with correct file extension
        if not markdown_filepath.endswith('.md'):
            markdown_filepath = markdown_filepath + '.md'

        # Set the progress value to 95
        self.progress.set_value(95)
        # Check if there are common files
        if len(self.common_files) == 0:
            print("No common files found")
            return 1
        else:
            # Open the file and write data to it
            with open(markdown_filepath, 'w') as f:
                # Write the header
                f.write("# Common Files\n\n")
                f.write("| File1 | File2 |\n")
                for file in self.common_files:
                    # Increment the progress
                    self.progress.increment(0.0001)
                    # Find entire filepath for 'file' in 'self.files1_verbose' and 'self.files2_verbose'
                    file1_index = self.files1_verbose.index(file)
                    file2_index = self.files2_verbose.index(file)
                    # Write to file
                    f.write(f"| {file1_index} | {file2_index} |\n")
                    file1_index = self.files1_verbose.index(file)
            # Set the progress value to 100
            self.progress.set_value(100)
            return 0

# Example usage
if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    directory1 = args.dir1
    directory2 = args.dir2
    output = args.output
    recursive = args.recursive
    # Find common files
    CommonFiles = Files(directory1, directory2, output, recursive)
    CommonFiles.verbose_output_to_markdown_table('common_files.md')


    # Check the return code and print a helpful message
    if runtime_code == 0:
        print("Data written to file successfully")
    else:
        print(f'Error {runtime_code} : Could not write data to file')