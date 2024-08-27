#!/usr/bin/env python3


def size():
    import os

    env = os.environ

    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            import struct
            import os

            cr = struct.unpack("hh", fcntl.ioctl(fd, termios.TIOCGWINSZ, "1234"))
        except:
            return None
        return cr

    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (env["LINES"], env["COLUMNS"])
        except:
            cr = (25, 80)
    return int(cr[1]), int(cr[0])


if __name__ == "__main__":
    print(size)
