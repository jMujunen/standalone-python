#!/usr/bin/env python3
"""__init__.py - Initializes the hwdata package"""

from .GPU import GpuData
from .CPU import CpuData
from .FAN import Fan
from .DISK import Disk
from .SYS import Temp, RAM, Misc
from .NET import Interface

# from  .Proc import Proc

__all__ = [
    "GPU",
    "CPU",
    "FAN",
    "SYS",
    "NET",
    "DISK",
    # 'Proc',
]
