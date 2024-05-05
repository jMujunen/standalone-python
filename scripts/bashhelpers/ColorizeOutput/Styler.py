import subprocess
import re

class Styler:
    """
    Class for colorizing command output using regular expressions.
    """

    def __init__(self, command, **kwargs):
        self.command = command
        if not kwargs:
            self.positional_arguments = ''
            self.flags = ''
        else:
            for arg in kwargs.items():
                if arg[0] == 'positional':
                    self.positional_arguments = ' '.join(arg[1])
                if arg[0] == 'flags':
                    self.flags = ' '.join(arg[1])

    def set_style(self, pattern, color_code):
        regex = re.compile(pattern)
        color_prefix = f"\033[{color_code}m"
        color_suffix = "\033[0m"
        return regex, color_prefix, color_suffix
        
    def run_command(self):
        command_output = subprocess.run(
            f'{self.command} {self.flags} {self.positional_arguments}',
            shell=True,
            capture_output=True,
            text=True
        )
        if command_output.stderr:
            print(command_output.stderr)
        else:
            return command_output.stdout

    def colorized_command_output(self, style):
        
        command_output = self.run_command()

        regex, color_prefix, color_suffix = style

        matches = re.findall(regex, command_output)
        for match in matches:
            command_output = command_output.replace(match, f'{color_prefix}{match}{color_suffix}')

        return command_output
