#!/usr/bin/env python3
"""img2txt.py - Extract text from an image."""

import os
import subprocess
import tempfile

import clipboard
import cv2
import pytesseract
from PIL import Image


def notify(status: str, icon: str) -> int:
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


def take_screenshot(output_dir="~/Pictures/Screenshots/OCR") -> str:
    filename = "imagegrab.png"
    output_path = os.path.join(os.path.expanduser(output_dir), filename)
    # Take a screenshot of a selected area
    try:
        subprocess.check_output(
            [
                "spectacle",
                "-rbn",
                "--output",
                output_path,
            ]
        )
    except subprocess.CalledProcessError:
        notify("Failed to take screenshot", "dialog-close")
    return output_path


def extract_text(image_path: str) -> str:
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Use thresholding to preprocess the image
    _, threshold = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return pytesseract.image_to_string(threshold, lang="eng")


if __name__ == "__main__":
    image = take_screenshot()
    text = extract_text(image)
    print(text)
    # Print extracted text and copy to the clipboard
    print(f"\033[32m{text}\033[0m")
    clipboard.copy(text)
    # Send a notification
    notify("Success", "region")
