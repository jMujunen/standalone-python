#!/usr/bin/env python3

# Import necessary libraries
import re
import subprocess

import requests
from bs4 import BeautifulSoup

PATTERN = re.compile(r".*imgs.xkcd.com/comics/.*")


def get_xkcd_comic() -> str:
    """Process the HTTP request."""
    page = requests.get("https://c.xkcd.com/random/comic/")
    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(page.content, "html.parser")
    # Find img tag
    img_tag = soup.find_all("img")
    if img_tag:
        for tag in img_tag:
            if PATTERN.match(tag["src"]):
                url = f'https:{tag["src"]}'
                return url

    raise Exception("No img tag found for the following cfg. `<img src=.*imgs.xkcd.com/comics/.*>`")


if __name__ == "__main__":
    url = get_xkcd_comic()
    print(f"Found comic: {url}")
    reponse = requests.get(url)
    page_content = reponse.content
    try:
        # Save to tmpfs and attempt to render with kitty
        with open("/tmp/xkcd.png", "wb") as f:
            f.write(page_content)
        subprocess.run(
            ["kitten", "icat", "/tmp/xkcd.png"],
            shell=True,
            check=False,
        )
    except Exception as e:
        print(f"Failed to save/open {url}:\n\n{e}")
