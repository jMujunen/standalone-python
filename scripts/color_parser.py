#!/usr/bin/env python3

# color_parser.py - Parse plaintext color to rgb or hexadecimal representation

import os, sys
import argparse
import clipboard

COLOR_DICT = {
    'aliceblue': (240, 248, 255),
    'antiquewhite': (250, 235, 215),
    'aqua': (0, 255, 255),
    'aquamarine': (127, 255, 212),
    'azure': (240, 255, 255),
    'beige': (245, 245, 220),
    'bisque': (255, 228, 196),
    'black': (0, 0, 0),
    'blanchedalmond': (255, 235, 205),
    'blue': (0, 0, 255),
    'blueviolet': (138, 43, 226),
    'brown': (165, 42, 42),
    'burlywood': (222, 184, 135),
    'cadetblue': (95, 158, 160),
    'chartreuse': (127, 255, 0),
    'chocolate': (210, 105, 30),
    'coral': (255, 127, 80),
    'cornflowerblue': (100, 149, 237),
    'cornsilk': (255, 248, 220),
    'crimson': (220, 20, 60),
    'cyan': (0, 255, 255),
    'darkblue': (0, 0, 139),
    'darkcyan': (0, 139, 139),
    'darkgoldenrod': (184, 134, 11),
    'darkgray': (169, 169, 169),
    'darkgreen': (0, 100, 0),
    'darkkhaki': (189, 183, 107),
    'darkmagenta': (139, 0, 139),
    'darkolivegreen': (85, 107, 47),
    'darkorange': (255, 140, 0),
    'darkorchid': (153, 50, 204),
    'darkred': (139, 0, 0),
    'darksalmon': (233, 150, 122),
    'darkseagreen': (143, 188, 143),
    'darkslateblue': (72, 61, 139),
    'darkslategray': (47, 79, 79),
    'darkturquoise': (0, 206, 209),
    'darkviolet': (148, 0, 211),
    'deeppink': (255, 20, 147),
    'deepskyblue': (0, 191, 255),
    'dimgray': (105, 105, 105),
    'dodgerblue': (30, 144, 255),
    'firebrick': (178, 34, 34),
    'floralwhite': (255, 250, 240),
    'forestgreen': (34, 139, 34),
    'fuchsia': (255, 0, 255),
    'gainsboro': (220, 220, 220),
    'ghostwhite': (248, 248, 255),
    'gold': (255, 215, 0),
    'goldenrod': (218, 165, 32),
    'gray': (128, 128, 128),
    'green': (0, 128, 0),
    'greenyellow': (173, 255, 47),
    'honeydew': (240, 255, 240),
    'hotpink': (255, 105, 180),
    'indianred': (205, 92, 92),
    'indigo': (75, 0, 130),
    'ivory': (255, 255, 240),
    'khaki': (240, 230, 140),
    'lavender': (230, 230, 250),
    'lavenderblush': (255, 240, 245),
    'lawngreen': (124, 252, 0),
    'lemonchiffon': (255, 250, 205),
    'lightblue': (173, 216, 230),
    'lightcoral': (240, 128, 128),
    'lightcyan': (224, 255, 255),
    'lightgoldenrodyellow': (250, 250, 210),
    'lightgray': (211, 211, 211),
    'lightgreen': (144, 238, 144),
    'lightpink': (255, 182, 193),
    'lightsalmon': (255, 160, 122),
    'lightseagreen': (32, 178, 170),
    'lightskyblue': (135, 206, 250),
    'lightyellow': (255, 255, 224),
    'lime': (0, 255, 0),
    'linen': (250, 240, 230),
    'magenta': (255, 0, 255),
    'maroon': (128, 0, 0),
    'mediumaquamarine': (102, 205, 170),
    'mediumorchid': (186, 85, 211),
    'mediumseagreen': (60, 179, 113),
    'mediumslateblue': (123, 104, 238),
    'mediumspringgreen': (0, 250, 154),
    'mediumvioletred': (199, 21, 133),
    'mintcream': (245, 255, 250),
    'mistyrose': (255, 228, 225),
    'navajowhite': (255, 222, 173),
    'oldlace': (253, 245, 230),
    'olive': (128, 128, 0),
    'orange': (255, 165, 0),
    'orangered': (255, 69, 0),
    'palegoldenrod': (238, 232, 170),
    'palegreen': (152, 251, 152),
    'palevioletred': (219, 112, 147),
    'peru': (205, 133, 63),
    'plum': (221, 160, 221),
    'powderblue': (176, 224, 230),
    'purple': (128, 0, 128),
    'red': (255, 0, 0),
    'rosybrown': (188, 143, 143),
    'saddlebrown': (139, 69, 19),
    'salmon': (250, 128, 114),
    'sandybrown': (244, 164, 96),
    'seashell': (255, 245, 238),
    'silver': (192, 192, 192),
    'skyblue': (135, 206, 235),
    'slateblue': (106, 90, 205),
    'snow': (255, 250, 250),
    'steelblue': (70, 130, 180),
    'tan': (210, 180, 140),
    'teal': (0, 128, 128),
    'thistle': (216, 191, 216),
    'wheat': (245, 222, 179),
    'white': (255, 255, 255),
    'yellow': (255, 255, 0),
    'yellowgreen': (154, 205, 50)
 }


def parse_args():
    parser = argparse.ArgumentParser(
        description='Plain text color to rgb or hexadecimal representation',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

    parser.add_argument('COLOR', help='Color name')

    parser.add_argument(
        '--hex',
        action='store_true',
        help='Return hex value of COLOR',
        default=False
    )

    parser.add_argument(
        '--rgb',
        action='store_true',
        help='Return rgb value of COLOR',
        default=True
    )

    return parser.parse_args()

def color_to_hex(color):
    """
    Convert a color name to its hexadecimal representation.

    Args:
        color (str): The name of the color to be converted.

    Returns:
        str: The hexadecimal representation of the input color.
    """
    rgb = COLOR_DICT[color]
    return '#%02x%02x%02x' % rgb

def color_to_rgb(color):
    """
    A function that converts a color to its corresponding RGB value from the COLOR_DICT.
    
    Parameters:
    color (str): The color to be converted to RGB.
    
    Returns:
    str: The RGB value corresponding to the input color.
    """
    return COLOR_DICT[color]

def main(args):
    if args.hex:
        args.rgb = False
        parsed_color = color_to_hex(args.COLOR)
    if args.rgb:
        parsed_color = color_to_hex(args.COLOR)
    return parsed_color

if __name__ == '__main__':
    args = parse_args()
    parsed_color = main(args)
    print(parsed_color)
    clipboard.copy(parsed_color)