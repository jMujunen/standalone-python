#!/usr/bin/env python3

# MetaData.py - This module contains reusable file objects. Most of the mutable state is metadata

import os
import sys
import re
import json
import subprocess
import datetime
import pandas as pd

from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS
from moviepy.editor import VideoFileClip
import cv2

from Color import *
import imagehash

GIT_OBJECT_REGEX = re.compile(r"([a-f0-9]{37,41})")

FILE_TYPES = {
    "img": [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".heic",
        ".nef",
    ],
    "img_other": [".heatmap", ".ico", ".svg", ".webp"],
    "metadata": [".xml", "aae", "exif", "iptc", "tiff", "xmp"],
    "doc": [".pdf", ".doc", ".docx", ".txt", ".odt", ".pptx"],
    "video": [".mp4", ".avi", ".mkv", ".wmv", ".webm", ".m4v", ".flv", ".mpg", ".mov"],
    "audio": [
        ".3ga",
        ".aac",
        ".ac3",
        ".aif",
        ".aiff",
        ".alac",
        ".amr",
        ".ape",
        ".au",
        ".dss",
        ".flac",
        ".flv",
        ".m4a",
        ".m4b",
        ".m4p",
        ".mp3",
        ".mpga",
        ".ogg",
        ".oga",
        ".mogg",
        ".opus",
        ".qcp",
        ".tta",
        ".voc",
        ".wav",
        ".wma",
        ".wv",
    ],
    "zip": [
        ".zip",
        ".rar",
        ".tar",
        ".bz2",
        ".7z",
        ".gz",
        ".xz",
        ".tar.gz",
        ".tgz",
        ".zipx",
    ],
    "raw": [".cr2", ".nef", ".raf", ".dng", ".raf"],
    "settings": [".properties", "ini", ".config", ".cfg", ".conf", ".yml", ".yaml"],
    "text": [".txt", ".md", ".log", ".json", ".csv", ".out", ".note"],
    "code": [
        ".py",
        ".bat",
        ".sh",
        ".c",
        ".cpp",
        ".h",
        ".java",
        ".js",
        ".ts",
        ".php",
        ".html",
        ".css",
        ".scss",
        ".ps1",
    ],
    "other": [
        ".lrprev",
        ".dat",
        ".db",
        ".dbf",
        ".mdb",
        ".sqlite",
        ".sqlite3",
        ".exe",
        ".mdat",
        ".thp",
        ".jar",
        ".mca",
        ".dll",
        ".package",
    ],  # For any other file type
    "ignored": [
        ".trashinfo",
        ".lnk",
        ".plist",
        ".shadow",
        "directoryStoreFile",
        "indexArrays",
        "indexBigDates",
        "indexCompactDirectory",
        "indexDirectory",
        "indexGroups",
        "indexHead",
        "indexIds",
        "indexPositions",
        "indexPostings",
        "indexUpdates",
        "shadowIndexGroups",
        "shadowIndexHead",
        "indexPositionTable",
        "indexTermIds",
        "shadowIndexArrays",
        "shadowIndexCompactDirectory",
        "shadowIndexDirectory",
        "shadowIndexTermIds",
        ".updates",
        ".loc",
        ".state",
        ".37",
        ".tmp",
        ".pyc",
        ".cachedmsg",
        ".git",
    ],
    "dupes": [],  # For duplicate files
}


class File:
    """
    This is the base class for all of the following objects. 
    It represents a generic file and defines the common methods that are used by all of them.
    It can be used standlone (Eg. text based files) or as a parent class for other classes.
    
    Attributes:
    ----------
        encoding (str): The encoding to use when reading/writing the file. Defaults to utf-8.
        path (str): The absolute path to the file.
        content (Any): Contains the content of the file. Only holds a value if read() is called.

    Properties:
    ----------
        size: The size of the file in bytes.
        file_name: The name of the file without its extension.
        extension: The extension of the file (Eg. file.out.txt -> file.out)
        basename: The basename of the file (Eg. file.out.txt)
        is_file: Check if the objects path is a file
        is_executable: Check if the object has an executable flag
        is_image: Check if item is an image
        is_video: Check if item is a video
        is_gitobject: Check if item is a git object
        content: The content of the file. Only holds a value if read() is called.

    Methods:
    ----------
        read(): Return the contents of the file
        head(self, n=5): Return the first n lines of the file
        tail(self, n=5): Return the last n lines of the file
        __eq__(): Compare properties of FileObjects
        __str__(): Return a string representation of the object
        
    """
    def __init__(self, path, encoding='utf-8'):
        """
        Constructor for the FileObject class.

        Paramaters:
        ----------
            path (str): The path to the file
            encoding (str): Encoding type of the file (default is utf-8)
        """
        self.encoding = encoding
        self.path = os.path.abspath(path)
        self._content = None

    def head(self, n=5):
        """
        Return the first n lines of the file

        Paramaters:
        ----------
            n (int): The number of lines to return (default is 5)

        Returns:
        ----------
            str: The first n lines of the file
        """
        if isinstance(self, (File, Exe, Log)):
            return '\n'.join(self.content.split('\n')[:n])
        else:
            raise TypeError("The object must be a FileObject or an ExecutableObject")
    
    def tail(self, n=5):
        """
        Return the last n lines of the file

        Paramaters:
        ----------
            n (int): The number of lines to return (default is 5)

        Returns:
        ----------
            str: The last n lines of the file
        """
        if isinstance(self, (File, Exe)):
            return '\n'.join(self.content.split('\n')[-n:])
        else:
            raise TypeError("The object must be a FileObject or an ExecutableObject")

    @property
    def size(self):
        """
        Return the size of the file in bytes

        Returns:
        ----------
            int: The size of the file in bytes
        """
        return int(os.path.getsize(self.path))
    @property
    def dir_name(self):
        """
        Return the parent directory of the file

        Returns:
            str: The parent directory of the file
        """
        return os.path.dirname(self.path) if not self.is_dir else self.path
    @property
    def file_name(self):
        """
        Return the file name without the extension

        Returns:
        ----------
            str: The file name without the extension
        """
        return str(os.path.splitext(self.path)[0])

    @property
    def basename(self):
        """
        Return the file name with the extension

        Returns:
        ----------
            str: The file name with the extension
        """
        return str(os.path.basename(self.path))

    @property
    def extension(self):
        """
        Return the file extension

        Returns:
        ----------
            str: The file extension
        """
        return str(os.path.splitext(self.path)[-1]).lower()
    @property
    def content(self):
        if not self._content:
            self._content = self.read()
        return self._content.strip()
    def read(self, *args):
        """
        Method for reading the content of a file. This method should overridden for VideoObjects

        Parameters:
            a, b (optional): Return content[a:b]
        Returns:
        ----------
            str: The content of the file
        """
        if isinstance(self, Image):
            with open(self.path, "rb") as f:
                content = f.read()
        elif isinstance(self, (File, Exe)):
            with open(self.path, "r", encoding=self.encoding) as f:
                content = f.read()
        try:
            content = content.decode()
        except (UnicodeDecodeError, AttributeError):
            content = content
        finally:
            return content.split('\n')[args[0]:args[1]] if args else content

    @property
    def is_file(self):
        """
        Check if the object is a file

        Returns:
        ----------
            bool: True if the object is a file, False otherwise
        """
        if GIT_OBJECT_REGEX.match(self.basename):
            return False
        return os.path.isfile(self.path)

    @property
    def is_executable(self):
        """
        Check if the file is executable

        Returns:
        ----------
            bool: True if the file is executable, False otherwise
        """
        return os.access(self.path, os.X_OK)

    @property
    def is_dir(self):
        """
        Check if the object is a directory

        Returns:
        ----------
            bool: True if the object is a directory, False otherwise
        """
        return os.path.isdir(self.path)

    @property
    def is_video(self):
        """
        Check if the file is a video

        Returns:
        ----------
            bool: True if the file is a video, False otherwise
        """
        return self.extension.lower() in FILE_TYPES["video"]

    @property
    def is_gitobject(self):
        """
        Check if the file is a git object

        Returns:
        ----------
            bool: True if the file is a git object, False otherwise
        """
        return GIT_OBJECT_REGEX.match(self.basename)

    @property
    def is_image(self):
        """
        Check if the file is an image

        Returns:
        ----------
            bool: True if the file is an image, False otherwise
        """
        return self.extension.lower() in FILE_TYPES["img"]

    def __iter__(self):
        """
        Iterate over the lines of a file.
        
        Yields:
            str: A line from the file
        """
        if isinstance(self, (File, Exe, Log)):
            for line in self.content.split('\n'):
                yield line.strip()
        else:
            raise TypeError(f"Object of type {type(self)} is not iterable")
    def __len__(self):
        """
        Get the number of lines in a file.
        
        Returns:
        -------
            int: The number of lines in the file
        """
        if isinstance(self, (File, Exe, Log)):
            return len(list(iter(self)))
        else:
            raise TypeError(f"Object of type {type(self)} does not support length operation")
    
    def __contains__(self, item):
         """
         Check if a line exists in the file.
         
         Parameters:
         ----------
             item (str): The line to check for
             
         Returns:
         -------
             bool: True if the line is found, False otherwise
         """
         return any(item in line for line in self)
    
    def __eq__(self, other):
        """
        Compare two FileObjects

        Paramaters:
        ----------
            other (Object): The Object to compare (FileObject, VideoObject, etc.)

        Returns:
        ----------
            bool: True if the two Objects are equal, False otherwise
        """
        if not isinstance(other, File):
            return False
        elif isinstance(other, Video):
            return self.size == other.size
        elif not self._content:
            self._content = self.read()
        return self._content == other.content

    def __str__(self):
        """
        Return a string representation of the FileObject

        Returns:
        ----------
            str: A string representation of the FileObject
        """
        return str(self.__dict__)

class Exe(File):
    """
    A class representing information about an executable file
    
    Attributes:
    ----------
        path (str): The absolute path to the file. (Required)

    Properties:
    ----------
        shebang (str): Return the shebang line of the file
        shebang.setter (str): Set a new shebang
    """
    def __init__(self, path):
        self._shebang = None
        super().__init__(path)

    @property
    def shebang(self):
        """
        Get the shebang line of the file.

        Returns:
        ----------
            str: The shebang line of the file
        """
        if self._shebang is None:
            self._shebang = self.head(1).strip()
        return self._shebang

    @shebang.setter
    def shebang(self, shebang):
        """
        Set a new shebang line for the file.

        Paramaters:
        ----------
            shebang (str): The new shebang line

        Returns:
        ----------
            str: The content of the file after updating the shebang line
        """
        self._content = shebang + self.read()[len(self.shebang.strip()) :]
        try:
            with open(self.path, "w") as f:
                f.seek(0)
                f.write(self._content)

            print(f"{self.basename}\n{self.shebang} -> {shebang}")
            print(self.tail(2))
            self._shebang = shebang
            return self._content
        except PermissionError:
            print(f"Permission denied: {self.path}")
            pass

class Dir(File):
    """
    A class representing information about a directory.
    
    Attributes:
    ----------
        path (str): The path to the directory (Required)
        _files (list): A list of file names in the directory
        _directories (list): A list containing the paths of subdirectories
        _objects (list): A list of items in the directory represented by FileObject
    
    Methods:
    ----------
        file_info (file_name): Returns information about a specific file in the directory
        objects (): Convert each file in self to an appropriate type of object inheriting from FileObject
        __eq__ (other): Compare properties of two DirectoryObjects
        __contains__ (other): Check if an item is present in two DirectoryObjects
        __len__ (): Return the number of items in the object
        __iter__ (): Define an iterator which yields the appropriate instance of FileObject
    
    Properties:
    ----------
        files       : A read-only property returning a list of file names
        objects     : A read-only property yielding a sequence of DirectoryObject or FileObject instances
        directories : A read-only property yielding a list of absolute paths for subdirectories
    
    """
    def __init__(self, path):
        self._files = None
        self._directories = None
        self._objects = None
        super().__init__(path)

    @property
    def files(self):
        """
        Return a list of file names in the directory represented by this object.

        Returns:
        ----------
            list: A list of file names
        """
        if self._files is None:
            self._files = [file for folder in os.walk(self.path) for file in folder[2]]
        return self._files
    @property
    def directories(self):
        """
        Return a list of subdirectory paths in the directory represented by this object.

        Returns:
        ----------
            list: A list of subdirectory paths
        """
        if self._directories is None:
            self._directories = [folder[0] for folder in os.walk(self.path)]
        return self._directories
    @property
    def rel_directories(self):
        """
        Return a list of subdirectory paths relative to the directory represented by this object

        Returns:
            list: A list of subdirectory paths relative to the directory represented by this object
        """
        return [folder.replace(self.path, "") for folder in self.directories]

    def objects(self):
        """
        Convert each file in self to an appropriate type of object inheriting from FileObject.

        Returns:
        ------
            The appropriate inhearitance of FileObject
        """
        if self._objects is None:
            self._objects = [item for item in self]
        return self._objects
        
    def file_info(self, file_name):
        """
        Query the object for files with the given name. Returns an appropriate FileObject if found.

        Paramaters
        ----------
            file_name (str): The name of the file
        Returns:
        ---------

            FileObject: Information about the specified file
        """
        if file_name not in self.files:
            return
        
        # if len(self.directories) == 0:
        #     for f in os.listdir(self.path):
        #         if f == file_name:
        #             return FileObject(os.path.join(self.path, f))
        try:
            try:
                if file_name in os.listdir(self.path):
                    return obj(os.path.join(self.path, file_name))
            except NotADirectoryError:
                pass
            for d in self.directories:
                if file_name in os.listdir(os.path.join(self.path, d)):
                    return obj(os.path.join(self.path, d, file_name))
        except (FileNotFoundError, NotADirectoryError) as e:
            print(e)
            pass
    @property
    def images(self):
        """
        Return a list of ImageObject instances found in the directory.
        
        Returns:
        --------
            List[ImageObject]: A list of ImageObject instances
        """
        return [item for item in self if isinstance(item, Image)]
    def videos(self):
        """
        Return a list of VideoObject instances found in the directory.
        
        Returns:
            List[VideoObject]: A list of VideoObject instances
        """
        return [item for item in self if isinstance(item, Video)]
    @property
    def dirs(self):
        """
        Return a list of DirectoryObject instances found in the directory.
        
        Returns:
            List[DirectoryObject]: A list of DirectoryObject instances
        """
        return [item for item in self if isinstance(item, Dir)]
    
    def __contains__(self, item):
        """
        Compare items in two DirecoryObjects

        Parameters:
        ----------
            item (FileObject, VideoObject, ImageObject, ExecutableObject, DirectoryObject): The item to check.

        Returns:
        ----------
            bool: True if the item is present, False otherwise.
        """
        if (
            isinstance(item, File)
            or isinstance(item, Video)
            or isinstance(item, Image)
            or isinstance(item, Exe)
            or isinstance(item, Dir)
        ):
            return item.basename in self.files
        return item in self.files

    def __len__(self):
        """
        Return the number of items in the object
        
        Returns:
        ----------
            int: The number of files and subdirectories in the directory
        """
        return len(self.directories) + len(self.files)

    def __iter__(self):
        """
        Yield a sequence of FileObject instances for each item in self
        
        Yields:
        -------
            FileObject: The appropriate instance of FileObject
        """
        for root, dirs, files in os.walk(self.path):
            for file in files:
                if os.path.splitext(file)[1].lower() in FILE_TYPES["video"]:
                    yield Video(os.path.join(root, file))
                elif os.path.splitext(file)[1].lower() in FILE_TYPES["img"]:
                    yield Image(os.path.join(root, file))
                elif os.path.splitext(file)[1].lower() in FILE_TYPES["code"]:
                    yield Exe(os.path.join(root, file))
                else:
                    yield File(os.path.join(root, file))
            for directory in dirs:
                yield Dir(os.path.join(self.path, directory))
    def __eq__(self, other):
        """
        Compare two DirectoryObjects

        Parameters:
        ----------
            other (DirectoryObject): The DirectoryObject instance to compare with.

        Returns:
        ----------
            bool: True if the path of the two DirectoryObject instances are equal, False otherwise.
        """
        if not isinstance(other, Dir):
            return False
        return self.path == other.path


class Image(File):
    """
    A class representing information about an image
    
    Attributes:
    ----------
        path (str): The absolute path to the file.

    Methods:
    ----------
        calculate_hash(self): Calculate the hash value of the image
        render(self, size=None): Render an image using kitty at a specified size (optional)
    
    Properties:
    ----------
        capture_date (str or None): Return the capture date of the image
        dimensions (tuple or None): Return a tuple containing the width and height of the image
        exif (dict or None): Return a dictionary containing EXIF data about the image if available
        is_corrupted (bool): Return True if the file is corrupted, False otherwise
    """
    def __init__(self, path):
        self._exif = None
        super().__init__(path)
    def calculate_hash(self, spec='avg'):
        """
        Calculate the hash value of the image

        Paramters:
        ---------
            spec (str): The specification for the hashing algorithm to use.

        Returns:
        ----------
            hash_value (str): The calculated hash value of the image.
            None (None)     : NoneType if an error occurs while calculating the hash
        """

        specs = {
            "avg": lambda x: imagehash.average_hash(x),
            "dhash": lambda x: imagehash.dhash(x),
            "phash": lambda x: imagehash.phash(x)

        }
        # Ignore heic until feature is implemented to support it.
        # Excluding this has unwanted effects when comparing hash values
        if self.extension == ".heic":
            pass

        try:
            with Image.open(self.path) as img:
                hash_value = specs[spec](img)
            return hash_value
        except UnidentifiedImageError as e:
            try:
                if obj(self.path).is_corrupt:
                    print(f"\033[1;31m{self.path} is corrupt\033[0m")
                    return
            except Exception as e:
                print(
                    f'\033[1;32mError detecting corruption of "{self.path}": {e}\033[0m'
                )
                return
            print(f"Error calculating hash: {e}")
            return

    @property
    def dimensions(self):
        """
        Extract the dimensions of the image

        Returns:
        ----------
            Tuple(int, int): width x height of the image in pixels.
        """
        with Image.open(self.path) as img:
            width, height = img.size
        return width, height

    @property
    def exif(self):
        """
        Extract the EXIF data from the image

        Returns:
        ----------
            dict: A dictionary containing the EXIF data of the image.
        """
        if self._exif is not None:
            return self._exif
        # Open Image
        try:
            with Image.open(self.path) as img:
                self._exif = img.getexif()
            return self._exif
        except UnidentifiedImageError as e:
            print(e)
        
    @property
    def capture_date(self):
        """
        Return the capture date of the image if it exists in the EXIF data.

        Returns:
        ----------
            str or None: The capture date in the format 'YYYY:MM:DD HH:MM:SS' if it exists,
                         otherwise None.
        """
        # Iterating over all EXIF data fields
        for tag_id in self.exif:
            # Get the tag name, instead of human unreadable tag id
            tag = TAGS.get(tag_id, tag_id)
            data = self.exif.get(tag_id)
            # Decode bytes
            if isinstance(data, bytes):
                data = data.decode()
            if str(tag).startswith("DateTime"):
                date, time = str(data).split(' ')
                year, month, day = date.split(':')
                hour, minute, second = time.split(':')
                return datetime.datetime(int(year), int(month), int(day),
                                        int(hour),int(minute), int(second[:2]))
                # return data - Depreciated
        return None
    def render(self, width=640, height=640):
        """
        Render the image in the terminal using kitty terminal
        """
        try:
            subprocess.run(
                f'kitten icat --use-window-size {width},100,{height},100 "{self.path}"', shell=True
        )
        except Exception as e:
            print(f"An error occurred while rendering the image:\n{str(e)}")
    def open(self):
        """
        Open the image in default program of your OS
        """
        try:
            img = Image.open(self.path)
            img.show()
            return img
        except UnidentifiedImageError as e:
            print(e)
    @property
    def is_corrupt(self):
        """
        Check if the image is corrupt

        Returns:
        ----------
            bool: True if the image is corrupt, False otherwise
        """
        # If the file is a HEIC image, it cannot be verified
        if self.extension == ".heic":
            return False  # Placeholder TODO

        try:
            # Verify integrity of the image
            img = Image.open(self.path)
            img.verify()
            return False
        # If an IOError or SyntaxError is raised, the image is corrupt           
        except (IOError, SyntaxError):
            return True
        except KeyboardInterrupt:
            sys.exit(0)
        # If any other exception is raised, we didnt account for something so print the error
        except Exception as e:
            print(f"Error: {e}")

    # def __str__(self):
    #     return f"""Image: {self.path}
    #         Dimensions: {self.dimensions}
    #         Hash: {self.hash}
    #         EXIF: {self.exif}
    #         Capture Date: {self.capture_date}"""


class Video(File):
    """
    A class representing information about a video.

    Attributes:
    ----------
        path (str): The absolute path to the file.
    
    Methods:
    ----------
        metadata (dict): Extract metadata from the video including duration, 
                         dimensions, fps, and aspect ratio.
        bitrate (int): Extract the bitrate of the video from the ffprobe output.
        is_corrupt (bool): Check integrity of the video.

    """

    def __init__(self, path):
        super().__init__(path)

    @property
    def metadata(self):
        """
        Extract metadata from the video including duration, dimensions, fps, and aspect ratio.

        Returns:
        ----------
            dict: A dictionary containing the metadata.
        """
        with VideoFileClip(self.path) as clip:
            metadata = {
                "duration": clip.duration,
                "dimensions": (clip.size[0], clip.size[1]),
                "fps": clip.fps,
                "aspect_ratio": clip.aspect_ratio,
            }
        return metadata

    @property
    def bitrate(self):
        """
        Extract the bitrate of the video from the ffprobe output.

        Returns:
        ----------
            int: The bitrate of the video in bits per second.
        """
        ffprobe_cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            self.path,
        ]
        ffprobe_output = subprocess.check_output(ffprobe_cmd).decode("utf-8")
        metadata = json.loads(ffprobe_output)
        capture_date = metadata["format"]["tags"].get("creation_time")
        bit_rate = metadata["format"]["bit_rate"]
        return bit_rate

    @property
    def is_corrupt(self):
        """
        Check if the video is corrupt.

        Returns:
        ----------
            bool: True if the video is corrupt, False otherwise.
        """
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

class Log(File):
    """
    A class to represent a hwlog file.
    """
    def __init__(self, path, spec='csv', encoding='iso-8859-1'):
        self.DIGIT_REGEX = re.compile(r"(\d+(\.\d+)?)")
        specs = {
            'csv': ',',
            'tsv': '\t',
            'custom': ', '
        }
        self.spec = specs[spec]
        super().__init__(path, encoding)
    @property
    def header(self):
        """
        Get the header of the log file.
        
        Returns:
        --------
            str: The header of the log file.
        """
        return self.head(1).strip().strip(self.spec)
    @property
    def columns(self):
        """
        Get the columns of the log file.
        
        Returns:
        --------
            list: Each column of the log file.
        """
        return [col for col in self.head(1).split(self.spec)]
    @property
    def footer(self):
        second_last, last = self.tail(2).strip().split('\n')
        second_last = second_last.strip(self.spec)
        last = last.strip(self.spec)
        return second_last if second_last == self.header else None
 
    def to_df(self):
        """
        Convert the log file into a pandas DataFrame.
        
        Returns:
        --------
            pd.DataFrame: The data of the log file in a DataFrame format.
        """
        import pandas as pd
        return pd.DataFrame(self.content, columns=self.columns)
    def sanatize(self):
        """
        Sanatize the log file by removing any empty lines, spaces, and trailing delimiters
        from the header and footer. Also remove the last 2 lines

        Returns:
        -------
            str: The sanatized content
        """
        SANATIZE_REGEX = re.compile(
                r'(GPU2.\w+\(.*\)|NaN|N\/A|Fan2|°|Â|\*|,,+|\s\[[^\s]+\]|\"|\+|\s\[..TDP\]|\s\[\]|\s\([^\s]\))')
        SUBSTITUTE_REGEX = re.compile(r'(,\s+|\s+,)')
        

        sanatized_content = []
        lines = len(self)
        for i, line in enumerate(self):
            if i == lines - 2:
                break
            sanatized_line = re.sub(SANATIZE_REGEX, '', line).strip().strip(self.spec)
            if sanatized_line:
                sanatized_line = re.sub(SUBSTITUTE_REGEX, ',', sanatized_line)
                sanatized_line = re.sub(r'(\w+)\s+(\w+)', r'\1_\2', sanatized_line)
                sanatized_content.append(sanatized_line)
                

        self._content = '\n'.join(sanatized_content)
        return self._content
    
    @property
    def stats(self):
        df = pd.read_csv(self.path)
        return df.mean()
        #return {'min': df.min(), 'max': df.max(), 'mean': df.mean()}
        
    def compare(self, other): #*args):
        """
        Print a pretty printed comparsion of the stats of this log file with one or more other log files.
        """
        def compare_numbers(num1, num2):
            DIGIT_REGEX = re.compile(r'(\d+(\.\d+)?)')
            
            num1 = DIGIT_REGEX.search(str(num1))[0]
            num2 = DIGIT_REGEX.search(str(num2))[0]
            # num2 = re.search(r'(\d+(\.\d+)?)', line.split(' ')[-1]).group(0)
            if float(num1) == float(num2):
                return f"{num1.replace(num1, f'{fg.cyan}{'\u003d'}{style.reset} {str(num1)}')}", num2
            if float(num1) > float(num2):
                return f"{num1.replace(
                    num1, f'{fg.red}{'\u002b'}{style.reset} {str(num1)}')}", num2 
            else:
                return num1, f"{num2.replace(
                    num2, f' {fg.red}{'\u002b'}{style.reset} {str(num2)}')}"
        def round_values(val):
            try:
                if float(val) < 5:
                    return float("{:.3f}".format(float(val)))  # round to three decimal places
                elif 5 <= float(val) < 15:
                    return float("{:.2f}".format(float(val)))  # round to two decimal places
                else:
                    return int(val)  # no decimal places
            except Exception as e:
                print(e)
                pass
                    
                for k, v in self.stats.items():
                    pass
                
        print('{:<20} {:>15} {:>20}'.format("Sensor", self.basename, other.basename))
        if isinstance(other, Log):
            try:
                df_stats1 = self.stats
                for k, v in df_stats1.items():
                    num1, num2 = compare_numbers(round_values(v), round_values(other.stats[k]))
                    print('{:<32} {:<15} {:>20}'.format(k, num1, num2))
            except KeyError:
                print('KeyError: Key from self.stats is missing in other.stats')
        pass

    def save(self):
        """
        Save the (updated) content to the log file (overwrites original content).
        """
        with open(self.path, 'w') as f:
            f.write(self._content)

def obj(path):
    if not os.path.exists(path):
        raise FileNotFoundError("Path does not exist")

    ext = os.path.splitext(path)[1].lower()
    classes = {
        ".jpg": Image,  # Images
        ".jpeg": Image,
        ".png": Image,
        ".nef": Image,
        ".mp4": Video,  # Videos
        ".avi": Video,
        ".mkv": Video,
        ".wmv": Video,
        ".webm": Video,
        ".mov": Video,
        ".py": Exe,  # Code files
        ".bat": Exe,
        ".sh": Exe,
        "": Dir,  # Directories,

    }
    
    cls = classes.get(ext)
    if not cls:
        return File(path)
    else:
        return cls(path)


if __name__ == "__main__":
    csv = Log('/mnt/hdd-red/HWLOGGING/0.925v_1920mhz.CSV')
    print(csv.compare(Log('/mnt/hdd-red/HWLOGGING/0.950v_1965mhz.CSV')))
    
    print('\n------------------\n')
    for col in csv._stats():
        print(col)
    # img = ImageObject("/home/joona/Pictures/PEGBOARD.jpg")
    # video = VideoObject("/mnt/ssd/compressed_obs/Dayz/blaze kill CQC.mp4")
    # txtfile = FileObject("/home/joona/python/Projects/dir_oraganizer/getinfo.py")
    
    # print(img)
    # print(video)
    # print(txtfile)


# f = len([f for folder in os.walk('/mnt/ssd/compressed_obs/CSGO/')
#         for f in folder])