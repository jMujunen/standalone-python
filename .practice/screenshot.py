#!/usr/bin/env python3

import datetime
import os

from PIL import ImageGrab


def take_screenshot():
    # Define the filename with date and time
    filename = "Screenshot_{}.png".format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    filepath = os.path.join(os.path.expanduser("~"), "Pictures", filename)

    # Take a screenshot
    screenshot = ImageGrab.grab()
    screenshot.save(filepath)

    # Notify the user where the screenshot has been saved
    print("Screenshot saved as {filepath}")


if __name__ == "__main__":
    take_screenshot()
