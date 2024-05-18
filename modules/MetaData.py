#!/usr/bin/env python3

# MetaData.py - This module contains reusable file objects. Most of the mutable state is metadata

import os
import sys
import re
import subprocess

from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS
from moviepy.editor import VideoFileClip
import cv2

import imagehash


class FileObject:
    def __init__(self, path):
        self.path = path

    @property
    def size(self):
        return int(os.path.getsize(self.path))

    @property
    def file_name(self):
        return str(os.path.splitext(self.path)[0])

    @property
    def basename(self):
        return str(os.path.basename(self.path))

    @property
    def extension(self):
        return str(os.path.splitext(self.path)[-1]).lower()

    def read(self):
        with open(self.path, 'rb') as f:
            self.content = f.read()
        return self.content

    @property
    def is_file(self):
        return os.path.isfile(self.path)

    @property
    def is_dir(self):
        return os.path.isdir(self.path)

    @property
    def is_video(self):
        return self.extension.lower() in ['.mp4', '.avi', '.mkv', '.wmv', '.webm', '.mov']

    @property
    def is_image(self):
        return self.extension.lower() in ['.jpg', '.jpeg', '.png', '.nef']
        # return FileObject(os.path.join(self.path, matching_files))

    def __eq__(self, other):
        if not isinstance(other, FileObject):
            return False
        elif isinstance(other, VideoObject):
            return self.size == other.size
        elif self.content is None:
            self.contnet = self.read()
        return self.content == other.content

    def __setattr__(self, name, value):
        try:
            self.__dict__[name] = value
            return self.__dict__[name]
        except AttributeError:
            raise AttributeError(
                f"{self.__class__.__name__} object has no attribute {name}")

    def __str__(self):
        return str(self.__dict__)


class DirectoryObject(FileObject):
    def __init__(self, path):
        self.path = path
        super().__init__(self.path)

    @property
    def files(self):
        return [file for folder in os.walk(self.path) for file in folder[2]]

    @property
    def directories(self):
        return [file for folder in os.walk(self.path) for file in folder[1]]

    def file_info(self, file_name):
        if file_name not in self.files:
            return
        if len(self.directories) == 0:
            for f in os.listdir(self.path):
                if f == file_name:
                    return FileObject(os.path.join(self.path, f))
        for d in self.directories:
            try:
                if file_name in os.listdir(os.path.join(self.path, d)):
                    file = FileObject(os.path.join(self.path, d, file_name))
                    if file.is_image:
                        return ImageObject(os.path.join(self.path, d, file_name))
                    elif file.is_video:
                        return VideoObject(os.path.join(self.path, d, file_name))
                    else:
                        return FileObject(os.path.join(self.path, d, file_name))
            except FileNotFoundError:
                pass

    def __contains__(self, item):
        return item in self.files

    def __len__(self):
        return len(self.directories) + len(self.files)

    def __iter__(self):
        for root, _, file in os.walk(self.path):
            yield DirectoryObject(root)
            for filename in file:
                if os.path.isfile(os.path.join(root, filename)):
                    if os.path.splitext(filename)[1].lower() in ['.mp4', '.avi', '.mkv', '.wmv', '.webm', '.mov']:
                        yield VideoObject(os.path.join(root, filename))
                    elif os.path.splitext(filename)[1].lower() in ['.jpg', '.jpeg', '.png', '.nef']:
                        yield ImageObject(os.path.join(root, filename))
                    else:
                        yield FileObject(os.path.join(root, filename))
                else:
                    yield DirectoryObject(os.path.join(root, filename))

    def __str__(self):
        return f"Directory: {self.path}\nFiles: {len(self)}\n"

    def __eq__(self, other):
        if not isinstance(other, DirectoryObject):
            return False
        return self.path == other.path


class ImageObject(FileObject):
    def __init__(self, path):
        super().__init__(path)

    def calculate_hash(self):
        try:
            with Image.open(self.path) as img:
                hash_value = imagehash.average_hash(img)
            return hash_value
        except UnidentifiedImageError as e:
            ERRORS.append(self.path)
            print(f"Error: {e}")
            return None

    @property
    def dimensions(self):
        """
        Calculate the dimensions of the image located at the specified path.
        Returns:
            Tuple[int, int]: width x height of the image in pixels.
        """
        with Image.open(self.path) as img:
            width, height = img.size
        return width, height

    @property
    def exif(self):
        # Open Image
        with Image.open(self.path) as img:
            data = img.getexif()
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

    @property
    def is_corrupt(self):
        try:
            img = Image.open(self.path)
            img.verify()
            return False  # Image is not corrupt
        except (IOError, SyntaxError):
            return True  # Image is corrupt
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")

    # def __str__(self):
    #     return f"""Image: {self.path}
    #         Dimensions: {self.dimensions}
    #         Hash: {self.hash}
    #         EXIF: {self.exif}
    #         Capture Date: {self.capture_date}"""


class VideoObject(FileObject):
    def __init__(self, path):
        super().__init__(path)

    @property
    def metadata(self):
        with VideoFileClip(self.path) as clip:
            metadata = {
                "duration": clip.duration,
                "dimensions": (clip.size[0], clip.size[1]),
                "fps": clip.fps,
                "aspect_ratio": clip.aspect_ratio
            }
        return metadata

    @property
    def bitrate(self):
        ffprobe_cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            self.path
        ]
        ffprobe_output = subprocess.check_output(ffprobe_cmd).decode('utf-8')
        metadata = json.loads(ffprobe_output)
        capture_date = metadata['format']['tags'].get('creation_time')
        bit_rate = metadata['format']['bit_rate']
        return bit_rate

    @property
    def is_corrupt(self):
        try:
            cap = cv2.VideoCapture(self.path)
            if not cap.isOpened():
                return True  # Video is corrupt
            else:
                return False  # Video is not corrupt
        except (IOError, SyntaxError):
            return True  # Video is corrupt
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")


# Example
if __name__ == "__main__":
    img = ImageObject("/home/joona/Pictures/PEGBOARD.jpg")
    video = VideoObject("/mnt/ssd/compressed_obs/Dayz/blaze kill CQC.mp4")
    txtfile = FileObject(
        "/home/joona/python/Projects/dir_oraganizer/getinfo.py")

    print(img)
    print(video)
    print(txtfile)


f = len([f for folder in os.walk('/mnt/ssd/compressed_obs/CSGO/')
        for f in folder])
