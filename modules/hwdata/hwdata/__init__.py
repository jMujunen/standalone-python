#!/usr/bin/env python3
"""__init__.py - Initializes the hwdata package"""

from ExecutionTimer import ExecutionTimer

with ExecutionTimer():
    from .GPU import GpuData
    from .CPU import CpuData
    from .FAN import Fan
    from .DISK import Disk
    from .SYS import Temp, RAM, Misc
    from .NET import Interface

# # from  .Proc import Proc

__all__ = [
    "GpuData",
    "CpuData",
    "Fan",
    "RAM",
    "Misc",
    "Interface",
    "Disk",
    "Temp",
    # 'Proc',
]

# print(GpuData().__doc__)
