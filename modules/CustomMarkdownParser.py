#!/usr/bin/env python3

# CustomMarkdownParser.py - A simple Markdown parser

import re
import argparse

class MarkdownParser:
    def __init__(self):
        self.rules = [
            ('# (.*)', '<h1>\g<1></h1>'),  # Headers
            ('\* (.*)', '<ul>\n<li>\g<1></li>\n</ul>'),  # Lists
            ('\*\*(.*)\*\*', '<b>\g<1></b>'),  # Bold
            ('\*(.*)\*', '<i>\g<1></i>'),  # Italic
            ('\[(.*)\]\((.*)\)', '<a href="\g<2>">\g<1></a>')  # Links
        ]

    def parse(self, text):
        for pattern, replacement in self.rules:
            text = re.sub(pattern, replacement, text)
        return text

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    args = parser.parse_args()

    with open(args.file, 'r') as file:
        text = file.read()

    markdown_parser = MarkdownParser()
    html = markdown_parser.parse(text)

    print(html)

if __name__ == '__main__':
    main()



'''
Perplexity

import re

class MarkdownParser:
    def __init__(self, text):
        self.text = text
        self.tokens = []

    def parse(self):
        self.tokens = self.lexer.tokenize(self.text)
        self.ast = self.parser.parse(self.tokens)
        return self.ast

    def render(self):
        return self.renderer.render(self.ast)

class Lexer:
    def __init__(self, text):
        self.text = text

    def tokenize(self):
        tokens = []
        for match in re.finditer(r"(\*|_)(\w+)", self.text):
            tokens.append(match.group(1))
        return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens

    def parse(self):
        ast = []
        for token in self.tokens:
            if token == "*":
                ast.append(["bold", token])
            elif token == "_":
                ast.append(["italic", token])
        return ast

class Renderer:
    def __init__(self, ast):
        self.ast = ast

    def render(self):
        output = ""
        for node in self.ast:
            if node[0] == "bold":
                output += f"<b>{node[1]}</b>"
            elif node[0] == "italic":
                output += f"<i>{node[1]}</i>"
        return output

text = "This is a *bold* text and this is an _italic_ text."
parser = MarkdownParser(text)
ast = parser.parse()
renderer = Renderer(ast)
output = renderer.render()
print(output)
'''