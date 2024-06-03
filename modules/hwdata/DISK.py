#!/usr/bin/env python3

# Disk.py - Query disk information for HWINFO

import psutil
import shutil
import os
import sys

class Disk:
    def __init__(self, mountpoint, friendly_name=None):
        self.mountpoint = mountpoint
        self.friendly_name = friendly_name
    def percent_used(self):
        return psutil.disk_usage(self.mountpoint).percent

    def __str__(self):
        return str(
            f'{self.mountpoint} {self.friendly_name if self.friendly_name else ""}:\n'
            f'Percent used: {self.percent_used()}%\n'
        )

# Example
if __name__ == '__main__':
    ROOTFS = Disk('/', 'Root')
    HOME = Disk('/home/', 'Home')
    WD40_external= Disk('/mnt/hdd/', '4TB External')
    #SSD = Disk('/mnt/ssd/')
    print(ROOTFS)
    print(WD40_external)
    print(HOME)
    