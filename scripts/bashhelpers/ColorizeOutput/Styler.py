import subprocess
import re

class Styler:
    """
    Class for colorizing command output using regular expressions.
    """
    # TODO
    # - Add options for styling the header 
    # - Add options for styling by column

    def __init__(self, command, **kwargs):
        self.command = command
        self._styles = []
        # TODO 
        # ! Add support for flags and positional arguments
        if not kwargs:
            self.positional_arguments = ''
            self.flags = ''
        else:
            for arg in kwargs.items():
                if arg[0] == 'positional':
                    self.positional_arguments = ' '.join(arg[1])
                if arg[0] == 'flags':
                    self.flags = ' '.join(arg[1])
    @property
    def styles(self):
        return self._styles
    def set_style(self, pattern, color):
        # TODO
        # ---------------------------------------------------------------
        # ! Add support for setting foreground and background colors with
        #if not isinstance(color_code, tuple):
        #    fg = color_code
        #    bg = 30
        #for color in color_code:
        #        pass
        # ---------------------------------------------------------------
        regex = re.compile(pattern)
        color_prefix = f"\033[{color}m"
        color_suffix = "\033[0m"

        self._styles.append((regex, color_prefix, color_suffix))
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
            sys.exit(1)
        
        return command_output.stdout

    def colorized_command_output(self, style):
        command_output = self.run_command()
        if not isinstance(style, list):
            style = [style]
        for s in style:
            regex, color_prefix, color_suffix = s
            matches = re.findall(regex, command_output)
            for match in matches:
                command_output = command_output.replace(match, f'{color_prefix}{match}{color_suffix}')
                
        # else:
        #     regex, color_prefix, color_suffix = style

        #     matches = re.findall(regex, command_output)
        #     for match in matches:
        #         command_output = command_output.replace(match, f'{color_prefix}{match}{color_suffix}')

        return command_output
