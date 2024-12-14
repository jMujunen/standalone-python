"""Higher level interface for printing colored text in the terminal.

This module utilizes metaclasses to create a higher level (and therefor) human readable interface for
printing colored text in the terminal. This is a significant improvement over printing raw escape codes.

Classes:
-------
    ColorMeta: The base metaclass for all color classes
    Style: Responsible for style changes
    BackgroundColor: Responsible for backround colors
    ForegroundColor: Responsible for foreground colors
    Parse: Parses the color classes into a single string

Functions:
---------
    cprint: Wrapper around `print()` which provides a cleaner way of interfacing with this module.
    The alternative is to use print with f-strings or string concatenation which can be tedious to read.

Examples
---------
    >>> print(f"{bg.red}Hello World{style.reset}")
    >>> cprint("This is bold and cyan", fg.cyan, style.bold)
"""

from dataclasses import dataclass, field
from typing import Any
from collections.abc import Iterator
from typing import ClassVar
from collections.abc import Callable
from collections.abc import Generator
import re
from enum import Enum

# RGB = namedtuple("RGB", ["r", "g", "b"], defaults=(0, 0, 0))

type Hex = str | None


hex_regex = re.compile(r"([ABCFEDabcdef-f0-9]{6})")


@dataclass
class Color:
    r: int = field(default_factory=int, init=True, compare=True, hash=True)
    g: int = field(default_factory=int, init=True, compare=True, hash=True)
    b: int = field(default_factory=int, init=True, compare=True, hash=True)
    # hex: Hex = field(default=None)

    def __post_init__(self):
        if isinstance(self.r, str) and len(self.r) == 6 and hex_regex.match(self.r):
            # Input is Hexadecimal color code
            self.r, self.g, self.b = self.from_hex(self.r)
        elif not all(isinstance(val, int) for val in self):
            raise ValueError("Invalid input type")
        # Clamp RGB values between 0 and 255
        self.r, self.g, self.b = (min(255, max(value, 0)) for value in self)

    def __getitem__(self, index, /):
        return (self.r, self.g, self.b)[index]

    def __iter__(self):
        yield from (self.r, self.g, self.b)

    @property
    def ascii(self) -> str:
        return "\033[38;2;{};{};{}m".format(*self)

    @property
    def hex(self) -> str:
        return "#{:02x}{:02x}{:02x}".format(*self)

    @classmethod
    def from_hex(cls, hex_color_code: str) -> "Color":
        """Create a Color object from hexadecimal color code.

        Parameters
            hex_color (str): The hexadecimal color code in format "#RRGGBB".

        Returns
            Color[r, g, b]: The RGB color.
        """
        hex_color_code = hex_color_code.lstrip("#")
        r, g, b = (
            int(*h)
            for h in ((hex_color_code[i : i + 2], 16) for i in range(0, len(hex_color_code), 2))
        )
        return cls(r, g, b)

    def fade(
        self, steps: int = 10, start: "Color | Hex" = None, end: "Color | Hex" = None
    ) -> list["Color"]:
        """Generate a list of hexadecimal color codes that transition smoothly
        from white (#FFFFFF) to the given color (hex_code) and then back to black (#000000).

        Parameters
        -----------
            hex_code (str): The target hexadecimal color code.
            steps (int, optional): Number of steps in the fade. Default is 10.
            start (str, optional): The starting color. Default is black ("FFFFFF").
            end (str, optional): The ending color. Default is white ("000000").

        Returns
        -------
            list[Color]: A list of hexadecimal color codes representing the fade.
        """
        match start, end:
            case str(), str():
                start = Color.from_hex(start)
                end = Color.from_hex(end)
            case str(), Color():
                start = Color.from_hex(start)
            case Color(), str():
                end = Color.from_hex(end)
            case _:
                start = Color(255, 255, 255)
                end = Color(0, 0, 0)

        def start_formula(base, end, i):
            return int(end + (base - end) * i / steps)

        fade_to_mid = (
            Color(
                start_formula(self.r, end.r, i),
                start_formula(self.g, end.g, i),
                start_formula(self.b, end.b, i),
            )
            for i in range(steps)
        )

        fade_from_mid = (
            Color(
                start_formula(self.r, start.r, i),
                start_formula(self.g, start.g, i),
                start_formula(self.b, start.b, i),
            )
            for i in range(steps)
        )
        # Combine the two fades, removing the duplicate mid color
        fade = *fade_to_mid, *fade_from_mid

        return sorted(fade, key=sum)

    def interpolate(self, other: "Color", ratio: float = 0.5) -> "Color":
        """Interpolate between two colors based on a given ratio.

        Parameters
            other (Color[r, g, b]): The second RGB color.
            ratio (float): The interpolation ratio (0.0 to 1.0).

        Returns
            Color[r, g, b]: The interpolated RGB color.
        """

        def formula(c1, c2):
            return int(c1 + (c2 - c1) * ratio)

        return Color(*map(formula, self, other))
        # return Color(formula(self.r, other.r), formula(self.g, other.g), formula(self.b, other.b))

    @staticmethod
    def generate_white_spectrum(num_colors) -> list["Color"]:
        colors = []
        for i in range(num_colors):
            # Calculate the RGB values based on position in the spectrum
            if i < num_colors / 3:
                r = int((255 / (num_colors / 3)) * i)
                g = 255
                b = 0
            elif i < 2 * num_colors / 3:
                r = 255
                g = int(255 - ((255 / (num_colors / 3)) * (i - num_colors / 3)))
                b = 0
            else:
                r = 255
                g = 0
                b = int((255 / (num_colors / 3)) * (i - 2 * num_colors / 3))
            colors.append(Color(r, g, b))
        return colors

    def __add__(self, other):
        return Color(*(a + b for a, b in zip(self, other, strict=False)))

    def __sub__(self, other):
        return Color(*(a - b for a, b in zip(self, other, strict=False)))

    def __len__(self):
        return len(self.__dict__)

    def __str__(self) -> str:
        return self.ascii

    def __repr__(self) -> str:
        return f'{f"Color({self.r}, {self.g}, {self.b})".ljust(25)} {self} {"▓" * 10}\033[0m'

    def __hash__(self):
        return hash((self.r, self.g, self.b))

    def __gt__(self, other, /):
        total = self.r + self.b + self.g
        return total > (other.r + other.b + other.g)

    def __lt__(self, other, /):
        total = self.r + self.g + self.b
        return total < (other.r + other.g + other.b)


class Parse:
    """Parses text with given styles."""

    text: str
    styles: tuple

    def __init__(self, text: str, *styles: list) -> None:
        """Initialize the class with text and styles.

        Parameters
        -----------
            text (str): The text to be parsed with styles.
            styles (list): The styles to be applied to the text
        """
        self.text = text
        self.styles = styles

    def __str__(self) -> str:
        """Return the text with applied styles.

        Returns
        --------
            str: The text with applied styles.
        """
        styled_text = self.text
        for s in self.styles:
            styled_text = f"{s}{styled_text}{style.reset}"
        return styled_text


@dataclass
class cprint(Parse):
    """Print the text with given styles."""

    def __init__(self, text: Any, *styles: Any, end="\n") -> None:
        """Initialize the class with text and styles."""
        self.text = str(text) if not isinstance(text, Exception) else text.args[0]
        self.styles = styles
        self(text, *styles, end=end)

    @staticmethod
    def __call__(text: Any, *styles: list, end="\n") -> None:
        print(Parse(text, *styles), end=end)

    @staticmethod
    def debug(*text: Any, end="\n") -> None:
        result = " ".join(map(str, text))
        print(Parse(f"{fg.orange}[DEBUG]{style.reset} - {result}"), end=end)

    @staticmethod
    def info(*text: Any, end="\n") -> None:
        result = " ".join(map(str, text))

        print(Parse(f"{fg.blue}[INFO]{style.reset} - {result}"), end=end)

    @staticmethod
    def warn(*text: Any, end="\n") -> None:
        result = " ".join(map(str, text))

        print(Parse(f"{fg.yellow}[WARN]{style.reset} - {result}"), end=end)

    @staticmethod
    def error(*text: Any, end="\n") -> None:
        result = " ".join(map(str, text))
        print(Parse(f"{fg.red}[ERROR]{style.reset} - {result}"), end=end)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(styles={self.styles}, text='{self.text}')"


@dataclass
class style:
    r"""Apply `style` text formatting.

    Methods
    --------
        listall(): Prints all available attributes.
        showall(): Similar to listall() but it renders the style as well.

    Examples
    -------
        >>> style.bold -> '\033[1m'
        >>> style.underline -> '\033[4m'
        >>> style.reset -> '\033[0m'
        >>> print(f"{style.bold}This is bold text{style.reset}")

    """

    bold: str = field(default="\033[1m")
    faint: str = field(default="\033[2m")
    italic: str = field(default="\033[3m")
    underline: str = field(default="\033[4m")
    negative: str = field(default="\033[7m")
    strike: str = field(default="\033[9m")
    overline: str = field(default="\033[53m")
    double_underline: str = field(default="\033[21m")
    reset: str = field(default="\033[0m")

    @staticmethod
    def all():
        """Return a list of all available attributes."""
        for k, v in style().__dict__.items():
            print(f"{v}{k}", end=f"{style.reset}\t")
            print()
        return list(style().__dict__.values())


class Palette(Enum):
    alice_blue = Color(240, 248, 255)
    antique_white = Color(250, 235, 215)
    antiquewhite1 = Color(255, 239, 219)
    antiquewhite2 = Color(238, 223, 204)
    antiquewhite3 = Color(205, 192, 176)
    antiquewhite4 = Color(139, 131, 120)
    aquamarine = Color(127, 255, 212)
    aquamarine2 = Color(118, 238, 198)
    aquamarine3 = Color(102, 205, 170)
    aquamarine4 = Color(69, 139, 116)
    azure = Color(240, 255, 255)
    azure2 = Color(224, 238, 238)
    azure3 = Color(193, 205, 205)
    azure4 = Color(131, 139, 139)
    beige = Color(245, 245, 220)
    bisque = Color(255, 228, 196)
    bisque2 = Color(238, 213, 183)
    bisque3 = Color(205, 183, 158)
    bisque4 = Color(139, 125, 107)
    black = Color(0, 0, 0)
    blanched_almond = Color(255, 235, 205)
    blue = Color(118, 168, 162)
    blue_violet = Color(138, 43, 226)
    blue2 = Color(0, 0, 238)
    blue3 = Color(0, 0, 205)
    blue4 = Color(0, 0, 139)
    brown = Color(165, 42, 42)
    brown1 = Color(255, 64, 64)
    brown2 = Color(238, 59, 59)
    brown3 = Color(205, 51, 51)
    brown4 = Color(139, 35, 35)
    burlywood = Color(222, 184, 135)
    burlywood1 = Color(255, 211, 155)
    burlywood2 = Color(238, 197, 145)
    burlywood3 = Color(205, 170, 125)
    burlywood4 = Color(139, 115, 85)
    cadet_blue = Color(95, 158, 160)
    cadetblue1 = Color(152, 245, 255)
    cadetblue2 = Color(142, 229, 238)
    cadetblue3 = Color(122, 197, 205)
    cadetblue4 = Color(83, 134, 139)
    chartreuse = Color(127, 255, 0)
    chartreuse2 = Color(118, 238, 0)
    chartreuse3 = Color(102, 205, 0)
    chartreuse4 = Color(69, 139, 0)
    chocolate = Color(210, 105, 30)
    chocolate1 = Color(255, 127, 36)
    chocolate2 = Color(238, 118, 33)
    chocolate3 = Color(205, 102, 29)
    chocolate4 = Color(139, 69, 19)
    coral = Color(255, 127, 80)
    coral1 = Color(255, 114, 86)
    coral2 = Color(238, 106, 80)
    coral3 = Color(205, 91, 69)
    coral4 = Color(139, 62, 47)
    cornflower_blue = Color(100, 149, 237)
    cornsilk = Color(255, 248, 220)
    cornsilk2 = Color(238, 232, 205)
    cornsilk3 = Color(205, 200, 177)
    cornsilk4 = Color(139, 136, 120)
    cyan = Color(0, 255, 255)
    cyan2 = Color(0, 238, 238)
    cyan3 = Color(0, 205, 205)
    cyan4 = Color(0, 139, 139)
    dark_goldenrod = Color(184, 134, 11)
    dark_gray = Color(169, 169, 169)
    dark_green = Color(0, 100, 0)
    dark_khaki = Color(189, 183, 107)
    dark_magenta = Color(139, 0, 139)
    dark_olive_green = Color(85, 107, 47)
    dark_orange = Color(255, 140, 0)
    dark_orchid = Color(153, 50, 204)
    dark_red = Color(139, 0, 0)
    dark_salmon = Color(233, 150, 122)
    dark_sea_green = Color(143, 188, 143)
    dark_slate_blue = Color(72, 61, 139)
    dark_slate_gray = Color(47, 79, 79)
    dark_turquoise = Color(0, 206, 209)
    dark_violet = Color(148, 0, 211)
    darkgoldenrod1 = Color(255, 185, 15)
    darkgoldenrod2 = Color(238, 173, 14)
    darkgoldenrod3 = Color(205, 149, 12)
    darkgoldenrod4 = Color(139, 101, 8)
    darkolivegreen1 = Color(202, 255, 112)
    darkolivegreen2 = Color(188, 238, 104)
    darkolivegreen3 = Color(162, 205, 90)
    darkolivegreen4 = Color(110, 139, 61)
    darkorange1 = Color(255, 127, 0)
    darkorange2 = Color(238, 118, 0)
    darkorange3 = Color(205, 102, 0)
    darkorange4 = Color(139, 69, 0)
    darkorchid1 = Color(191, 62, 255)
    darkorchid2 = Color(178, 58, 238)
    darkorchid3 = Color(154, 50, 205)
    darkorchid4 = Color(104, 34, 139)
    darkseagreen1 = Color(193, 255, 193)
    darkseagreen2 = Color(180, 238, 180)
    darkseagreen3 = Color(155, 205, 155)
    darkseagreen4 = Color(105, 139, 105)
    darkslategray1 = Color(151, 255, 255)
    darkslategray2 = Color(141, 238, 238)
    darkslategray3 = Color(121, 205, 205)
    darkslategray4 = Color(82, 139, 139)
    debianred = Color(215, 7, 81)
    deep_pink = Color(255, 20, 147)
    deep_sky_blue = Color(0, 191, 255)
    deeppink = Color(238, 18, 137)
    deeppink1 = Color(205, 16, 118)
    deeppink2 = Color(139, 10, 80)
    deepskyblue2 = Color(0, 178, 238)
    deepskyblue3 = Color(0, 154, 205)
    deepskyblue4 = Color(0, 104, 139)
    dim_gray = Color(105, 105, 105)
    dodger_blue = Color(30, 144, 255)
    dodgerblue2 = Color(28, 134, 238)
    dodgerblue3 = Color(24, 116, 205)
    dodgerblue4 = Color(16, 78, 139)
    firebrick = Color(178, 34, 34)
    firebrick1 = Color(255, 48, 48)
    firebrick2 = Color(238, 44, 44)
    firebrick3 = Color(205, 38, 38)
    firebrick4 = Color(139, 26, 26)
    floral_white = Color(255, 250, 240)
    forest_green = Color(34, 139, 34)
    gainsboro = Color(220, 220, 220)
    ghost_white = Color(248, 248, 255)
    gold = Color(255, 215, 0)
    gold2 = Color(238, 201, 0)
    gold3 = Color(205, 173, 0)
    gold4 = Color(139, 117, 0)
    goldenrod = Color(218, 165, 32)
    goldenrod1 = Color(255, 193, 37)
    goldenrod2 = Color(238, 180, 34)
    goldenrod3 = Color(205, 155, 29)
    goldenrod4 = Color(139, 105, 20)
    gray = Color(190, 190, 190)
    gray1 = Color(3, 3, 3)
    gray10 = Color(26, 26, 26)
    gray100 = Color(255, 255, 255)
    gray11 = Color(28, 28, 28)
    gray12 = Color(31, 31, 31)
    gray13 = Color(33, 33, 33)
    gray14 = Color(36, 36, 36)
    gray15 = Color(38, 38, 38)
    gray16 = Color(41, 41, 41)
    gray17 = Color(43, 43, 43)
    gray18 = Color(46, 46, 46)
    gray19 = Color(48, 48, 48)
    gray2 = Color(5, 5, 5)
    gray20 = Color(51, 51, 51)
    gray21 = Color(54, 54, 54)
    gray22 = Color(56, 56, 56)
    gray23 = Color(59, 59, 59)
    gray24 = Color(61, 61, 61)
    gray25 = Color(64, 64, 64)
    gray26 = Color(66, 66, 66)
    gray27 = Color(69, 69, 69)
    gray28 = Color(71, 71, 71)
    gray29 = Color(74, 74, 74)
    gray3 = Color(8, 8, 8)
    gray30 = Color(77, 77, 77)
    gray31 = Color(79, 79, 79)
    gray32 = Color(82, 82, 82)
    gray33 = Color(84, 84, 84)
    gray34 = Color(87, 87, 87)
    gray35 = Color(89, 89, 89)
    gray36 = Color(92, 92, 92)
    gray37 = Color(94, 94, 94)
    gray38 = Color(97, 97, 97)
    gray39 = Color(99, 99, 99)
    gray4 = Color(10, 10, 10)
    gray40 = Color(102, 102, 102)
    gray42 = Color(107, 107, 107)
    gray43 = Color(110, 110, 110)
    gray44 = Color(112, 112, 112)
    gray45 = Color(115, 115, 115)
    gray46 = Color(117, 117, 117)
    gray47 = Color(120, 120, 120)
    gray48 = Color(122, 122, 122)
    gray49 = Color(125, 125, 125)
    gray5 = Color(13, 13, 13)
    gray50 = Color(127, 127, 127)
    gray51 = Color(130, 130, 130)
    gray52 = Color(133, 133, 133)
    gray53 = Color(135, 135, 135)
    gray54 = Color(138, 138, 138)
    gray55 = Color(140, 140, 140)
    gray56 = Color(143, 143, 143)
    gray57 = Color(145, 145, 145)
    gray58 = Color(148, 148, 148)
    gray59 = Color(150, 150, 150)
    gray6 = Color(15, 15, 15)
    gray60 = Color(153, 153, 153)
    gray61 = Color(156, 156, 156)
    gray62 = Color(158, 158, 158)
    gray63 = Color(161, 161, 161)
    gray64 = Color(163, 163, 163)
    gray65 = Color(166, 166, 166)
    gray66 = Color(168, 168, 168)
    gray67 = Color(171, 171, 171)
    gray68 = Color(173, 173, 173)
    gray69 = Color(176, 176, 176)
    gray7 = Color(18, 18, 18)
    gray70 = Color(179, 179, 179)
    gray71 = Color(181, 181, 181)
    gray72 = Color(184, 184, 184)
    gray73 = Color(186, 186, 186)
    gray74 = Color(189, 189, 189)
    gray75 = Color(191, 191, 191)
    gray76 = Color(194, 194, 194)
    gray77 = Color(196, 196, 196)
    gray78 = Color(199, 199, 199)
    gray79 = Color(201, 201, 201)
    gray8 = Color(20, 20, 20)
    gray80 = Color(204, 204, 204)
    gray81 = Color(207, 207, 207)
    gray82 = Color(209, 209, 209)
    gray83 = Color(212, 212, 212)
    gray84 = Color(214, 214, 214)
    gray85 = Color(217, 217, 217)
    gray86 = Color(219, 219, 219)
    gray87 = Color(222, 222, 222)
    gray88 = Color(224, 224, 224)
    gray89 = Color(227, 227, 227)
    gray9 = Color(23, 23, 23)
    gray90 = Color(229, 229, 229)
    gray91 = Color(232, 232, 232)
    gray92 = Color(235, 235, 235)
    gray93 = Color(237, 237, 237)
    gray94 = Color(240, 240, 240)
    gray95 = Color(242, 242, 242)
    gray96 = Color(245, 245, 245)
    gray97 = Color(247, 247, 247)
    gray98 = Color(250, 250, 250)
    gray99 = Color(252, 252, 252)
    green = Color(139, 162, 110)
    green_yellow = Color(173, 255, 47)
    green2 = Color(0, 238, 0)
    green3 = Color(0, 205, 0)
    green4 = Color(0, 139, 0)

    honeydew = Color(240, 255, 240)
    honeydew2 = Color(224, 238, 224)
    honeydew3 = Color(193, 205, 193)
    honeydew4 = Color(131, 139, 131)
    hot_pink = Color(255, 105, 180)
    hotpink1 = Color(255, 110, 180)
    hotpink2 = Color(238, 106, 167)
    hotpink3 = Color(205, 96, 144)
    hotpink4 = Color(139, 58, 98)
    indian_red = Color(205, 92, 92)
    indianred1 = Color(255, 106, 106)
    indianred2 = Color(238, 99, 99)
    indianred3 = Color(205, 85, 85)
    indianred4 = Color(139, 58, 58)
    ivory = Color(255, 255, 240)
    ivory2 = Color(238, 238, 224)
    ivory3 = Color(205, 205, 193)
    ivory4 = Color(139, 139, 131)
    khaki = Color(240, 230, 140)
    khaki1 = Color(255, 246, 143)
    khaki2 = Color(238, 230, 133)
    khaki3 = Color(205, 198, 115)
    khaki4 = Color(139, 134, 78)
    lavender = Color(230, 230, 250)
    lavender_blush = Color(255, 240, 245)
    lavenderblush2 = Color(238, 224, 229)
    lavenderblush3 = Color(205, 193, 197)
    lavenderblush4 = Color(139, 131, 134)
    lawn_green = Color(124, 252, 0)
    lemon_chiffon = Color(255, 250, 205)
    lemonchiffon2 = Color(238, 233, 191)
    lemonchiffon3 = Color(205, 201, 165)
    lemonchiffon4 = Color(139, 137, 112)
    light_blue = Color(173, 216, 230)
    light_coral = Color(240, 128, 128)
    light_cyan = Color(224, 255, 255)
    light_goldenrod = Color(238, 221, 130)
    light_goldenrod_yellow = Color(250, 250, 210)
    light_gray = Color(211, 211, 211)
    light_green = Color(144, 238, 144)
    light_pink = Color(255, 182, 193)
    light_salmon = Color(255, 160, 122)
    light_sea_green = Color(32, 178, 170)
    light_sky_blue = Color(135, 206, 250)
    light_slate_blue = Color(132, 112, 255)
    light_slate_gray = Color(119, 136, 153)
    light_steel_blue = Color(176, 196, 222)
    light_yellow = Color(255, 255, 224)
    lightblue1 = Color(191, 239, 255)
    lightblue2 = Color(178, 223, 238)
    lightblue3 = Color(154, 192, 205)
    lightblue4 = Color(104, 131, 139)
    lightcyan2 = Color(209, 238, 238)
    lightcyan3 = Color(180, 205, 205)
    lightcyan4 = Color(122, 139, 139)
    lightgoldenrod1 = Color(255, 236, 139)
    lightgoldenrod2 = Color(238, 220, 130)
    lightgoldenrod3 = Color(205, 190, 112)
    lightgoldenrod4 = Color(139, 129, 76)
    lightpink1 = Color(255, 174, 185)
    lightpink2 = Color(238, 162, 173)
    lightpink3 = Color(205, 140, 149)
    lightpink4 = Color(139, 95, 101)
    lightsalmon2 = Color(238, 149, 114)
    lightsalmon3 = Color(205, 129, 98)
    lightsalmon4 = Color(139, 87, 66)
    lightskyblue1 = Color(176, 226, 255)
    lightskyblue2 = Color(164, 211, 238)
    lightskyblue3 = Color(141, 182, 205)
    lightskyblue4 = Color(96, 123, 139)
    lightsteelblue1 = Color(202, 225, 255)
    lightsteelblue2 = Color(188, 210, 238)
    lightsteelblue3 = Color(162, 181, 205)
    lightsteelblue4 = Color(110, 123, 139)
    lightyellow2 = Color(238, 238, 209)
    lightyellow3 = Color(205, 205, 180)
    lightyellow4 = Color(139, 139, 122)
    lime_green = Color(50, 205, 50)
    linen = Color(250, 240, 230)
    magenta = Color(255, 0, 255)
    magenta2 = Color(238, 0, 238)
    magenta3 = Color(205, 0, 205)
    maroon = Color(176, 48, 96)
    maroon1 = Color(255, 52, 179)
    maroon2 = Color(238, 48, 167)
    maroon3 = Color(205, 41, 144)
    maroon4 = Color(139, 28, 98)
    medium_orchid = Color(186, 85, 211)
    medium_purple = Color(147, 112, 219)
    medium_sea_green = Color(60, 179, 113)
    medium_slate_blue = Color(123, 104, 238)
    medium_spring_green = Color(0, 250, 154)
    medium_turquoise = Color(72, 209, 204)
    medium_violet_red = Color(199, 21, 133)
    mediumorchid1 = Color(224, 102, 255)
    mediumorchid2 = Color(209, 95, 238)
    mediumorchid3 = Color(180, 82, 205)
    mediumorchid4 = Color(122, 55, 139)
    mediumpurple1 = Color(171, 130, 255)
    mediumpurple2 = Color(159, 121, 238)
    mediumpurple3 = Color(137, 104, 205)
    mediumpurple4 = Color(93, 71, 139)
    mistyrose2 = Color(238, 213, 210)
    mistyrose3 = Color(205, 183, 181)
    mistyrose4 = Color(139, 125, 123)
    moccasin = Color(255, 228, 181)
    navajo_white = Color(255, 222, 173)
    navajowhite2 = Color(238, 207, 161)
    navajowhite3 = Color(205, 179, 139)
    navajowhite4 = Color(139, 121, 94)
    navy = Color(0, 0, 128)
    old_lace = Color(253, 245, 230)
    olive_drab = Color(107, 142, 35)
    olivedrab1 = Color(192, 255, 62)
    olivedrab2 = Color(179, 238, 58)
    olivedrab3 = Color(154, 205, 50)
    olivedrab4 = Color(105, 139, 34)
    orange = Color(255, 165, 0)
    orange_red = Color(255, 69, 0)
    orange2 = Color(238, 154, 0)
    orange3 = Color(205, 133, 0)
    orange4 = Color(139, 90, 0)
    orangered2 = Color(238, 64, 0)
    orangered3 = Color(205, 55, 0)
    orangered4 = Color(139, 37, 0)
    orchid = Color(218, 112, 214)
    orchid1 = Color(255, 131, 250)
    orchid2 = Color(238, 122, 233)
    orchid3 = Color(205, 105, 201)
    orchid4 = Color(139, 71, 137)
    pale_goldenrod = Color(238, 232, 170)
    pale_green = Color(152, 251, 152)
    pale_turquoise = Color(175, 238, 238)
    pale_violet_red = Color(219, 112, 147)
    palegreen1 = Color(154, 255, 154)
    palegreen3 = Color(124, 205, 124)
    palegreen4 = Color(84, 139, 84)
    paleturquoise1 = Color(187, 255, 255)
    paleturquoise2 = Color(174, 238, 238)
    paleturquoise3 = Color(150, 205, 205)
    paleturquoise4 = Color(102, 139, 139)
    palevioletred1 = Color(255, 130, 171)
    palevioletred2 = Color(238, 121, 159)
    palevioletred3 = Color(205, 104, 137)
    palevioletred4 = Color(139, 71, 93)
    papaya_whip = Color(255, 239, 213)
    peach_puff = Color(255, 218, 185)
    peachpuff2 = Color(238, 203, 173)
    peachpuff3 = Color(205, 175, 149)
    peachpuff4 = Color(139, 119, 101)
    peru = Color(205, 133, 63)
    pink = Color(255, 192, 203)
    pink1 = Color(255, 181, 197)
    pink2 = Color(238, 169, 184)
    pink3 = Color(205, 145, 158)
    pink4 = Color(139, 99, 108)
    plum = Color(221, 160, 221)
    plum1 = Color(255, 187, 255)
    plum2 = Color(238, 174, 238)
    plum3 = Color(205, 150, 205)
    plum4 = Color(139, 102, 139)
    powder_blue = Color(176, 224, 230)
    purple = Color(174, 134, 155)
    purple1 = Color(155, 48, 255)
    purple2 = Color(145, 44, 238)
    purple3 = Color(125, 38, 205)
    purple4 = Color(85, 26, 139)
    red = Color(200, 118, 120)
    red2 = Color(238, 0, 0)
    red3 = Color(205, 0, 0)
    rosy_brown = Color(188, 143, 143)
    rosybrown1 = Color(255, 193, 193)
    rosybrown2 = Color(238, 180, 180)
    rosybrown3 = Color(205, 155, 155)
    rosybrown4 = Color(139, 105, 105)
    royal_blue = Color(65, 105, 225)
    royalblue1 = Color(72, 118, 255)
    royalblue2 = Color(67, 110, 238)
    royalblue3 = Color(58, 95, 205)
    royalblue4 = Color(39, 64, 139)
    salmon = Color(250, 128, 114)
    salmon1 = Color(255, 140, 105)
    salmon2 = Color(238, 130, 98)
    salmon3 = Color(205, 112, 84)
    salmon4 = Color(139, 76, 57)
    sandy_brown = Color(244, 164, 96)
    sea_green = Color(46, 139, 87)
    seagreen1 = Color(84, 255, 159)
    seagreen2 = Color(78, 238, 148)
    seagreen3 = Color(67, 205, 128)
    seashell = Color(255, 245, 238)
    seashell2 = Color(238, 229, 222)
    seashell3 = Color(205, 197, 191)
    seashell4 = Color(139, 134, 130)
    sienna = Color(160, 82, 45)
    sienna1 = Color(255, 130, 71)
    sienna2 = Color(238, 121, 66)
    sienna3 = Color(205, 104, 57)
    sienna4 = Color(139, 71, 38)
    sky_blue = Color(135, 206, 235)
    skyblue1 = Color(135, 206, 255)
    skyblue2 = Color(126, 192, 238)
    skyblue3 = Color(108, 166, 205)
    skyblue4 = Color(74, 112, 139)
    slate_blue = Color(106, 90, 205)
    slate_gray = Color(112, 128, 144)
    slateblue1 = Color(131, 111, 255)
    slateblue2 = Color(122, 103, 238)
    slateblue3 = Color(105, 89, 205)
    slateblue4 = Color(71, 60, 139)
    slategray1 = Color(198, 226, 255)
    slategray2 = Color(185, 211, 238)
    slategray3 = Color(159, 182, 205)
    slategray4 = Color(108, 123, 139)
    snow = Color(255, 250, 250)
    snow2 = Color(238, 233, 233)
    snow3 = Color(205, 201, 201)
    snow4 = Color(139, 137, 137)
    spring_green = Color(0, 255, 127)
    springgreen2 = Color(0, 238, 118)
    springgreen3 = Color(0, 205, 102)
    springgreen4 = Color(0, 139, 69)
    steel_blue = Color(70, 130, 180)
    steelblue1 = Color(99, 184, 255)
    steelblue2 = Color(92, 172, 238)
    steelblue3 = Color(79, 148, 205)
    steelblue4 = Color(54, 100, 139)
    tan = Color(210, 180, 140)
    tan1 = Color(255, 165, 79)
    tan2 = Color(238, 154, 73)
    tan4 = Color(139, 90, 43)
    thistle = Color(216, 191, 216)
    thistle1 = Color(255, 225, 255)
    thistle2 = Color(238, 210, 238)
    thistle3 = Color(205, 181, 205)
    thistle4 = Color(139, 123, 139)
    tomato = Color(255, 99, 71)
    tomato2 = Color(238, 92, 66)
    tomato3 = Color(205, 79, 57)
    tomato4 = Color(139, 54, 38)
    turquoise = Color(64, 224, 208)
    turquoise1 = Color(0, 245, 255)
    turquoise2 = Color(0, 229, 238)
    turquoise3 = Color(0, 197, 205)
    turquoise4 = Color(0, 134, 139)
    violet = Color(238, 130, 238)
    violet_red = Color(208, 32, 144)
    violetred1 = Color(255, 62, 150)
    violetred2 = Color(238, 58, 140)
    violetred3 = Color(205, 50, 120)
    violetred4 = Color(139, 34, 82)
    wheat = Color(245, 222, 179)
    wheat1 = Color(255, 231, 186)
    wheat2 = Color(238, 216, 174)
    wheat3 = Color(205, 186, 150)
    wheat4 = Color(139, 126, 102)
    yellow = Color(255, 213, 116)
    yellow2 = Color(238, 238, 0)
    yellow3 = Color(205, 205, 0)
    yellow4 = Color(139, 139, 0)

    def __init__(self, color: Color):
        self.color = color
        self.ascii = "\033[38;2;{};{};{}m".format(*self.color)
        self.hex = "#{:02x}{:02x}{:02x}".format(*self.color)

    @staticmethod
    def rainbow(num_colors) -> list["Color"]:
        colors = []
        for i in range(num_colors):
            # Calculate the RGB values based on position in the spectrum
            if i < num_colors / 3:
                r = int((255 / (num_colors / 3)) * i)
                g = 255
                b = 0
            elif i < 2 * num_colors / 3:
                r = 255
                g = int(255 - ((255 / (num_colors / 3)) * (i - num_colors / 3)))
                b = 0
            else:
                r = 255
                g = 0
                b = int((255 / (num_colors / 3)) * (i - 2 * num_colors / 3))
            colors.append(Color(r, g, b))
        return colors

    def __iter__(self) -> Iterator:
        return iter(self.__dict__.values())


@dataclass
class fg(Enum):
    r"""Apply `fg` foreground formatting.

    Methods
    --------
        listall(): Prints all available attributes.
        showall(): Similar to listall() but it renders the style as well.

    Examples
    ---------
        >>> fg.red -> '\033[31m'
        >>> fg.green -> '\033[32m'
        >>> print(f"{fg.red}This is red text{style.reset}")
    """

    @staticmethod
    def ls() -> list[str]:
        """Print all available attributes."""
        for k, v in fg.__dict__.items():
            if not k.startswith("__"):
                print(f"{v}{k}", end=f"{style.reset}\t")
                print()
        return list(filter(lambda x: not str(x).startswith("__"), fg.__dict__.values()))


@dataclass
class bg:
    r"""Apply background formatting.

    Methods
    --------
        listall(): Prints all available attributes.
        showall(): Similar to listall() it renders the style as well.

    Examples
    ---------
        >>> bg.red -> '\033[41m'
        >>> bg.green -> '\033[42m'
        >>> print(f"{bg.red}This is red text{style.reset}")
    """

    black: str = field(default="\033[40m")
    red: str = field(default="\033[41m")
    green: str = field(default="\033[42m")
    yellow: str = field(default="\033[43m")
    blue: str = field(default="\033[44m")
    magenta: str = field(default="\033[45m")
    cyan: str = field(default="\033[46m")
    light_grey: str = field(default="\033[47m")
    dark_grey: str = field(default="\033[100m")
    light_red: str = field(default="\033[101m")
    light_green: str = field(default="\033[102m")
    light_yellow: str = field(default="\033[103m")
    light_blue: str = field(default="\033[104m")
    light_magenta: str = field(default="\033[105m")
    light_cyan: str = field(default="\033[106m")
    white: str = field(default="\033[107m")

    @staticmethod
    def all() -> list[str]:
        """Similar to listall() but it renders the style as well."""
        for k, v in bg().__dict__.items():
            print(f"{v}{k}", end=f"{style.reset}\t")
            print()
        return list(bg().__dict__.values())


for item in Palette:
    setattr(fg, item.name, item.value)
