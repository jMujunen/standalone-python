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


class FileObject:
    def __init__(self, path):
        self.path = path
        self.content = None

    def head(self, n=5):
        lines = []
        if isinstance(self, FileObject):
            try:
                with open(self.path, "r") as f:
                    lines = [next(f) for _ in range(n)]
            except (StopIteration, UnicodeDecodeError):
                pass
        return "".join(lines)

    def tail(self, n=5):
        lines = []
        if isinstance(self, FileObject):
            try:
                with open(self.path, "r") as f:
                    lines = f.readlines()[-n:]
            except (StopIteration, UnicodeDecodeError):
                pass
        return "".join(lines)

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
        with open(self.path, "rb") as f:
            content = f.read()
        try:
            self.content = content.decode()
        except (UnicodeDecodeError, AttributeError):
            self.content = content
        finally:
            return self.content

    @property
    def is_file(self):
        if GIT_OBJECT_REGEX.match(self.basename):
            return False
        return os.path.isfile(self.path)

    @property
    def is_executable(self):
        return os.access(self.path, os.X_OK)

    @property
    def is_dir(self):
        return os.path.isdir(self.path)

    @property
    def is_video(self):
        return self.extension.lower() in FILE_TYPES["video"]

    @property
    def is_gitobject(self):
        return GIT_OBJECT_REGEX.match(self.basename)

    @property
    def is_image(self):
        return self.extension.lower() in FILE_TYPES["img"]
        # return FileObject(os.path.join(self.path, matching_files))

    def __eq__(self, other):
        if not isinstance(other, FileObject):
            return False
        elif isinstance(other, VideoObject):
            return self.size == other.size
        elif self.content is None:
            self.content = self.read()
        return self.content == other.content

    # def __setattr__(self, name, value):
    #     try:
    #         self.__dict__[name] = value
    #         return self.__dict__[name]
    #     except AttributeError:
    #         raise AttributeError(
    #             f"{self.__class__.__name__} object has no attribute {name}"
    #         )

    def __str__(self):
        return str(self.__dict__)


class ExecutableObject(FileObject):
    def __init__(self, path):
        self.path = path
        self._shebang = ""
        super().__init__(self.path)

    @property
    def shebang(self):
        if not self._shebang:
            self._shebang = self.head(1).strip()
        return self._shebang

    @shebang.setter
    def shebang(self, shebang):
        self.content = shebang + self.read()[len(self.shebang.strip()) :]
        try:
            with open(self.path, "w") as f:
                f.seek(0)
                f.write(self.content)

            print(f"{self.basename}\n{self.shebang} -> {shebang}")
            print(self.tail(2))
            self._shebang = shebang
            return self.content
        except PermissionError:
            print(f"Permission denied: {self.path}")
            pass


class DirectoryObject(FileObject):
    def __init__(self, path):
        self.path = path
        self.map = {}
        super().__init__(self.path)

    @property
    def files(self):
        return [file for folder in os.walk(self.path) for file in folder[2]]
        # return [FileObject(os.path.join(folder[0], file))
        #     for folder in os.walk(self.path) for file in folder[2]]

    def objects(self):
        return [
            obj(os.path.join(self.path, folder[0], file))
            for folder in os.walk(self.path)
            for file in folder[2]
        ]

    @property
    def directories(self):
        return [file for folder in os.walk(self.path) for file in folder[1]]

    @property
    def dir_paths(self):
        return [os.path.join(self.path, d) for d in self.directories]

    def file_info(self, file_name):
        if file_name not in self.files:
            return
        if len(self.directories) == 0:
            for f in os.listdir(self.path):
                if f == file_name:
                    return FileObject(os.path.join(self.path, f))
        try:
            try:
                if file_name in os.listdir(self.path):
                    return obj(os.path.join(self.path, file_name))
            except NotADirectoryError:
                pass
            for d in self.directories:
                if file_name in os.listdir(os.path.join(self.path, d)):
                    file = FileObject(os.path.join(self.path, d, file_name))
                    return obj(os.path.join(self.path, d, file_name))
                    # if file.is_image:
                    #     return ImageObject(os.path.join(self.path, d, file_name))
                    # elif file.is_video:
                    #     return VideoObject(os.path.join(self.path, d, file_name))
                    # elif file.is_executable:
                    #     return ExecutableObject(os.path.join(self.path, d, file_name))
                    # else:
                    #     return FileObject(os.path.join(self.path, d, file_name))
        except (FileNotFoundError, NotADirectoryError) as e:
            print(e)
            pass

    def __contains__(self, item):
        if (
            isinstance(item, FileObject)
            or isinstance(item, VideoObject)
            or isinstance(item, ImageObject)
            or isinstance(item, ExecutableObject)
            or isinstance(item, DirectoryObject)
        ):
            return item.basename in self.files
        return item in self.files

    def __len__(self):
        return len(self.directories) + len(self.files)

    def __iter__(self):
        for root, _, file in os.walk(self.path):
            yield DirectoryObject(root)
            for filename in file:
                if os.path.isfile(os.path.join(root, filename)):
                    if os.path.splitext(filename)[1].lower() in FILE_TYPES["video"]:
                        yield VideoObject(os.path.join(root, filename))
                    elif os.path.splitext(filename)[1].lower() in FILE_TYPES["img"]:
                        yield ImageObject(os.path.join(root, filename))
                    elif os.path.splitext(filename)[1].lower() in [
                        ".sh",
                        ".py",
                        ".bash",
                        ".cmd",
                        ".ps1",
                        ".bat",
                    ]:
                        yield ExecutableObject(os.path.join(root, filename))
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
            try:
                if obj(self.path).is_corrupt:
                    print(f"\033[1;31m{self.path} is corrupt\033[0m")
                    return
            except Exception as e:
                print(
                    f'\033[1;32mError detecting corruption of "{self.path}":\033[0m\033[1;31m {e}\033[0m'
                )
                return

            print(f"Error calculating hash: {e}")
            return

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
            if str(tag).startswith("DateTime"):
                return data
        return None

    @property
    def is_corrupt(self):
        try:
            if self.extension == ".heic":
                pass
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
                "aspect_ratio": clip.aspect_ratio,
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
            self.path,
        ]
        ffprobe_output = subprocess.check_output(ffprobe_cmd).decode("utf-8")
        metadata = json.loads(ffprobe_output)
        capture_date = metadata["format"]["tags"].get("creation_time")
        bit_rate = metadata["format"]["bit_rate"]
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


def obj(path):
    if not os.path.exists(path):
        raise FileNotFoundError("Path does not exist")

    ext = os.path.splitext(path)[1].lower()
    classes = {
        ".jpg": ImageObject,  # Images
        ".jpeg": ImageObject,
        ".png": ImageObject,
        ".nef": ImageObject,
        ".mp4": VideoObject,  # Videos
        ".avi": VideoObject,
        ".mkv": VideoObject,
        ".wmv": VideoObject,
        ".webm": VideoObject,
        ".mov": VideoObject,
        ".py": ExecutableObject,  # Code files
        ".bat": ExecutableObject,
        ".sh": ExecutableObject,
        "": DirectoryObject,  # Directories
    }

    cls = classes.get(ext)
    if not cls:
        return FileObject(path)
    else:
        return cls(path)


if __name__ == "__main__":
    img = ImageObject("/home/joona/Pictures/PEGBOARD.jpg")
    video = VideoObject("/mnt/ssd/compressed_obs/Dayz/blaze kill CQC.mp4")
    txtfile = FileObject("/home/joona/python/Projects/dir_oraganizer/getinfo.py")

    print(img)
    print(video)
    print(txtfile)


# f = len([f for folder in os.walk('/mnt/ssd/compressed_obs/CSGO/')
#         for f in folder])
