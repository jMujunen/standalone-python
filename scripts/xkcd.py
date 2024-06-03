#!/usr/bin/env python3

import re
import subprocess
import requests
from bs4 import BeautifulSoup

PATTERN = pattern = re.compile(r'.*imgs.xkcd.com/comics/.*')

def get_xkcd_comic():
    # Send HTTP request
    page = requests.get('https://c.xkcd.com/random/comic/')    
    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(page.content, 'html.parser')
    # Find img tag
    img_tag = soup.find_all('img')
    
    for tag in img_tag:
        if PATTERN.match(tag['src']):
            url = f'https:{tag['src']}'
            return url
    
    raise Exception('No img tag found for the following cfg. `<img src=.*imgs.xkcd.com/comics/.*>`') 
        
if __name__ == "__main__":
    url = get_xkcd_comic()
    print(f'Found comic: {url}')
    reponse = requests.get(url)
    page_content = reponse.content
    try:
        # Try to open the image with default application
        with open('/tmp/xkcd.png', 'wb') as f:
            f.write(page_content)
        subprocess.run(
            'kitten icat /tmp/xkcd.png',
            shell=True,
        )
    except:
        print(f'Failed to save/open {url}')