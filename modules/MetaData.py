#!/usr/bin/env python3

# MetaData.py - This module contains reusable file objects. Most of the mutable state is metadata

import os, sys, re, subprocess

from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS
from moviepy.editor import VideoFileClip

import imagehash

class FileObject:
    def __init__(self, path):
        self.path = path
        self.content = None
        self.metadata = None

    @property
    def size(self):
        return int(os.path.getsize(self.path))
    @property
    def file_name(self):
        return str(os.path.basename(self.path))
    @property
    def extension(self):
        return str(os.path.splitext(self.path)[-1])
    def read(self):
        with open(self.path, 'rb') as f:
            self.content = f.read()
        return self.content
    def is_file(self):
        return os.path.isfile(self.path)
    def is_dir(self):
        return os.path.isdir(self.path)
    def __eq__(self, other):
        if not isinstance(other, FileObject):
            return False
        if self.content is None:
            self.contnet = self.read()
        return self.content == other.content
    def __setattr__(self, name, value):
        try:
            self.__dict__[name] = value
            return self.__dict__[name]
        except AttributeError:
            raise AttributeError(f"{self.__class__.__name__} object has no attribute {name}")
    def __str__(self):
        return str(self.__dict__)

class DirectoryObject(FileObject):
    def __init__(self, path):
        self.path = path
        super().__init__(self.path)
    def __len__(self):
        return len(os.listdir(self.path))
    def __iter__(self):
        for item in os.listdir(self.path):
            if os.path.isdir(os.path.join(self.path, item)):
                yield DirectoryObject(os.path.join(self.path, item))
            else:
                yield FileObject(os.path.join(self.path, item))
    def __str__(self):
        return f"Directory: {self.path}\nFiles: {len(self)}\n"
    def __eq__(self, other):
        if not isinstance(other, DirectoryObject):
            return False
        return self.path == other.path


class ImageObject(FileObject):
    def __init__(self , path):
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
    
    def __str__(self):
        return f"""Image: {self.path}
            Dimensions: {self.dimensions}
            Hash: {self.hash}
            EXIF: {self.exif}
            Capture Date: {self.capture_date}"""


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

    def __str__(self):
        return f"VideoObject(path={self.path}, metadata={self.metadata}, bitrate={self.bitrate})"
