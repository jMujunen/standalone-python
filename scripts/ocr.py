#!/usr/bin/env python3
"""img2txt.py - Extract text from an image."""

import os
import subprocess
import sys
from pathlib import Path

import clipboard
import cv2
import pytesseract


def notify(status: str, icon: str) -> int:
    """Send a desktop notification.

    Parameters
    -----------
        status (str): The message to display in the notification.
        icon (str): The path to an image file to use as the notification's icon.

    Returns
    --------
        int: The return code of the subprocess call. If it is 0, then the command was successful.

    """
    cmd = [
        "notify-send",
        status,
        "-u",
        "normal",
        "--app-name=OCR",
        f"--icon={icon}",
        "-t",
        "2000",
    ]
    return subprocess.call(cmd)


def take_screenshot(output_dir: str = "~/Pictures/Screenshots/OCR") -> Path:
    """Take a screenshot of the selected area and save it to a specified directory.

    Parameters
    -----------
        output_dir (str): The path to the directory where the screenshot will be saved. Defaults to "~/Pictures/Screenshots/OCR".

    Returns
    --------
        str: The full path of the saved screenshot.
    """
    output_path = Path(output_dir).expanduser() / "imagegrab.png"
    Path.mkdir(output_path.parent, parents=True, exist_ok=True)

    # Take a screenshot of a selected area
    try:
        subprocess.check_output(
            [
                "spectacle",
                "-rbn",
                "--output",
                str(output_path),
            ]
        )
    except subprocess.CalledProcessError:
        notify("Failed to take screenshot", "dialog-close")

    return output_path


def extract_text(image_path: str) -> str:
    """Extract text from an image using OCR (Optical Character Recognition).

    Parameters
    -----------
        image_path (str): The path to the image file.

    Returns
    --------
        str: The extracted text as a string.
    """
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Use thresholding to preprocess the image
    _, threshold = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return pytesseract.image_to_string(threshold, lang="eng")


if __name__ == "__main__":
    try:
        image = take_screenshot()
        text = extract_text(str(image))
        print(text)
        # Print extracted text and copy to the clipboard
        print(f"\033[32m{text}\033[0m")
        clipboard.copy(text)
    except Exception as e:
        print(f"{e:!s}")
        sys.exit(1)
    # Send a notification
    try:
        code = notify("Success", "region")
        sys.exit(code)
    except subprocess.CalledProcessError:
        print("Failed to send notification")
        sys.exit(1)
    finally:
        sys.exit(0)
