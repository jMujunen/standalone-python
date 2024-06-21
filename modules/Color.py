#!/usr/bin/env python
"""Higher level interface for printing colored text in the terminal.

This module utilizes metaclasses to create a higher level (and therefor) human readble interface for
printing colored text in the terminal. This is a significant improvement over printing raw escape codes.

Classes:
-------
    ColorMeta: The base metaclass for all color classes
    Style: Responsible for style changes
    BackgroundColor: Resposible for backround colors
    ForegroundColor: Resposible for foreground colors
    Parse: Parses the color classes into a single string

Functions:
---------
    cprint: Wrapper arond `print()` which provides a cleaner way of interfacing with this module.
    The alternative is to use print with f-strings or string concatenation which can be tedious to read.

Examples:
---------
    >>> print(f"{bg.red}Hello World{style.reset}")
    >>> cprint("This is bold and cyan", fg.cyan, style.bold)
"""


class ColorMeta(type):
    """Metaclass base for creating the interface for printing colored text in the terminal."""

    def __getattr__(self, item):
        return f"{self.STYLE[item]}"


class BackgroundColor(metaclass=ColorMeta):
    """
    Background color styler.

    Attributes:
    ----------
        STYLE (dict): Key, values where each key represents the corresponding escape code.
    """

    STYLE = {
        "black": "\033[40m",
        "red": "\033[41m",
        "green": "\033[42m",
        "yellow": "\033[43m",
        "blue": "\033[44m",
        "magenta": "\033[45m",
        "cyan": "\033[46m",
        "light_grey": "\033[47m",
        "dark_grey": "\033[100m",
        "light_red": "\033[101m",
        "light_green": "\033[102m",
        "light_yellow": "\033[103m",
        "light_blue": "\033[104m",
        "light_magenta": "\033[105m",
        "light_cyan": "\033[106m",
        "white": "\033[107m",
    }


class ForegroundColor(metaclass=ColorMeta):
    """
    Foreground color styler.

    Attributes:
    -----------
        STYLE (dict): Key, values where each key represents the corresponding escape code.
    """

    STYLE = {
        "aliceblue": "\033[38;2;240;248;255m",
        "antiquewhite": "\033[38;2;250;235;215m",
        "aqua": "\033[38;2;0;255;255m",
        "aquamarine": "\033[38;2;127;255;212m",
        "azure": "\033[38;2;240;255;255m",
        "beige": "\033[38;2;245;245;220m",
        "bisque": "\033[38;2;255;228;196m",
        "black": "\033[38;2;0;0;0m",
        "blanchedalmond": "\033[38;2;255;235;205m",
        "blue": "\033[34m",
        "blueviolet": "\033[38;2;138;43;226m",
        "brown": "\033[38;2;165;42;42m",
        "burlywood": "\033[38;2;222;184;135m",
        "cadetblue": "\033[38;2;95;158;160m",
        "chartreuse": "\033[38;2;127;255;0m",
        "chocolate": "\033[38;2;210;105;30m",
        "coral": "\033[38;2;255;127;80m",
        "cornflowerblue": "\033[38;2;100;149;237m",
        "cornsilk": "\033[38;2;255;248;220m",
        "crimson": "\033[38;2;220;20;60m",
        "cyan": "\033[36m",
        "darkblue": "\033[38;2;0;0;139m",
        "darkcyan": "\033[38;2;0;139;139m",
        "darkgoldenrod": "\033[38;2;184;134;11m",
        "darkgray": "\033[38;2;169;169;169m",
        "darkgreen": "\033[38;2;0;100;0m",
        "darkkhaki": "\033[38;2;189;183;107m",
        "darkmagenta": "\033[38;2;139;0;139m",
        "darkolivegreen": "\033[38;2;85;107;47m",
        "darkorange": "\033[38;2;255;140;0m",
        "darkorchid": "\033[38;2;153;50;204m",
        "darkred": "\033[38;2;139;0;0m",
        "darksalmon": "\033[38;2;233;150;122m",
        "darkseagreen": "\033[38;2;143;188;143m",
        "darkslateblue": "\033[38;2;72;61;139m",
        "darkslategray": "\033[38;2;47;79;79m",
        "darkturquoise": "\033[38;2;0;206;209m",
        "darkviolet": "\033[38;2;148;0;211m",
        "deeppink": "\033[38;2;255;20;147m",
        "deepskyblue": "\033[38;2;0;191;255m",
        "dimgray": "\033[38;2;105;105;105m",
        "dodgerblue": "\033[38;2;30;144;255m",
        "firebrick": "\033[38;2;178;34;34m",
        "floralwhite": "\033[38;2;255;250;240m",
        "forestgreen": "\033[38;2;34;139;34m",
        "fuchsia": "\033[38;2;255;0;255m",
        "gainsboro": "\033[38;2;220;220;220m",
        "ghostwhite": "\033[38;2;248;248;255m",
        "gold": "\033[38;2;255;215;0m",
        "goldenrod": "\033[38;2;218;165;32m",
        "gray": "\033[97m",
        "green": "\033[32m",
        "greenyellow": "\033[38;2;173;255;47m",
        "honeydew": "\033[38;2;240;255;240m",
        "hotpink": "\033[38;2;255;105;180m",
        "indianred": "\033[38;2;205;92;92m",
        "indigo": "\033[38;2;75;0;130m",
        "ivory": "\033[38;2;255;255;240m",
        "khaki": "\033[38;2;240;230;140m",
        "lavender": "\033[38;2;230;230;250m",
        "lavenderblush": "\033[38;2;255;240;245m",
        "lawngreen": "\033[38;2;124;252;0m",
        "lemonchiffon": "\033[38;2;255;250;205m",
        "lightblue": "\033[38;2;173;216;230m",
        "lightcoral": "\033[38;2;240;128;128m",
        "lightcyan": "\033[38;2;224;255;255m",
        "lightgoldenrodyellow": "\033[38;2;250;250;210m",
        "lightgray": "\033[38;2;211;211;211m",
        "lightgreen": "\033[38;2;144;238;144m",
        "lightpink": "\033[38;2;255;182;193m",
        "lightsalmon": "\033[38;2;255;160;122m",
        "lightseagreen": "\033[38;2;32;178;170m",
        "lightskyblue": "\033[38;2;135;206;250m",
        "lightyellow": "\033[38;2;255;255;224m",
        "lime": "\033[38;2;0;255;0m",
        "linen": "\033[38;2;250;240;230m",
        "magenta": "\033[35m",
        "maroon": "\033[38;2;128;0;0m",
        "mediumaquamarine": "\033[38;2;102;205;170m",
        "mediumorchid": "\033[38;2;186;85;211m",
        "mediumseagreen": "\033[38;2;60;179;113m",
        "mediumslateblue": "\033[38;2;123;104;238m",
        "mediumspringgreen": "\033[38;2;0;250;154m",
        "mediumvioletred": "\033[38;2;199;21;133m",
        "mintcrea": "\033[38;2;245;255;250m",
        "mistyrose": "\033[38;2;255;228;225m",
        "navajowhite": "\033[38;2;255;222;173m",
        "oldlace": "\033[38;2;253;245;230m",
        "olive": "\033[38;2;128;128;0m",
        "orange": "\033[38;2;255;165;0m",
        "orangered": "\033[38;2;255;69;0m",
        "palegoldenrod": "\033[38;2;238;232;170m",
        "palegreen": "\033[38;2;152;251;152m",
        "palevioletred": "\033[38;2;219;112;147m",
        "peru": "\033[38;2;205;133;63m",
        "plu": "\033[38;2;221;160;221m",
        "powderblue": "\033[38;2;176;224;230m",
        "purple": "\033[38;2;128;0;128m",
        "red": "\033[31m",
        "rosybrown": "\033[38;2;188;143;143m",
        "saddlebrown": "\033[38;2;139;69;19m",
        "salmon": "\033[38;2;250;128;114m",
        "sandybrown": "\033[38;2;244;164;96m",
        "seashell": "\033[38;2;255;245;238m",
        "silver": "\033[38;2;192;192;192m",
        "skyblue": "\\033[033m[\033[38;2;135;206;235mm",
        "slateblue": "\033[38;2;106;90;205m",
        "snow": "\033[38;2;255;250;250m",
        "steelblue": "\033[38;2;70;130;180m",
        "tan": "\033[38;2;210;180;140m",
        "teal": "\033[38;2;0;128;128m",
        "thistle": "\033[38;2;216;191;216m",
        "wheat": "\033[38;2;245;222;179m",
        "white": "\033[77m",
        "yellow": "\033[33m",
        "yellowgreen": "\033[38;2;154;205;50m",
    }


class Attributes(metaclass=ColorMeta):
    """
    Attribute styler.

    Attributes:
    ----------
        STYLE (dict): Key, values where each key represents the corresponding escape code.
    """

    STYLE = {
        "bold": "\033[1m",
        "faint": "\033[2m",
        "italic": "\033[3m",
        "underline": "\033[4m",
        "negative": "\033[7m",
        "strike": "\033[9m",
        "overline": "\033[53m",
        "double_underline": "\033[21m",
        "reset": "\033[0m",
    }


class style(Attributes):
    """
    Applys `style` text formatting.

    Methods:
    --------
        listall(): Prints all available attributes.
        showall(): Similar to listall() but it renders the style as well.

    Examples:
    -------
        >>> style.bold -> '\\033[1m'
        >>> style.underline -> '\\033[4m'
        >>> style.reset -> '\\033[0m'
        >>> print(f"{style.bold}This is bold text{style.reset}")

    """

    def listall():
        """Prints all available attributes."""
        print(" ".join(list(style.STYLE.keys())))

    def showall():
        """Similar to listall() but it renders the style as well."""
        for k, v in style.STYLE.items():
            print(f"{v}{k}", end=f"{style.reset}\t")
        return [v for v in style.STYLE.values()]


class fg(ForegroundColor):
    """
    Applys `fg` foreground formatting.

    Methods:
    --------
        listall(): Prints all available attributes.
        showall(): Similar to listall() but it renders the style as well.

    Examples:
    ---------
        >>> fg.red -> '\\033[31m'
        >>> fg.green -> '\\033[32m'
        >>> print(f"{fg.red}This is red text{style.reset}")
    """

    pass

    def listall():
        print(" ".join([k for k in fg.STYLE.keys()]))

    def showall():
        for k, v in fg.STYLE.items():
            print(f"{v}{k}", end=f"{style.reset}\t")
        return [v for v in fg.STYLE.values()]


class bg(BackgroundColor):
    """
    Applys `bg` foreground formatting.

    Methods:
    --------
        listall(): Prints all available attributes.
        showall(): Similar to listall() it renders the style as well.

    Examples:
    ---------
        >>> bg.red -> '\\033[41m'
        >>> bg.green -> '\\033[42m'
        >>> print(f"{bg.red}This is red text{style.reset}")
    """

    pass

    def listall():
        """Prints all available attributes."""

        print(" ".join([k for k in bg.STYLE.keys()]))

    def showall():
        """Similar to listall() but it renders the style as well."""
        yield (f"{v}{k}" for k, v in bg.STYLE.items())
        for k, v in bg.STYLE.items():
            print(f"{v}{k}", end=f"{style.reset}\t")

        return [v for v in bg.STYLE.values()]


class Parse:
    """
    Parses text with given styles.

    Methods:
    -------
        __init__(): Initializes the class with text and styles.
        __str__(): Returns the text with applied styles.
    """

    def __init__(self, text, *styles):
        """
        Initializes the class with text and styles.

        Parameters:
        -----------
            text (str): The text to be parsed with styles.
            styles (list): The styles to be applied to the text
        """
        self.text = text
        self.styles = styles

    def __str__(self):
        """
        Returns the text with applied styles.

        Returns:
        --------
            str: The text with applied styles.
        """
        styled_text = self.text
        for s in self.styles:
            styled_text = f"{s}{styled_text}{style.reset}"
        return styled_text


def cprint(text, *styles, end="\n"):
    """
    Prints the text with given styles.

    Parameters:
    ----------
        text (str): The text to be printed with styles.
        styles: The styles to be applied to the

    Example:
    -------
        >>> cprint('Hello, World!', fg.orange, style.bold)
    """
    print(str(Parse(text, *styles)), end=end)


# Example usage
if __name__ == "__main__":
    print(f"{fg.red}Hello, World!{style.reset}")
    cprint("Hello, World!", bg.red, style.italic)
    print(dir(fg))

    for s in style.STYLE.values():
        for foreground in fg.STYLE.values():
            print(f"{s}{foreground}HheEyY!{style.reset}", end="\t")
