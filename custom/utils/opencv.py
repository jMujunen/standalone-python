import os
from datetime import timedelta

import cv2
import cython
import numpy as np
import pytesseract
from Color import cprint, fg, style
from FrameBuffer import FrameBuffer
import moviepy
from numpy import ndarray
from collections import namedtuple

INTERVAL = 60
WRITER_FPS = 60
BUFFER = 120
log_template = "[{}] {} - Frame {}"

ROI_W, ROI_H = (800, 200)
ALT_W, ALT_H = (800, 200)

MONITOR_DIMS = (1920, 1080)
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}

NULLSIZE = 300

dimensions = namedtuple("dimensions", ["w", "h"])
video_props = namedtuple("video_props", ["w", "h", "fps"])

ROI = dimensions(w=800, h=200)

region_of_interest = namedtuple("region_of_interest", ["x", "y", "w", "h"])


def name_in_killfeed(img: ndarray, keywords: list[str], *args: tuple[int, ...]) -> tuple[bool, str]:
    """Check if a kill-related keyword is present in the text extracted from the ndarray.

    Parameters
    -----------
        - `img (ndarray)` : The image to extract text from
        - `keywords (list[str])` : The keywords to search for in the text
        - `*args (tuple[int])` : The region of interest(s) to extract text from in the format: x, y, w, h
    """
    preprocessed_frames = []
    if args is not None:
        for arg in args:
            x, y, w, h = arg  # type: ignore
            roi = img[y : y + h, x : x + w]
            # Crop the frame to the region of interest (rio)
            gray_frame = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            preprocessed_frames.append(cv2.threshold(gray_frame, 175, 255, cv2.THRESH_BINARY)[1])
            preprocessed_frames.append(
                cv2.threshold(gray_frame, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            )

    concatted_img = cv2.hconcat(preprocessed_frames)
    text = pytesseract.image_to_string(concatted_img, lang="eng")

    # Check if any kill-related keyword is present in the extracted text
    if any(keyword.lower() in text.lower() for keyword in keywords):
        return True, text.lower()
    return False, text.lower()


def format_timedelta(td: timedelta) -> str:
    """Format timedelta objects in a descriptive manor (e.g 00:00:20.05)
    omitting microseconds and retaining milliseconds."""
    result = str(td)
    try:
        result, ms = result.split(".")
    except ValueError:
        return (result + ".00").replace(":", "-")
    ms = int(ms)
    ms = round(ms / 1e4)
    return f"{result}.{ms:02}".replace(":", "-")


def video_from_frames(frame_list: list[np.ndarray], video_path: str, output_path: str) -> None:
    """Write frames to a video file using OpenCV's VideoWriter class.

    Parameters
    ----------
        - `frame_list (list[np.ndarray])` : list of frames to write into the video file.
        - `video_path (str)` : path to the video file that you want to extract frames from.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # type: ignore
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    for frame in frame_list:
        out.write(frame)


def find_continuous_segments(frames: list[int]) -> list[list[int]]:
    if not frames:
        return []

    segments = [[frames[0]]]
    for i in range(1, len(frames)):
        if frames[i] == frames[i - 1] + 1:
            segments[-1].append(frames[i])
        else:
            segments.append([frames[i]])
    return segments


def create_video_clip(frames: list[np.ndarray], fps=60) -> moviepy.ImageSequenceClip:
    return moviepy.ImageSequenceClip(frames, fps=fps)


def save_keyframe(
    frame: np.ndarray, frame_duration: float, filename: str, output_folder: str
) -> None:
    """Save a keyframe to the specified output folder with a name that includes its duration in seconds.

    Parameters
    ----------
        - `frame (np.ndarray)` : The frame to be saved.
        - `frame_duration (float)` : Duration of the frame in seconds.
        - `filename (str)` : Name of the file where the keyframe will be stored.
        - `output_folder (str)` : Path to the output folder where the keyframe will be saved.

    Example:
    ---------
    >>> while cap.isOpened():
            ret, frame = cap.read()
            save_keyframe(frame, 0.0166, 'output', './')
    """
    frame_duration_formatted = format_timedelta(timedelta(seconds=frame_duration))
    cv2.imwrite(os.path.join(output_folder, f"frame{frame_duration_formatted}.jpg"), frame)


def create_frame_index(
    vid_path: str, output_path: str, buffer: FrameBuffer, keywords: list[str]
) -> list[str]:
    """Return a list of frames indices that contain <keywords>.

    Parameters
    -----------
        - `interval` (int): How often to check for <keywords> in the video (in frames)
        - `buffer` (int): An instance of a FrameBuffer to cache a limited number of frames
        - `keywords` (list): A list of keywords to to look for in the killfeed.

    Returns
    --------
    - `log` (list): A Debug log
    """
    log = []
    log_template = "{}[{}]{} {} - Frame {}"  # <LOG-LEVEL> - <MESSAGE TEXT> <CURRENT FRAME>
    cap = cv2.VideoCapture(vid_path)
    if not cap.isOpened():
        msg = log_template.format("ERROR", "Failed to open ", vid_path)
        cap.release()
        return log

    # Extract vars from video
    count = 0
    cap = cv2.VideoCapture(vid_path, cv2.CAP_FFMPEG)

    # Temporary placeholder vars
    kill_detected = False
    name = ""
    frame_index = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        buffer.add_frame((frame, count))
        # Check for killfeed every <INTERVAL> frames instead of each frame to save time/resources
        if count % INTERVAL == 0:
            kill_detected, name = name_in_killfeed(frame, keywords)
            if kill_detected is True:
                msg = log_template.format(fg.green, "DETECT", style.reset, "Kill found @", count)
                print(f"{msg:60}", end=" ")
                # Write the past <INTERVAL> frames to the output video
                for _buffered_frame, index in buffer.get_frames():
                    # This is a check to ensure that we don't write duplicate frames
                    if index not in frame_index:
                        msg = log_template.format(
                            fg.cyan, "WRITE", style.reset, "Wrote frame", index
                        )
                        cprint(f"{msg:60}", end="\r")
                        frame_index.append(index)
                    else:
                        msg = log_template.format(
                            fg.yellow, "SKIPPED", style.reset, "Duplicate frame", index
                        )
                        print(msg, end="\r")
            else:  # Debug logging
                msg = log_template.format(fg.orange, "SKIPPED", style.reset, "No kill", count)
                log.append("\t".join([msg, name]))
                print(f"{msg}", end="\r")

        count += 1
    # Flag for garbage collection
    cap.release()

    return frame_index


def video_to_ndarray(video_path: str, saving_fps: int = 1) -> list[ndarray]:
    count: cython.int
    event_gap: cython.double
    video_fps: cython.int
    num_frames: cython.int
    frames: list[ndarray] = []

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    # Extract vars from video(\w+)\s=\sR
    cap = cv2.VideoCapture(video_path)
    video_fps = round(cap.get(cv2.CAP_PROP_FPS))
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames = []

    event_gap = video_fps / saving_fps
    count = 0
    print(event_gap)
    print(video_fps)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        print(f"Processing frame {count}/{num_frames}", end="\r")
        # Check for killfeed every <event_gap> frames instead of each frame to save time/resources
        if count % event_gap == 0:
            frames.append(frame)
        count += 1
    return frames
