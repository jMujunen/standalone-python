#!/usr/bin/env python3 

# get_original_capture_date.py - Extracting EXIF data from a photo

import os
import sys
import argparse

from PIL import Image
from PIL.ExifTags import TAGS



class ExifData():
    def __init__(self, path, recursive):
        self.path = path
        self.recursive = recursive
        self.exif = self.get_datetime(self.path)

        if os.path.isdir(self.path):
            self.get_datetime_directory(self.path)
        else:
            self.get_datetime(self.path)


    def get_datetime(self, file):
        # Open Image
        self.image = Image.open(file)
        self.exifdata = self.image.getexif()
        # Iterating over all EXIF data fields
        count = 0
        for tag_id in self.exifdata:
            count += 1
            # Get the tag name, instead of human unreadable tag id
            self.tag = TAGS.get(tag_id, tag_id)
            self.data = self.exifdata.get(tag_id)
            # Decode bytes 
            if isinstance(self.data, bytes):
                self.data = self.data.decode()

            if str(self.tag).startswith('DateTime'):
                try:
                    return self.data
                except:
                    return "Error: Maybe EXIF is missing DateTimeOriginal Tag?"
            
    def get_datetime_recursive(self, dir_path):
        # Loop through all files in the directory tree
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                self.get_datetime(file_path)
            
    def get_datetime_directory(self, dir_path):
        # Loop through all files in the directory
        for file in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file)
            self.get_datetime(file_path)

    def get_date(self, original_datatime):
        return original_datatime[:10]

    def get_time(self, original_datatime):
        return original_datatime[-8:]

    def get_year(self, original_datatime):
        return original_datatime[:4]

    def get_month(self, original_datatime):
        return original_datatime[5:7]

    def get_day(self, original_datatime):
        return original_datatime[8:10]


def parse_args():
    parser = argparse.ArgumentParser(
        description='Extracting EXIF data from a photo',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('file_path', type=str, help='File path')
    parser.add_argument('--directory', '-d', action='store_true', help='Enable directory mode')
    parser.add_argument('--recursive', '-r', action='store_true', help='Enable recursive operation on a directory')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    # Parse args
    args = parse_args()
    path = args.file_path

    exif = ExifData(path, args.recursive)




'''
# Example Usage
if __name__ == '__main__':
    try:
        # Parse args
        args = parse_args()
        if args.directory:
            image_path = args.file_path
        else:
            image_path = args.file_path
    except:
        sys.exit()

    datetime = get_datetime(image_path)
    try:
        date = get_date(datetime)
        time = get_time(datetime)
    except:
        print("Error: Maybe EXIF is missing DateTimeOriginal Tag?")

try:
    print(f"Datetime: {datetime}\nDate: {date}\nTime: {time}")
    print(f"Year: {get_year(datetime)}, Month: {get_month(datetime)}, Day: {get_day(datetime)}")

except:
    print("Error: Maybe EXIF is missing DateTimeOriginal Tag?")
'''