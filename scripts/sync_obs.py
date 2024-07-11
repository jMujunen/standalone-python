#!/usr/bin/env python3
"""This script mounts the windows ssd, compresses the OBS clips by outputting to local storage"""

import ctypes
import ctypes.util
import os
from sh import mount

from fsutils import Video, Dir

mount()
