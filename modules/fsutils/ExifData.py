#!/usr/bin/env python3
"""get_original_capture_date.py - Extracting EXIF data from a photo."""
import argparse
from PIL import Image
from PIL.ExifTags import TAGS

class ExifData:
    """Class to extract EXIF metadata."""
    def __init__(self, path):
        self.path = path

    @property
    def exif(self):
        """Open image and return all EXIF data."""
        with Image.open(self.path) as img:
            data = img.getexif()
        return data

    @property
    def capture_date(self):
        """Iterate over all EXIF data fields and return the DateTime field if it exists."""
        for tag_id in self.exif:
            # Get the tag name, instead of human unreadable tag id
            tag = TAGS.get(tag_id, tag_id)
            data = self.exif.get(tag_id)
            # Decode bytes
            if isinstance(data, bytes):
                data = data.decode()
            if str(tag).startswith("DateTime"):
                return data

    def __str__(self):
        """Format the capture date in a human readable format."""
        if not self.capture_date:
            raise ValueError('Could not determine capture date')
        date = self.capture_date[:10].replace(":", "-")
        time = self.capture_date[-8:]
        return f"{date} {time}"

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Extracting EXIF data from a photo",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("file_path", type=str, help="File path")
    parser.add_argument("--directory", "-d", action="store_true", help="Enable directory mode")
    return parser.parse_args()

# Example usage
if __name__ == "__main__":
    # Parse args
    args = parse_args()
    exif = ExifData(args.file_path)
    print("\n")
    print("datetime: ", format(exif, "datetime"))
    print("year: ", format(exif, "year"))
    print("month: ", format(exif, "month"))
    print("day: ", format(exif, "day"))
    print("\n")
    print("full date time: ", exif)