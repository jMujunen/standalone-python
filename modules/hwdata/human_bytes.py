#!/usr/bin/env python3

# human_bytes.py - Convert bytes to human readable format

# EG. human_size(1024) == '1.0KB'
# EG. human_size(1024 * 1024) == '1.0MB'
# EG. human_size(1024 * 1024 * 1024) == '1.0GB'
# EG. human_size(1024 * 1024 * 1024 * 1024) == '1.0TB'
def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n
def human_size(bytes, units=(' bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB')):
    """ Returns a human readable string reprentation of bytes"""
    return str(bytes) + ' ' + units[0] if bytes < 1024 else human_size(bytes >> 10, units[1:])
def percise_human_size(bytes):
    """ Returns a human readable string reprentation of bytes"""
    return str(bytes)
# Example usage
if __name__ == '__main__':
    print(human_size(1024 * 1024 * 1024 * 1024)) # 1 TB