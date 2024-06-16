"""Represents an image"""

from ExecutionTimer import ExecutionTimer

with ExecutionTimer():
    print('Img')
    import subprocess
    import datetime

    from PIL import Image, UnidentifiedImageError
    from PIL.ExifTags import TAGS
    import ollama
    import imagehash

    from fsutils.GenericFile import File

    class Img(File):
        """
        A class representing information about an image

        Attributes:
        ----------
            path (str): The absolute path to the file.

        Methods:
        ----------
            calculate_hash(self): Calculate the hash value of the image
            render(self, size=None): Render an image using kitty at a specified size (optional)
            generate_title(): EXPERIMENTAL! - Generate a title for the image using ollama

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

        def calculate_hash(self, spec="avg"):
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
                "phash": lambda x: imagehash.phash(x),
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
                file = Img(self.path)
                if file.is_corrupt:
                    print(f"\033[1;31m{self.path} is corrupt\033[0m")
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
                    date, time = str(data).split(" ")
                    year, month, day = date.split(":")
                    hour, minute, second = time.split(":")
                    return datetime.datetime(
                        int(year),
                        int(month),
                        int(day),
                        int(hour),
                        int(minute),
                        int(second[:2]),
                    )
            return None

        def generate_title(self):
            """Generate a title for the image using ollama"""
            try:
                response = ollama.chat(
                    model="llava",
                    messages=[
                        {
                            "role": "user",
                            "content": "Catagorize the image into 1 of the following based on the scene. Cat, Portrait, Car, Nature",  # Based off the scene in the image, create a filename under 5 tokens?",
                            "images": [self.path],
                        },
                    ],
                )
                return response["message"]["content"]
            except Exception as e:
                print(f"An error occurred while generating a title:\n{str(e)}")

        def render(self, width=640, height=640):
            """Render the image in the terminal using kitty terminal"""
            try:
                subprocess.run(
                    f'kitten icat --use-window-size {width},100,{height},100 "{self.path}"',
                    shell=True,
                    check=False,
                )
            except Exception as e:
                print(f"An error occurred while rendering the image:\n{str(e)}")

        def open(self):
            """Save img to /tmp and open the image in the OS default image viewer"""
            try:
                with Image.open(self.path) as f:
                    f.show()
                return f
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
                with Image.open(self.path) as f:
                    f.verify()
                return False
            # If an IOError or SyntaxError is raised, the image is corrupt
            except (IOError, SyntaxError):
                return True
            except KeyboardInterrupt:
                return
            # If any other exception is raised, we didnt account for something so print the error
            except Exception as e:
                print(f"Error: {e}")
