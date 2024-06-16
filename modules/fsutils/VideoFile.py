"""Video: Represents a video file. Has methods to extract metadata like fps, aspect ratio etc."""

from ExecutionTimer import ExecutionTimer

with ExecutionTimer():
    print('Video')
    import subprocess
    import os
    import json
    import cv2
    import sys

    from fsutils.GenericFile import File

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
            self._metadata = None
            super().__init__(path)

        @property
        def metadata(self):
            if not self._metadata:
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
                self._metadata = json.loads(ffprobe_output).get('format')
            return self._metadata

        @property
        def bitrate(self):
            """
            Extract the bitrate of the video from the ffprobe output.

            Returns:
            ----------
                int: The bitrate of the video in bits per second.
            """
            return self.metadata.get('bit_rate')

        @property
        def duration(self):
            return self.metadata.get('duration')

        @property
        def capture_date(self):
            return self.metadata.get('tags').get('creation_time')

        # @property
        # def capture_date(self):
        #     if not self._metadata:
        #         self._metadata =

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

        def render(self):
            """Render the video using in the shell using kitty protocols."""
            if os.environ.get("TERM") == 'xterm-kitty':
                try:
                    subprocess.call(['mpv', self.path])
                except Exception as e:
                    print(f"Error: {e}")
            else:
                try:
                    subprocess.call(["xdg-open", self.path])
                except Exception as e:
                    print(f"Error: {e}")
