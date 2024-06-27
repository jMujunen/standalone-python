#!/usr/bin/env python3
"""Adds bullet points to copied text"""

import pyperclip

text = pyperclip.paste()

lines = text.split('\n')

for i in range(len(lines)):
    lines[i] = '- ' + lines[i]

text = '\n'.join(lines)
pyperclip.copy(text)
print('Paste complete: \n' + text)
