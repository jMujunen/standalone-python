import re
import subprocess

ESCAPE_REGEX = re.compile(r"(\d+;?)+")


class Styler:
    """
    Class for colorizing command output using regular expressions.

    Attributes:
    ----------
        command (str): The command to be run.
        positional_arguments (str): Positional arguments for the command.
        flags (str): Flags for the command.

    Methods:
    ----------
        __init__(command, **kwargs): Init object
        styles(): Applies styles to the command
        body_style(pattern, color): Applies a style (color) to all instances of a specific pattern in the command
        run_command(): Runs the command and captures its output
        colorized_command_output(style): Returns the colorized command output
    """

    def __init__(self, command, **kwargs):
        # Initialization of the Styler object with a command and optional positional arguments or flags.
        self.command = command
        self._styles = []

        if not kwargs:
            self.positional_arguments = ""
            self.flags = ""
        else:
            for arg in kwargs.items():
                if arg[0] == "positional":
                    self.positional_arguments = "  ".join(arg[1])
                if arg[0] == "flags":
                    self.flags = "  ".join(arg[1])
        self.command_output = self.run_command()

    @property
    def styles(self):
        # Property for getting the list of styles applied to the command output.
        return self._styles

    def body_style(self, pattern, color):
        """
        Applies a style (color) to all instances of a specific pattern in the command output.

        Args:
        ----------
            pattern (str): The regular expression pattern for identifying text to style.
            color (Union[int, str]): The escape code or plain text representation of the desired color.

        Returns:
        ----------
            tuple: A tuple containing the compiled regex, prefix and suffix strings used for styling.
        """
        # TODO Add support for setting foreground and background colors with color codes as integers

        if ESCAPE_REGEX.match(str(color)):
            color_prefix = f"\033[{color}m"
        else:  # Option for using Color object and specifying color with plain text
            color_prefix = color

        color_suffix = "\033[0m"
        regex = re.compile(pattern)

        self._styles.append((regex, color_prefix, color_suffix))
        return (regex, color_prefix, color_suffix)

    def run_command(self):
        """
        Runs the command and captures its output.

        Returns:
        ----------
            str: The stdout of the command as a string. If stderr is not empty, it prints the error and exits with status 1.
        """

        command_output = subprocess.run(
            f"{self.command} {self.flags} {self.positional_arguments}",
            shell=True,
            capture_output=True,
            text=True,
        )
        if command_output.stderr:
            # print(command_output.stderr)
            # sys.exit(1)
            return self.command

        return command_output.stdout

    def sort(self, ignore_header=True):
        """
        Sorts the output of the command. Ignores the header during sorting and prepends it unless specified.

        Parameters:
        ----------
        ignore_header (bool): Specifies whether to ignore the header during sorting. Defaults to True.

        Returns:
        --------
            str: The sorted command output as a string.
        """
        rows = self.command_output.split("\n")
        # If specified, ignore the header during sorting, and prepend the header
        if ignore_header and len(rows) > 1:
            header = rows[0]
            rows = rows[1:]
            rows = sorted(rows)
            sorted_rows = [header] + rows

        else:
            sorted_rows = sorted(rows)
        return "\n".join(sorted_rows).replace("\n\n", "\n")

    def colorized_command_output(self, style):
        """
        Applies a list of styles to the command output and returns it.

        Args:
        ----------
            style (Union[tuple, list]): A tuple or list of tuples where each tuple contains a pattern and color code for styling text in the output.

        Returns:
        ----------
            str: The colorized version of the command's stdout. Each instance of the patterns in the style tuples are replaced with the corresponding color codes.
        """

        if not isinstance(style, list):
            style = [style]

        for s in style:
            regex, color_prefix, color_suffix = s
            matches = re.findall(regex, self.command_output)

            for match in matches:
                self.command_output = self.command_output.replace(
                    match, f"{color_prefix}{match}{color_suffix}"
                )

        return self.command_output
