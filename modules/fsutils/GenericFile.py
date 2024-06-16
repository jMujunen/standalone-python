"""Base class and building block for all other classes defined in this library"""

from ExecutionTimer import ExecutionTimer

with ExecutionTimer():
    print('Generic')
    import os
    import re
    import chardet

    from fsutils.mimecfg import FILE_TYPES

    GIT_OBJECT_REGEX = re.compile(r"([a-f0-9]{37,41})")

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
            detect_encoding(): Return the encoding of the file based on its content
            __eq__(): Compare properties of FileObjects
            __str__(): Return a string representation of the object

        """

        def __init__(self, path, encoding="utf-8"):
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
            # if isinstance(self, (File, Exe, Log)):
            try:
                return "\n".join(self.content.split("\n")[:n])
            except Exception as e:
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
            # if isinstance(self, (File, Exe)):
            try:
                return "\n".join(self.content.split("\n")[-n:])
            except Exception as e:
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
            """
            Helper for self.read()
            Returns the content of the file as a string

            Returns:
            --------
                str: The content of the file
            """
            if not self._content:
                self._content = self.read()
            return self._content.strip()

        def read(self, *args):
            """
            Method for reading the content of a file.

            While this method is cabable of reading certain binary data, it would be good
            practice to override this method in subclasses that deal with binary files.

            Parameters:
            ------------
                a, b (optional): Return content[a:b]
            Returns:
            ----------
                str: The content of the file
            """
            try:
                # if isinstance(self, Img):
                with open(self.path, "rb") as f:
                    content = f.read().decode("utf-8")
                    # elif isinstance(self, (File, Exe)):
                    with open(self.path, "r", encoding=self.encoding) as f:
                        content = f.read()
                # else:
                # raise TypeError(f"Reading {type(self)} is unsupported")
            except Exception as e:
                print(e)
                try:
                    with open(self.path, "r", encoding=self.encoding) as f:
                        content = f.read()
                except Exception as e:
                    print(e)
                    raise TypeError(f"Reading {type(self)} is unsupported")
            self._content = content
            return self._content.split("\n")[args[0] : args[1]] if len(args) == 2 else self._content

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
            return GIT_OBJECT_REGEX.match(self.basename) is not None

        @property
        def is_image(self):
            """
            Check if the file is an image

            Returns:
            ----------
                bool: True if the file is an image, False otherwise
            """
            return self.extension.lower() in FILE_TYPES["img"]

        def detect_encoding(self):
            """
            Detects encoding of the file

            Returns:
            -------
                str: Encoding of the file
            """
            with open(self.path, "rb") as f:
                encoding = chardet.detect(f.read())["encoding"]
            return encoding

        def unixify(self):
            """Convert DOS line endings to UNIX - \\r\\n -> \\n"""
            self._content = re.sub("\r\n", "\n", self.content)
            return self._content

        def __iter__(self):
            """
            Iterate over the lines of a file.

            Yields:
            --------
                str: A line from the file
            """
            try:
                # if isinstance(self, (File, Exe, Log)):
                for line in self.content.split("\n"):
                    yield line.strip()
            except TypeError as e:
                # else:
                raise TypeError(f"Object of type {type(self)} is not iterable")

        def __len__(self):
            """
            Get the number of lines in a file.

            Returns:
            -------
                int: The number of lines in the file
            """
            try:
                # if isinstance(self, (File, Exe, Log)):
                return len(list(iter(self)))
            except Exception as e:
                raise TypeError(f"Object of type {type(self)} does not support len()")

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
            # elif isinstance(other, Video):
            # return self.size == other.size
            try:
                # elif not self._content:
                self._content = self.read()
            except TypeError:
                print(f"Error: {type(other)} is unsupported")
            return self._content == other.content

        def __str__(self):
            """
            Return a string representation of the FileObject

            Returns:
            ----------
                str: A string representation of the FileObject
            """
            return str(self.__dict__)
