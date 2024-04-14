#!/usr/bin/env python3

def convert_bytes(bytes):
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024**2:
        return f"{bytes / 1024:.2f} KB"
    elif bytes < 1024**3:
        return f"{bytes / (1024**2):.2f} MB"
    elif bytes < 1024**4:
        return f"{bytes / (1024**3):.2f} GB"
    else:
        return f"{bytes / (1024**4):.2f} TB"

