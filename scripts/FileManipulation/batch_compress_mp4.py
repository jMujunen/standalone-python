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
    if os.path.isfile(file_path):cls
        os.remove(file_path)
    else:
        print(f'[\033[38;5;200m Error: {file_path} is a directory \033[0m]')
'''

def write_to_file(file_path, content):
    with open(file_path, 'w') as file:
        for line in content:
            file.write(line + '\n')

def main(input_directory, output_directory):
    """
    Compresses all .mp4 files in the input directory and saves the compressed files in the output directory.
    
    Args:
        input_directory (str): The directory containing the .mp4 files to be compressed.
        output_directory (str): The directory where the compressed .mp4 files will be saved.
    
    Returns:
        list: A list of the names of the successfully compressed .mp4 files.
    
    Raises:
        SystemExit: If the output file already exists and is not a file.
    
    Prints:
        str: The progress of the compression process.
        str: Information about the current file being compressed.
        str: Information about the successful conversion of a file.
        str: Information about the failed conversion of a file.
        str: A message indicating the completion of the batch conversion.
    """
    successfully_compressed = []

    # Replace whitespace in the output directory path with underscores
    output_directory = output_directory.replace(' ', '_')

    try:
        # Create the output directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)
    except OSError as e:
        print(f"[\033[31m Error creating output directory '{output_directory}': {e} \033[0m]")
        return

    # Get total files
    files = os.listdir(input_directory)
    number_of_files = len(files)

    print(f"\033[34mTotal number of .mp4 files to process:\033[0m \033[2;36m{number_of_files}\033[m") # DEBUGGING
    
    # Iterate over all .mp4 files in the input directory
    for i, input_file in enumerate(os.listdir(input_directory)):
        print(f"[\033[33m Processing {input_file} ({i + 1}/{number_of_files}) \033[0m]")
        if input_file.endswith(".mp4"):

            # Extract the file name without extension 
            # (some_video_file_name.getsome.arhagag.mp4) -> (some_video_file_name)
            file_name = os.path.splitext(input_file)[0]

            try:
                # Define the output file path
                output_file = os.path.join(output_directory, f"{file_name}.mp4")
            except Exception as e:
                print(f"[\033[31m {e} \033[0m")
                continue
            
            # Run ffmpeg command for each file
            result = subprocess.run(
                 f'ffmpeg -i \'{os.path.join(input_directory, input_file)}\' \
                    -c:v h264_nvenc -rc constqp -qp 28 \'{output_file}\' -n',
                    shell=True, 
                    capture_output=True, 
                    text=True)
            result = result.returncode
            # Check if conversion was successful
            if result == 0:
                print(f"[\033[32m Successfully converted {input_file} \033[0m]")
                successfully_compressed.append(input_file)
            else:
                print(f"[\033[31m {input_file} could not be converted. Error code: {result}:{result} \033[0m]")
    print("[\033[1;32m Batch conversion completed. \033[0m]")
    return successfully_compressed

if __name__ == "__main__":
    args = parse_arguments()
    files_to_remove = main(args.input_directory, args.output_directory)
    write_to_file(args.successfully_compressed, files_to_remove)

