from dataclasses import dataclass
from typing import Any
from collections.abc import Iterator
from collections.abc import Generator
import re
from enum import Enum

type Hex = str | None
type Decoration = fg | bg | style
hex_regex: re.Pattern

palette: dict[str, Color]

class style(Enum):
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
    def all() -> None: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

@dataclass
class Color:
    r: int
    g: int
    b: int
    bg: bool
    def __post_init__(self) -> None: ...
    def __getitem__(self, index, /) -> int: ...
    def __iter__(self) -> Generator[int, None, None]: ...
    @property
    def ascii(self) -> str: ...
    @property
    def hex(self) -> str: ...
    def to_hsv(self) -> tuple[float, float, float]: ...
    @classmethod
    def from_hex(cls, hex_color_code: str) -> Color: ...
    def fade(
        self, steps: int = 10, start: Color | Hex = None, end: Color | Hex = None
    ) -> list[Color]: ...
    def interpolate(self, other: Color, ratio: float = 0.5) -> Color: ...
    @staticmethod
    def rainbow(num_colors) -> list[Color]: ...
    def __add__(self, other): ...
    def __sub__(self, other): ...
    def __len__(self): ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    def __hash__(self): ...
    def __gt__(self, other, /): ...
    def __lt__(self, other, /): ...

class ColorFactory:
    def __init_subclass__(cls, /, bg: bool = False, **kwargs): ...

class Parse:
    text: str
    styles: tuple
    def __init__(self, text: str, *styles: Decoration) -> None: ...
    def __str__(self) -> str: ...

class cprint(Parse):
    def __init__(self, text: str | Exception, *styles: Decoration, end="\n") -> None: ...
    @staticmethod
    def __call__(text: str | Exception, *styles: Decoration, end="\n") -> None: ...
    @staticmethod
    def debug(*text: str | Exception, end="\n") -> None: ...
    @staticmethod
    def success(*text: str | Exception, end="\n") -> None: ...
    @staticmethod
    def info(*text: str | Exception, end="\n") -> None: ...
    @staticmethod
    def warn(*text: str | Exception, end="\n") -> None: ...
    @staticmethod
    def error(*text: str | Exception, end="\n") -> None: ...
    def __repr__(self) -> str: ...

@dataclass
class fg(ColorFactory, bg=False):
    red: Color
    lightpink3: Color
    lightpink2: Color
    lightpink1: Color
    light_pink: Color
    pink: Color
    pink1: Color
    pink3: Color
    pink2: Color
    pink4: Color
    lavender_blush: Color
    maroon: Color
    hot_pink: Color
    purple: Color
    deeppink1: Color
    deeppink: Color
    deeppink2: Color
    maroon1: Color
    maroon2: Color
    maroon3: Color
    medium_violet_red: Color
    maroon4: Color
    orchid: Color
    violet: Color
    dark_magenta: Color
    thistle: Color
    magenta2: Color
    plum: Color
    magenta: Color
    magenta3: Color
    medium_orchid: Color
    dark_violet: Color
    dark_orchid: Color
    purple4: Color
    purple3: Color
    purple2: Color
    blue_violet: Color
    purple1: Color
    medium_purple: Color
    blue4: Color
    lavender: Color
    blue2: Color
    navy: Color
    blue3: Color
    cornflower_blue: Color
    light_steel_blue: Color
    alice_blue: Color
    light_sky_blue: Color
    sky_blue: Color
    lightblue2: Color
    deep_sky_blue: Color
    lightblue1: Color
    light_blue: Color
    lightblue3: Color
    turquoise4: Color
    dark_turquoise: Color
    cyan4: Color
    light_cyan: Color
    cyan2: Color
    cyan: Color
    cyan3: Color
    azure: Color
    pale_turquoise: Color
    medium_turquoise: Color
    light_sea_green: Color
    turquoise: Color
    blue: Color
    aquamarine: Color
    medium_spring_green: Color
    spring_green: Color
    medium_sea_green: Color
    dark_sea_green: Color
    honeydew: Color
    green2: Color
    lime_green: Color
    pale_green: Color
    light_green: Color
    green4: Color
    dark_green: Color
    forest_green: Color
    green3: Color
    lawn_green: Color
    green: Color
    green_yellow: Color
    dark_olive_green: Color
    olive_drab: Color
    beige: Color
    light_yellow: Color
    ivory: Color
    light_goldenrod_yellow: Color
    dark_khaki: Color
    pale_goldenrod: Color
    khaki: Color
    gold2: Color
    gold3: Color
    gold: Color
    light_goldenrod: Color
    gold4: Color
    cornsilk: Color
    goldenrod: Color
    dark_goldenrod: Color
    yellow: Color
    floral_white: Color
    old_lace: Color
    wheat: Color
    orange3: Color
    orange4: Color
    orange: Color
    orange2: Color
    moccasin: Color
    papaya_whip: Color
    blanched_almond: Color
    tan: Color
    antique_white: Color
    burlywood: Color
    dark_orange: Color
    bisque: Color
    linen: Color
    peru: Color
    tan2: Color
    tan4: Color
    tan1: Color
    sandy_brown: Color
    seashell: Color
    sienna: Color
    light_salmon: Color
    orange_red: Color
    coral: Color
    dark_salmon: Color
    tomato: Color
    salmon: Color
    gray11: Color
    gray73: Color
    gray84: Color
    gray36: Color
    gray35: Color
    gray51: Color
    gray92: Color
    gray21: Color
    gray3: Color
    dim_gray: Color
    gray1: Color
    gray80: Color
    gray9: Color
    black: Color
    gray33: Color
    gray53: Color
    gray48: Color
    gray24: Color
    gray29: Color
    gray44: Color
    gray78: Color
    gray52: Color
    gray91: Color
    gray50: Color
    gray64: Color
    gray25: Color
    gray14: Color
    gray94: Color
    gray26: Color
    gray38: Color
    gray95: Color
    gray12: Color
    gray40: Color
    gray54: Color
    gray70: Color
    gray81: Color
    gray47: Color
    gray82: Color
    gray69: Color
    gray46: Color
    gray45: Color
    gray49: Color
    gray2: Color
    gray97: Color
    gray67: Color
    gray34: Color
    gray93: Color
    gray57: Color
    gray96: Color
    gray66: Color
    gray79: Color
    gray28: Color
    gray75: Color
    gray20: Color
    gray71: Color
    gray17: Color
    gray72: Color
    gray74: Color
    gray18: Color
    gray39: Color
    gray7: Color
    gray4: Color
    red2: Color
    gray60: Color
    gray86: Color
    gray: Color
    gray58: Color
    gray83: Color
    gray61: Color
    gray62: Color
    gray42: Color
    dark_red: Color
    gray98: Color
    gray23: Color
    gray88: Color
    gray13: Color
    gray22: Color
    gray87: Color
    red3: Color
    gray15: Color
    gray99: Color
    gray8: Color
    gray90: Color
    gray30: Color
    gray85: Color
    gray77: Color
    gray56: Color
    gray31: Color
    light_gray: Color
    gray32: Color
    dark_gray: Color
    gray59: Color
    gray63: Color
    gray55: Color
    gray76: Color
    gray5: Color
    snow: Color
    gray19: Color
    gray43: Color
    gray37: Color
    gray6: Color
    gray68: Color
    gray27: Color
    gray10: Color
    light_coral: Color
    gray16: Color
    gray89: Color
    indian_red: Color
    @staticmethod
    def ls() -> None: ...

@dataclass
class bg(ColorFactory, bg=True):
    red: Color
    lightpink3: Color
    lightpink2: Color
    lightpink1: Color
    light_pink: Color
    pink: Color
    pink1: Color
    pink3: Color
    pink2: Color
    pink4: Color
    lavender_blush: Color
    maroon: Color
    hot_pink: Color
    purple: Color
    deeppink1: Color
    deeppink: Color
    deeppink2: Color
    maroon1: Color
    maroon2: Color
    maroon3: Color
    medium_violet_red: Color
    maroon4: Color
    orchid: Color
    violet: Color
    dark_magenta: Color
    thistle: Color
    magenta2: Color
    plum: Color
    magenta: Color
    magenta3: Color
    medium_orchid: Color
    dark_violet: Color
    dark_orchid: Color
    purple4: Color
    purple3: Color
    purple2: Color
    blue_violet: Color
    purple1: Color
    medium_purple: Color
    blue4: Color
    lavender: Color
    blue2: Color
    navy: Color
    blue3: Color
    cornflower_blue: Color
    light_steel_blue: Color
    alice_blue: Color
    light_sky_blue: Color
    sky_blue: Color
    lightblue2: Color
    deep_sky_blue: Color
    lightblue1: Color
    light_blue: Color
    lightblue3: Color
    turquoise4: Color
    dark_turquoise: Color
    cyan4: Color
    light_cyan: Color
    cyan2: Color
    cyan: Color
    cyan3: Color
    azure: Color
    pale_turquoise: Color
    medium_turquoise: Color
    light_sea_green: Color
    turquoise: Color
    blue: Color
    aquamarine: Color
    medium_spring_green: Color
    spring_green: Color
    medium_sea_green: Color
    dark_sea_green: Color
    honeydew: Color
    green2: Color
    lime_green: Color
    pale_green: Color
    light_green: Color
    green4: Color
    dark_green: Color
    forest_green: Color
    green3: Color
    lawn_green: Color
    green: Color
    green_yellow: Color
    dark_olive_green: Color
    olive_drab: Color
    beige: Color
    light_yellow: Color
    ivory: Color
    light_goldenrod_yellow: Color
    dark_khaki: Color
    pale_goldenrod: Color
    khaki: Color
    gold2: Color
    gold3: Color
    gold: Color
    light_goldenrod: Color
    gold4: Color
    cornsilk: Color
    goldenrod: Color
    dark_goldenrod: Color
    yellow: Color
    floral_white: Color
    old_lace: Color
    wheat: Color
    orange3: Color
    orange4: Color
    orange: Color
    orange2: Color
    moccasin: Color
    papaya_whip: Color
    blanched_almond: Color
    tan: Color
    antique_white: Color
    burlywood: Color
    dark_orange: Color
    bisque: Color
    linen: Color
    peru: Color
    tan2: Color
    tan4: Color
    tan1: Color
    sandy_brown: Color
    seashell: Color
    sienna: Color
    light_salmon: Color
    orange_red: Color
    coral: Color
    dark_salmon: Color
    tomato: Color
    salmon: Color
    gray11: Color
    gray73: Color
    gray84: Color
    gray36: Color
    gray35: Color
    gray51: Color
    gray92: Color
    gray21: Color
    gray3: Color
    dim_gray: Color
    gray1: Color
    gray80: Color
    gray9: Color
    black: Color
    gray33: Color
    gray53: Color
    gray48: Color
    gray24: Color
    gray29: Color
    gray44: Color
    gray78: Color
    gray52: Color
    gray91: Color
    gray50: Color
    gray64: Color
    gray25: Color
    gray14: Color
    gray94: Color
    gray26: Color
    gray38: Color
    gray95: Color
    gray12: Color
    gray40: Color
    gray54: Color
    gray70: Color
    gray81: Color
    gray47: Color
    gray82: Color
    gray69: Color
    gray46: Color
    gray45: Color
    gray49: Color
    gray2: Color
    gray97: Color
    gray67: Color
    gray34: Color
    gray93: Color
    gray57: Color
    gray96: Color
    gray66: Color
    gray79: Color
    gray28: Color
    gray75: Color
    gray20: Color
    gray71: Color
    gray17: Color
    gray72: Color
    gray74: Color
    gray18: Color
    gray39: Color
    gray7: Color
    gray4: Color
    red2: Color
    gray60: Color
    gray86: Color
    gray: Color
    gray58: Color
    gray83: Color
    gray61: Color
    gray62: Color
    gray42: Color
    dark_red: Color
    gray98: Color
    gray23: Color
    gray88: Color
    gray13: Color
    gray22: Color
    gray87: Color
    red3: Color
    gray15: Color
    gray99: Color
    gray8: Color
    gray90: Color
    gray30: Color
    gray85: Color
    gray77: Color
    gray56: Color
    gray31: Color
    light_gray: Color
    gray32: Color
    dark_gray: Color
    gray59: Color
    gray63: Color
    gray55: Color
    gray76: Color
    gray5: Color
    snow: Color
    gray19: Color
    gray43: Color
    gray37: Color
    gray6: Color
    gray68: Color
    gray27: Color
    gray10: Color
    light_coral: Color
    gray16: Color
    gray89: Color
    indian_red: Color

    @staticmethod
    def ls() -> None: ...
