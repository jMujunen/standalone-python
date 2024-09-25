"""Reusable object for manipulating command output."""

import re
import subprocess
from typing import Any

ESCAPE_REGEX = re.compile(r"(\d+;?)+")
ORIGINAL_FORMAT_REGEX = re.compile(r"^([^\s]+(\s+))+")


class Styler:
    """
    Class for colorizing command output using regular expressions.

    Attributes:
    ----------
        `command` (str) : The command to be run.
        `positional_arguments` (str) : Positional arguments for the command.
        `flags` (str): Flags for the command.

    Methods:
    ----------
        `styles()` : Applies styles to the command
        `body_style(pattern, color)` : Applies a style (color) to all instances of a specific pattern in the command
        `run_command()` :  Runs the command and captures its output
        `colorized_command_output(style)` : # Returns the colorized command output
    """

    _styles: list[str]

    def __init__(self, command: str, *args: Any, skip_subprocess=False) -> None:
        """Initialize object with a command and optional positional arguments or flags."""
        self._styles = []
        self.command = command, *args
        if skip_subprocess is True:
            self.command_output = command
            return
        self.command_output = self.run_command(command, *args)

    @property
    def styles(self) -> list[str]:
        # Property for getting the list of styles applied to the command output.
        return self._styles

    def body_style(self, pattern: str, color: int | str) -> tuple[re.Pattern[str], str, str]:
        """
        Apply a style (color) to all instances of a specific pattern in the command output.

        Args:
        ----------
            - pattern (str): The regular expression pattern for identifying text to style.
            - color (Union[int, str]): The escape code or plain text representation of the desired color.

        Returns:
        ----------
            - tuple: A tuple containing the compiled regex, prefix and suffix strings used for styling.
        """
        # TODO Add support for setting foreground and background colors with color codes as integers

        color_prefix = f"\033[{color}m" if ESCAPE_REGEX.match(str(color)) else color
        color_suffix = "\033[0m"
        regex = re.compile(pattern)

        self._styles.append((regex, color_prefix, color_suffix))
        return (regex, str(color_prefix), "\033[0m")

    def run_command(self, prog, *args) -> str:
        """
        Run the command and captures its output.

        Returns:
        ----------
            - str: The stdout of the command as a string. If stderr is not empty, it prints the error and exits with status 1.
        """
        match args:
            case ["--help"]:
                return subprocess.run(
                    [prog, "--help"], check=False, text=True, capture_output=True
                ).stdout

        command_output = subprocess.run(
            self.command,
            capture_output=True,
            text=True,
            check=False,
        )
        if command_output.stderr:
            return command_output.stderr

        return command_output.stdout

    def sort(self, ignore_header=True) -> str:
        """Sort the output of the command.

        Parameters:
        ----------
            - ignore_header (bool): Specifies whether to ignore the header during sorting. Defaults to True.

        Returns:
        --------
            - str: The sorted command output as a string.
        """
        rows = self.command_output.split("\n")
        # If specified, ignore the header during sorting, and prepend the header
        if ignore_header and len(rows) > 1:
            header = rows[0]
            rows = rows[1:]
            rows = sorted(rows)
            sorted_rows = [header, *rows]

        else:
            sorted_rows = sorted(rows)
        self.command_output = "\n".join(sorted_rows).replace("\n\n", "\n")
        return self.command_output

    def colorized_command_output(
        self, style: list[tuple[re.Pattern[str], str, str]] | list[re.Pattern[str]]
    ) -> str:
        """
        Apply a list of styles to the command output and returns it.

        Args:
        ----------
            style (Union[tuple[re.Pattern, [str]]): A tuple or list of tuples where
            each tuplecontains a pattern and color code for styling text in the output.

        Returns:
        ----------
            str: The colorized version of the command's stdout. Each instance of
            the patterns in the style tuples are replaced with the corresponding color codes.
        """
        if not isinstance(style[0], tuple):
            style = [style]
        for s in style:
            regex, color_prefix, color_suffix = s
            matches = re.findall(regex, self.command_output)

            for match in matches:
                self.command_output = self.command_output.replace(
                    match, f"{color_prefix}{match}{color_suffix}"
                )

        return self.command_output

    def remove_by_regex(self, pattern: str) -> None:
        """
        Remove all instances of a specific regular expression pattern from the command output.

        Args:
        ------
            pattern (str): The regular expression pattern to be removed from the command output.
        """
        self.command_output = re.sub(pattern, "", self.command_output)

    def remove_by_column(self, column: int) -> None:
        """
        Remove a specific column from the command output.

        Args:
        ------
            column (int): The index of the column to be removed from the command output.
                          Columns are 0-indexed.
        """
        lines = self.command_output.split("\n")
        for i in range(len(lines)):
            line = lines[i].split()
            if column < len(line):
                del line[column]
            lines[i] = " ".join(line)
        self.command_output = "\n".join(lines)

    def remove_by_row(self, row: int | str) -> None:
        """Remove a specific row from the command output.

        Args:
        ------
            row (int): The index of the row to be removed from the command output.
                       Rows are 0-indexed.
        """
        lines = self.command_output.split("\n")
        if isinstance(row, int) and row < len(lines):
            del lines[row]
        elif isinstance(row, str):
            self.command_output = "\n".join([line for line in lines if row not in line])
            return
        self.command_output = "\n".join(lines)

    def style_column(self, column: int, color: int | str) -> None:
        """
        Apply a style (color) to all instances of a specific column in the command output.

        Args:
        ------
            column (int): The index of the column to be styled in the command output.
                          Columns are 0-indexed.
            color (Union[int, str]): The escape code or plain text representation of the desired color.
        """
        lines = self.command_output.split("\n")
        for i in range(len(lines)):
            line = lines[i].split()
            if column < len(line):
                color_prefix = f"\x1b[{color}m" if ESCAPE_REGEX.match(str(color)) else color
                color_suffix = "\033[0m"
                line[column] = f"{color_prefix}{line[column]}{color_suffix}"
            lines[i] = " ".join(line)
        self.command_output = "\n".join(lines)

    def style_row(self, row: int, color: int | str) -> None:
        """
        Apply a style (color) to all instances of a specific row in the command output.

        Args:
        ------
            row (int): The index of the row to be styled in the command output.
                       Rows are 0-indexed.
            color (Union[int, str]): The escape code or plain text representation of the desired color.
        """
        lines = self.command_output.split("\n")
        if row < len(lines):
            color_prefix = f"\x1b[{color}m" if ESCAPE_REGEX.match(str(color)) else color
            color_suffix = "\033[0m"
            lines[row] = f"{color_prefix}{lines[row]}{color_suffix}"
        self.command_output = "\n".join(lines)

    def __str__(self) -> str:
        return self.command_output

    def __repr__(self) -> str:
        return self.__class__.__name__ + "(command={command})".format(**vars(self))
