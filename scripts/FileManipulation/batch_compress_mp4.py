#!/usr/bin/env python3

# bp_mp4_cs.py - Batch process all .mp4 files in a directory

import os
import subprocess
import argparse
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(description="Batch process all .mp4 files in a directory")
    parser.add_argument("input_directory", help="Input directory")
    parser.add_argument("output_directory", help="Output directory")
    parser.add_argument("successfully_compressed", help="File path to save list of successfully compressed files")
    return parser.parse_args()

'''
# Function to remove file after compression completes successfully
def remove_file(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)
    else:
        print(f'[\033[38;5;200m Error: {file_path} is a directory \033[0m]')
'''

def write_to_file(file_path, content):
    with open(file_path, 'w') as file:
        for line in content:
            file.write(line + '\n')

def main(input_directory, output_directory):
    successfully_compressed = []

    # Replace whitespace in the output directory path with underscores
    output_directory = output_directory.replace(' ', '_')
    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Get total files
    files = os.listdir(input_directory)
    number_of_files = len(files)

    # Iterate over all .mp4 files in the input directory
    for i, input_file in enumerate(os.listdir(input_directory)):
        print(f"[\033[38;5;200m Processing {i + 1} out of {number_of_files} \033[0m]")
        if input_file.endswith(".mp4"):
            # Print information about the current file to the user
            print(f"Processing file: {input_file}")

            # Extract the file name without extension
            file_name = os.path.splitext(input_file)[0]

            try:
                # Define the output file path
                output_file = os.path.join(output_directory, f"{file_name}.mp4")
            except Exception as e:
                print(f"[\033[31m {e} \033[0m")
                output_file = os.path.join(output_directory, f"{file_name}1.mp4")
                if os.path.isfile(output_file):
                    sys.exit(666)
            # Run ffmpeg command for each file
            result = subprocess.run(
                ["ffmpeg", "-i", os.path.join(input_directory, input_file), 
                "-c:v", "h264_nvenc", "-rc", "constqp", "-qp", "28", output_file], 
                shell=True, 
                capture_output=True, 
                text=True)
            
            # Check if conversion was successful
            if result.returncode == 0:
                print(f"[\033[38;5;200m File {input_file} successfully converted to {output_file} \033[0m]")
                successfully_compressed.append(input_file)
            else:
                print(f"[\033[38;5;200m File {input_file} could not be converted. Error code: {result.returncode}:{result.stderr} \033[0m]")
    print("[\033[38;5;200m Batch conversion completed. \033[0m]")
    return successfully_compressed

if __name__ == "__main__":
    args = parse_arguments()
    files_to_remove = main(args.input_directory, args.output_directory)
    write_to_file(args.successfully_compressed, files_to_remove)
