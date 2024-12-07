#!/usr/bin/env python3

# Import necessary libraries
import re
import subprocess
from time import sleep

import requests
from bs4 import BeautifulSoup
from Color import cprint, fg
from ExecutionTimer import ExecutionTimer

PATTERN = re.compile(r".*imgs.xkcd.com/comics/.*")


def get_xkcd_comic() -> str:
    """Process the HTTP request."""
    page = requests.get("https://c.xkcd.com/random/comic/")
    # Parse the content with BeautifulSoup
    print(f"Page status code: {page.status_code}")
    soup = BeautifulSoup(page.content, "html.parser")
    # Find img tag
    img_tag = soup.find_all("img")
    if img_tag:
        for tag in img_tag:
            if PATTERN.match(tag["src"]):
                return f'https:{tag["src"]}'

    raise Exception("No img tag found for the following cfg. `<img src=.*imgs.xkcd.com/comics/.*>`")


def save(data: bytes) -> str:
    """Save image to /tmp/xkcd.png."""
    with open("/tmp/xkcd.png", "wb") as f:
        f.write(data)
        return "/tmp/xkcd.png"
    return ""


def main() -> None:
    with ExecutionTimer():
        print("Connecting to page...")
        img_url = get_xkcd_comic()
        print(f"Source located at {img_url}...")
        reponse = requests.get(img_url)
        page_content = reponse.content
        try:
            with open("/tmp/xkcd.png", "wb") as f:
                f.write(page_content)
            subprocess.run(
                ["kitty", "+kitten", "icat", "/tmp/xkcd.png"],
                check=False,
            )
        except Exception as e:
            print(f"Failed to save/open {img_url}:\n\n{e!r}")


if __name__ == "__main__":
    main()
