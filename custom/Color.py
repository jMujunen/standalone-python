"""Higher level interface for printing colored text in the terminal.

This module utilizes metaclasses to create a higher level (and therefor) human readable interface for
printing colored text in the terminal. This is a significant improvement over printing raw escape codes.

Classes:
-------
    style: Responsible for style changes
    bg: Responsible for backround colors
    fg: Responsible for foreground colors

Functions:
---------
    cprint: Wrapper around `print()` which provides a clean way of interfacing with this module.
    The alternative is to use print with f-strings or string concatenation which can be tedious to read.

Examples
---------
    >>> print(f"{bg.red}Hello World{style.reset}")
    >>> cprint("This is bold and cyan", fg.cyan, style.bold)
"""

from dataclasses import dataclass, field
from collections.abc import Generator
import re
from enum import Enum
import colorsys

type Hex = str | None
type Decoration = fg | bg | style
hex_regex = re.compile(r"([ABCFEDabcdef-f0-9]{6})")


class style(Enum):
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

    reset = "\033[0m"
    bold = "\033[1m"
    dim = "\033[2m"
    italic = "\033[3m"
    underline = "\033[4m"
    blink = "\033[5m"
    reverse = "\033[7m"
    hidden = "\033[8m"
    double_underline = "\033[21m"
    overline = "\033[53m"
    strike = "\033[9m"

    @staticmethod
    def all() -> None:
        """Return a list of all available attributes."""
        for item in style:
            print(f"{item.name:<10} {item.value}", end=f"{style.reset}\t")

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"


@dataclass
class Color:
    r: int = field(default_factory=int, init=True, compare=True, hash=True)
    g: int = field(default_factory=int, init=True, compare=True, hash=True)
    b: int = field(default_factory=int, init=True, compare=True, hash=True)
    bg: bool = field(default=False, init=True, compare=True, hash=True, kw_only=True)

    def __post_init__(self) -> None:
        if isinstance(self.r, str) and len(self.r) == 6 and hex_regex.match(self.r):
            # Input is Hexadecimal color code
            self.r, self.g, self.b = self.from_hex(self.r)
        elif not all(isinstance(val, int) for val in self):
            raise ValueError("Invalid input type")
        # Clamp RGB values between 0 and 255
        self.r, self.g, self.b = (min(255, max(value, 0)) for value in self)

    def __getitem__(self, index: int, /) -> int:
        return (self.r, self.g, self.b)[index]

    def __iter__(self) -> Generator[int, None, None]:
        yield from (self.r, self.g, self.b)

    @property
    def ascii(self) -> str:
        return "\033[38;2;{};{};{}m".format(*self)

    @property
    def hex(self) -> str:
        return "#{:02x}{:02x}{:02x}".format(*self)

    def to_hsv(self) -> tuple[float, float, float]:
        return colorsys.rgb_to_hsv(self.r / 255.0, self.g / 255.0, self.b / 255.0)

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

    def __add__(self, other):
        return Color(*(a + b for a, b in zip(self, other, strict=False)))

    def __sub__(self, other):
        return Color(*(a - b for a, b in zip(self, other, strict=False)))

    def __len__(self):
        return len(self.__dict__)

    def __str__(self) -> str:
        return f"\033[{'48' if self.bg else '38'};2;{self.r};{self.g};{self.b}m"

    def __repr__(self) -> str:
        return f"{f'Color({self.r}, {self.g}, {self.b})'.ljust(20)} {self} {self.hex} \033[0m"

    def __hash__(self):
        return hash((self.r, self.g, self.b))

    def __gt__(self, other, /):
        total = self.r + self.b + self.g
        return total > (other.r + other.b + other.g)

    def __lt__(self, other, /):
        total = self.r + self.g + self.b
        return total < (other.r + other.g + other.b)


palette: dict[str, Color] = {
    "red": Color(200, 118, 120),
    "lightpink3": Color(139, 95, 101),
    "lightpink2": Color(205, 140, 149),
    "lightpink1": Color(238, 162, 173),
    "light_pink": Color(255, 182, 193),
    "pink": Color(255, 192, 203),
    "pink1": Color(255, 181, 197),
    "pink3": Color(205, 145, 158),
    "pink2": Color(238, 169, 184),
    "pink4": Color(139, 99, 108),
    "lavender_blush": Color(255, 240, 245),
    "maroon": Color(176, 48, 96),
    "hot_pink": Color(255, 105, 180),
    "purple": Color(174, 134, 155),
    "deeppink1": Color(205, 16, 118),
    "deeppink": Color(238, 18, 137),
    "deeppink2": Color(139, 10, 80),
    "maroon1": Color(255, 52, 179),
    "maroon2": Color(238, 48, 167),
    "maroon3": Color(205, 41, 144),
    "medium_violet_red": Color(199, 21, 133),
    "maroon4": Color(139, 28, 98),
    "orchid": Color(218, 112, 214),
    "violet": Color(238, 130, 238),
    "dark_magenta": Color(139, 0, 139),
    "thistle": Color(216, 191, 216),
    "magenta2": Color(238, 0, 238),
    "plum": Color(221, 160, 221),
    "magenta": Color(255, 0, 255),
    "magenta3": Color(205, 0, 205),
    "medium_orchid": Color(186, 85, 211),
    "dark_violet": Color(148, 0, 211),
    "dark_orchid": Color(153, 50, 204),
    "purple4": Color(85, 26, 139),
    "purple3": Color(125, 38, 205),
    "purple2": Color(145, 44, 238),
    "blue_violet": Color(138, 43, 226),
    "purple1": Color(155, 48, 255),
    "medium_purple": Color(147, 112, 219),
    "blue4": Color(0, 0, 139),
    "lavender": Color(230, 230, 250),
    "blue2": Color(0, 0, 238),
    "navy": Color(0, 0, 128),
    "blue3": Color(0, 0, 205),
    "cornflower_blue": Color(100, 149, 237),
    "light_steel_blue": Color(176, 196, 222),
    "alice_blue": Color(240, 248, 255),
    "light_sky_blue": Color(135, 206, 250),
    "sky_blue": Color(135, 206, 235),
    "lightblue2": Color(154, 192, 205),
    "deep_sky_blue": Color(0, 191, 255),
    "lightblue1": Color(178, 223, 238),
    "light_blue": Color(173, 216, 230),
    "lightblue3": Color(104, 131, 139),
    "turquoise4": Color(0, 134, 139),
    "dark_turquoise": Color(0, 206, 209),
    "cyan4": Color(0, 139, 139),
    "light_cyan": Color(224, 255, 255),
    "cyan2": Color(0, 238, 238),
    "cyan": Color(0, 255, 255),
    "cyan3": Color(0, 205, 205),
    "azure": Color(240, 255, 255),
    "pale_turquoise": Color(175, 238, 238),
    "medium_turquoise": Color(72, 209, 204),
    "light_sea_green": Color(32, 178, 170),
    "turquoise": Color(64, 224, 208),
    "blue": Color(118, 168, 162),
    "aquamarine": Color(127, 255, 212),
    "medium_spring_green": Color(0, 250, 154),
    "spring_green": Color(0, 255, 127),
    "medium_sea_green": Color(60, 179, 113),
    "dark_sea_green": Color(143, 188, 143),
    "honeydew": Color(240, 255, 240),
    "green2": Color(0, 238, 0),
    "lime_green": Color(50, 205, 50),
    "pale_green": Color(152, 251, 152),
    "light_green": Color(144, 238, 144),
    "green4": Color(0, 139, 0),
    "dark_green": Color(0, 100, 0),
    "forest_green": Color(34, 139, 34),
    "green3": Color(0, 205, 0),
    "lawn_green": Color(124, 252, 0),
    "green": Color(139, 162, 110),
    "green_yellow": Color(173, 255, 47),
    "dark_olive_green": Color(85, 107, 47),
    "olive_drab": Color(107, 142, 35),
    "beige": Color(245, 245, 220),
    "light_yellow": Color(255, 255, 224),
    "ivory": Color(255, 255, 240),
    "light_goldenrod_yellow": Color(250, 250, 210),
    "dark_khaki": Color(189, 183, 107),
    "pale_goldenrod": Color(238, 232, 170),
    "khaki": Color(240, 230, 140),
    "gold2": Color(238, 201, 0),
    "gold3": Color(205, 173, 0),
    "gold": Color(255, 215, 0),
    "light_goldenrod": Color(238, 221, 130),
    "gold4": Color(139, 117, 0),
    "cornsilk": Color(255, 248, 220),
    "goldenrod": Color(218, 165, 32),
    "dark_goldenrod": Color(184, 134, 11),
    "yellow": Color(255, 213, 116),
    "floral_white": Color(255, 250, 240),
    "old_lace": Color(253, 245, 230),
    "wheat": Color(245, 222, 179),
    "orange3": Color(205, 133, 0),
    "orange4": Color(139, 90, 0),
    "orange": Color(255, 165, 0),
    "orange2": Color(238, 154, 0),
    "moccasin": Color(255, 228, 181),
    "papaya_whip": Color(255, 239, 213),
    "blanched_almond": Color(255, 235, 205),
    "tan": Color(210, 180, 140),
    "antique_white": Color(250, 235, 215),
    "burlywood": Color(222, 184, 135),
    "dark_orange": Color(255, 140, 0),
    "bisque": Color(255, 228, 196),
    "linen": Color(250, 240, 230),
    "peru": Color(205, 133, 63),
    "tan2": Color(238, 154, 73),
    "tan4": Color(139, 90, 43),
    "tan1": Color(255, 165, 79),
    "sandy_brown": Color(244, 164, 96),
    "seashell": Color(255, 245, 238),
    "sienna": Color(160, 82, 45),
    "light_salmon": Color(255, 160, 122),
    "orange_red": Color(255, 69, 0),
    "coral": Color(255, 127, 80),
    "dark_salmon": Color(233, 150, 122),
    "tomato": Color(255, 99, 71),
    "salmon": Color(250, 128, 114),
    "gray11": Color(28, 28, 28),
    "gray73": Color(186, 186, 186),
    "gray84": Color(214, 214, 214),
    "gray36": Color(92, 92, 92),
    "gray35": Color(89, 89, 89),
    "gray51": Color(130, 130, 130),
    "gray92": Color(235, 235, 235),
    "gray21": Color(54, 54, 54),
    "gray3": Color(8, 8, 8),
    "dim_gray": Color(105, 105, 105),
    "gray1": Color(3, 3, 3),
    "gray80": Color(204, 204, 204),
    "gray9": Color(23, 23, 23),
    "black": Color(0, 0, 0),
    "gray33": Color(84, 84, 84),
    "gray53": Color(135, 135, 135),
    "gray48": Color(122, 122, 122),
    "gray24": Color(61, 61, 61),
    "gray29": Color(74, 74, 74),
    "gray44": Color(112, 112, 112),
    "gray78": Color(199, 199, 199),
    "gray52": Color(133, 133, 133),
    "gray91": Color(232, 232, 232),
    "gray50": Color(127, 127, 127),
    "gray64": Color(163, 163, 163),
    "gray25": Color(64, 64, 64),
    "gray14": Color(36, 36, 36),
    "gray94": Color(240, 240, 240),
    "gray26": Color(66, 66, 66),
    "gray38": Color(97, 97, 97),
    "gray95": Color(242, 242, 242),
    "gray12": Color(31, 31, 31),
    "gray40": Color(102, 102, 102),
    "gray54": Color(138, 138, 138),
    "gray70": Color(179, 179, 179),
    "gray81": Color(207, 207, 207),
    "gray47": Color(120, 120, 120),
    "gray82": Color(209, 209, 209),
    "gray69": Color(176, 176, 176),
    "gray46": Color(117, 117, 117),
    "gray45": Color(115, 115, 115),
    "gray49": Color(125, 125, 125),
    "gray2": Color(5, 5, 5),
    "gray97": Color(247, 247, 247),
    "gray67": Color(171, 171, 171),
    "gray34": Color(87, 87, 87),
    "gray93": Color(237, 237, 237),
    "gray57": Color(145, 145, 145),
    "gray96": Color(245, 245, 245),
    "gray66": Color(168, 168, 168),
    "gray79": Color(201, 201, 201),
    "gray28": Color(71, 71, 71),
    "gray75": Color(191, 191, 191),
    "gray20": Color(51, 51, 51),
    "gray71": Color(181, 181, 181),
    "gray17": Color(43, 43, 43),
    "gray72": Color(184, 184, 184),
    "gray74": Color(189, 189, 189),
    "gray18": Color(46, 46, 46),
    "gray39": Color(99, 99, 99),
    "gray7": Color(18, 18, 18),
    "gray4": Color(10, 10, 10),
    "red2": Color(238, 0, 0),
    "gray60": Color(153, 153, 153),
    "gray86": Color(219, 219, 219),
    "gray": Color(190, 190, 190),
    "gray58": Color(148, 148, 148),
    "gray83": Color(212, 212, 212),
    "gray61": Color(156, 156, 156),
    "gray62": Color(158, 158, 158),
    "gray42": Color(107, 107, 107),
    "dark_red": Color(139, 0, 0),
    "gray98": Color(250, 250, 250),
    "gray23": Color(59, 59, 59),
    "gray88": Color(224, 224, 224),
    "gray13": Color(33, 33, 33),
    "gray22": Color(56, 56, 56),
    "gray87": Color(222, 222, 222),
    "red3": Color(205, 0, 0),
    "gray15": Color(38, 38, 38),
    "gray99": Color(252, 252, 252),
    "gray8": Color(20, 20, 20),
    "gray90": Color(229, 229, 229),
    "gray30": Color(77, 77, 77),
    "gray85": Color(217, 217, 217),
    "gray77": Color(196, 196, 196),
    "gray56": Color(143, 143, 143),
    "gray31": Color(79, 79, 79),
    "light_gray": Color(211, 211, 211),
    "gray32": Color(82, 82, 82),
    "dark_gray": Color(169, 169, 169),
    "gray59": Color(150, 150, 150),
    "gray63": Color(161, 161, 161),
    "gray55": Color(140, 140, 140),
    "gray76": Color(194, 194, 194),
    "gray5": Color(13, 13, 13),
    "snow": Color(255, 250, 250),
    "gray19": Color(48, 48, 48),
    "gray43": Color(110, 110, 110),
    "gray37": Color(94, 94, 94),
    "gray6": Color(15, 15, 15),
    "gray68": Color(173, 173, 173),
    "gray27": Color(69, 69, 69),
    "gray10": Color(26, 26, 26),
    "light_coral": Color(240, 128, 128),
    "gray16": Color(41, 41, 41),
    "gray89": Color(227, 227, 227),
    "indian_red": Color(205, 92, 92),
    "gray65": Color(166, 166, 166),  # a6a6a6
}


class ColorFactory:
    def __init_subclass__(cls, /, bg: bool = False, **kwargs):
        super().__init_subclass__(**kwargs)
        for key, value in palette.items():
            setattr(cls, key, Color(*value, bg=bg))


@dataclass
class fg(ColorFactory, bg=False):
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
    def ls() -> None:
        """Print all available attributes."""
        for k, v in fg.__dict__.items():
            if not k.startswith("__"):
                print(f"{v}{k}", end=f"{style.reset}\t")
                print()


@dataclass
class bg(ColorFactory, bg=True):
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

    @staticmethod
    def ls() -> None:
        """Print all available attributes."""
        for k, v in bg.__dict__.items():
            if not k.startswith("__"):
                print(f"{v}{k}", end=f"{style.reset}\t")
                print()


class Parse:
    """Parses text with given styles."""

    text: str | Exception
    styles: tuple

    def __init__(self, text: str | Exception, *styles: Decoration) -> None:
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
        styled_text = repr(self.text) if isinstance(self.text, Exception) else self.text
        for s in self.styles:
            styled_text = f"{s}{styled_text}{style.reset}"
        return styled_text


class cprint(Parse):
    """Print the text with given styles."""

    def __init__(self, text: str | Exception, *styles: Decoration, end="\n") -> None:
        """Initialize the class with text and styles.

        Parameters
        -----------
            text (str): The text to be printed.
            styles (list): The styles to be applied to the text
            end (str): The end character to be used after printing the text.
        """
        self.text = str(text) if not isinstance(text, Exception) else text.args[0]
        self.styles = styles
        self(text, *styles, end=end)

    @staticmethod
    def __call__(text: str | Exception, *styles: Decoration, end="\n") -> None:
        """Print the text with given styles.

        Parameters
        -----------
            text (str): The text to be printed.
            *styles (list): The styles to be applied to the text
            end (str): The end character to be used after printing the text.
        """
        print(Parse(text, *styles), end=end)

    @staticmethod
    def debug(*text: str | Exception, end="\n") -> None:
        result = " ".join(map(str, text))
        print(Parse(f"{fg.orange}[DEBUG]{style.reset} - {result}"), end=end)  # type: ignore

    @staticmethod
    def success(*text: str | Exception, end="\n") -> None:
        result = " ".join(map(str, text))
        print(Parse(f"{fg.green}[DEBUG]{style.reset} - {result}"), end=end)  # type: ignore

    @staticmethod
    def info(*text: str | Exception, end="\n") -> None:
        result = " ".join(map(str, text))
        print(Parse(f"{fg.blue}[INFO]{style.reset} - {result}"), end=end)  # type: ignore

    @staticmethod
    def warn(*text: str | Exception, end="\n") -> None:
        result = " ".join(map(str, text))

        print(Parse(f"{fg.yellow}[WARN]{style.reset} - {result}"), end=end)  # type: ignore

    @staticmethod
    def error(*text: str | Exception, end="\n") -> None:
        result = " ".join(map(str, text))
        print(Parse(f"{fg.red}[ERROR]{style.reset} - {result}"), end=end)  # type: ignore

    def __repr__(self) -> str:
        enums: filter[Decoration] = filter(lambda x: isinstance(x, Enum), self.styles)
        colors: filter[Color] = filter(lambda x: isinstance(x, Color), self.styles)
        styles = *colors, *enums
        return f"{self.__class__.__name__}(styles={styles}, text='{self.text}')"
