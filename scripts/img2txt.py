#!/usr/bin/env python3
"""img2txt.py - Extract text from an image"""

import datetime
import os
import subprocess
import tempfile

import clipboard
import cv2
import pytesseract
from PIL import Image


def take_screenshot() -> str:
    # Define the filename with date and time
    filename = "Area_{}.png".format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots", filename)

    # Take a screenshot of a selected area
    subprocess.run(
        "spectacle -rbn --output /home/joona/Pictures/Screenshots/OCR/imagegrab.png",
        shell=True,
        check=False,
    )
    img_path = "/home/joona/Pictures/Screenshots/OCR/imagegrab.png"

    return img_path


def get_text_from_image(image_path: str) -> str:
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Use thresholding to preprocess the image
    _, threshold = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    with tempfile.NamedTemporaryFile(delete=True, suffix=".png") as temp_file:
        cv2.imwrite(temp_file.name, gray)
        # Use pytesseract to extract text from the preprocessed image
        text = pytesseract.image_to_string(Image.open(temp_file.name))

    # Return the extracted text
    return text


if __name__ == "__main__":
    image = take_screenshot()
    text = get_text_from_image(image)
    # Print extracted text and copy to the clipboard
    print(f"\033[32m{text}\033[0m")
    clipboard.copy(text)
    # Send a notification
    shell_output = subprocess.run(
        f'kdialog --msgbox "OCR Complete" "{text} --icon=region"',
        #f'notify-send "Extracted Text:" --icon=spectacle --app-name="OCR" "{text}" ',
        shell=True,
        check=False,
    )
