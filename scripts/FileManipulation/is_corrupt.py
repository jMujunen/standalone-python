#!/usr/bin/env python3

from ExecutionTimer import ExecutionTimer
import sys
import cv2
from PIL import Image
import clipboard
import re
import os


re.compile(r"(^Y|^y|^)$")

IMAGES = ['.jpg', '.jpeg', '.png', '.gif', '.heic', '.nef','.webp', '.svg', '.ico', '.heatmap']
VIDEOS = ['.mp4', '.avi', '.mkv', '.wmv', '.webm', '.m4v', '.flv', '.mpg']

def is_video_corrupt(file_path):
    try:
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            return True  # Video is corrupt
        else:
            return False  # Video is not corrupt
    except:
        return True  # Video is corrupt


def is_image_corrupt(file_path):
    try:
        img = Image.open(file_path)
        img.verify()
        return False  # Image is not corrupt
    except (IOError, SyntaxError):
        return True  # Image is corrupt



with ExecutionTimer():
    if sys.argv[1] == "--help":
        print("Checks if vid is corrupt or not")
        print("Usage: python is_corrupt.py <DIR>")
        sys.exit(0)

    corrupt_files = []
    for root, _, files in os.walk(sys.argv[1]):
        for file in files:
            if file[-4:].lower() in VIDEOS:  # file[-4:]
                if is_video_corrupt(os.path.join(root, file)):
                    print(f"\033[31m{file} is corrupt\033[0m")
                    corrupt_files.append(os.path.join(root, file))
                else:
                    print(f"\033[32m{file} is not corrupt\033[0m")
            elif file[-4:].lower() in IMAGES:
                if is_image_corrupt(os.path.join(root, file)):
                    print(f"{file} is corrupt")
                    corrupt_files.append(os.path.join(root, file))

    print(f"Found {len(corrupt_files)} corrupt files:\n {corrupt_files}")
    with open("corrupt_files.txt", "w") as f:
        f.write("\n".join(corrupt_files))
    print("Corrupt files saved to corrupt_files.txt")
    


   
