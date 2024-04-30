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

    @property
    def exif(self):
        # Open Image
        with Image.open(self.path) as image:
            data = image.getexif()
        return data
    @property
    def capture_date(self):
        # Iterating over all EXIF data fields
        for tag_id in self.exif:
            # Get the tag name, instead of human unreadable tag id
            tag = TAGS.get(tag_id, tag_id)
            data = self.exif.get(tag_id)
            # Decode bytes 
            if isinstance(data, bytes):
                data = data.decode()
            if str(tag).startswith('DateTime'):
                return data
        return None
            
    def __format__(self, format_spec):
        formats = {
            'date': self.capture_date[:10],
            'time': self.capture_date[-8:],
            'year': self.capture_date[:4],
            'month': self.capture_date[5:7],
            'day': self.capture_date[8:10],
            'datetime': self.capture_date
        }

        if format_spec in formats:
            return formats[format_spec]
        else:
            return self.exif

    def __str__(self):
        date = self.capture_date[:10].replace(':', '-')
        time = self.capture_date[-8:]
        return f'{date} {time}'

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
    print('\n')
    print(format(exif, 'datetime'))
    print(format(exif, 'year'))
    print(format(exif, 'month'))
    print(format(exif, 'day'))
    print('\n')
    print(exif)


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

    datetime = exif(image_path)
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