#!/usr/bin/env python3
"""Generates a random RGB color as a tuple"""

# rng_rgb.py - Random RGB color generator
# TLDR:
import random


def generate_rgb():
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)
    return (red, green, blue)


if __name__ == "__main__":
    print(generate_rgb())
