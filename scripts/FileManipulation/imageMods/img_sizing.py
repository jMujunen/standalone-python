#!/usr/bin/env python3

# img_sizing.py - Resizes images and displays image dimensions

import argparse
from PIL import Image

def parse_args():
    """
    Parse the command-line arguments for image resizing.

    Args:
        None

    Returns:
        parsed arguments from the command line
    """
    parser = argparse.ArgumentParser(description="Image Resizer")
    parser.add_argument("image_path", help="path to the input image")
    parser.add_argument("--width", type=int, help="desired width of the output image")
    parser.add_argument("--height", type=int, help="desired height of the output image")
    parser.add_argument("-o", "--output", help="path to save the resized image")
    parser.add_argument("-d", "--dimensions", action="store_true", help="display image dimensions")

    return parser.parse_args()

def get_image_dimensions(image_path):
    """
    Function to get the dimensions of an image from the given image path.
    
    Args: 
        image_path: The path of the image file.

    Returns
        None
    """
    with Image.open(image_path) as img:
        width, height = img.size
        print(f"Image dimensions: {width} x {height}")

def resize_image(image_path, width, height, output_path):
    """
    Resize an image to the specified width and height and save the resized image to the output path.

    Args:
        image_path (str): The file path of the input image.
        width (int): The desired width of the resized image.
        height (int): The desired height of the resized image.
        output_path (str): The file path where the resized image will be saved.

    Returns:
        None
    """
    with Image.open(image_path) as img:
        resized_img = img.resize((width, height))
        resized_img.save(output_path)
        print(f"Resized image saved to: {output_path}")

def main():
    """
    A function to execute the main logic of the program. It parses arguments, checks for dimensions, and resizes the image accordingly.
    Args:
        None

    Returns:
        None
    """
    args = parse_args()
    if args.dimensions:
        get_image_dimensions(args.image_path)
    elif args.width and args.height and args.output:
        resize_image(args.image_path, args.width, args.height, args.output)
    else:
        print('Error')

# Execute the main function if the script is run standalone
if __name__ == "__main__":
    main()