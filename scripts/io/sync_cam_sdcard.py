#!/usr/bin/env python3

from fsutils.video import Video
from fsutils.img import Img
from fsutils.dir import Dir, obj
import argparse
import ctypes
import ctypes.util
import os
import shutil
import sys
from pathlib import Path
from Color import cprint, fg, bg, style

libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)

SRC = "/mnt/flash/DCIM/107D5600/"
IMG_DEST = "/mnt/ssd/Media/Photos/RAW"
VID_DEST = "/mnt/ssd/Media/Videos"


def mount(source: str, target: str, fs: str, options: str) -> int:
    """Mount a filesystem.

    Parameters
    -----------
        source (str): The source of the filesystem.
        target (str): The target directory to mount the filesystem on.
        fs (str): The type of filesystem to use.
        options (str): Options for mounting the filesystem.

    Returns
    ---------
        int: The return code of the mount call.
    """
    libc.mount.argtypes = (
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_ulong,
        ctypes.c_char_p,
    )

    ret = libc.mount(source.encode(), target.encode(), fs.encode(), 0, options.encode())
    if ret < 0:
        errno = ctypes.get_errno()
        if errno == 16:
            return ret
        raise OSError(
            errno,
            f"""Error mounting {source} ({fs}) on {target} with options {options}
            {os.strerror(errno)}""",
        )
    return ret


def umount(target: str) -> int:
    """Unmount a filesystem.

    Parameters
    -----------
        target (str): The target directory to unmount the filesystem from.

    Returns
    ---------
        int: The return code of the umount call.
    """
    libc.umount.argtypes = (ctypes.c_char_p,)
    ret = libc.umount(target.encode())
    if ret < 0:
        errno = ctypes.get_errno()
        raise OSError(
            errno,
            f"""Error unmounting {target}
            {os.strerror(errno)}""",
        )
    return ret


def get_dest(item: Video | Img, target: str) -> Path:
    """Categorize a file into the appropriate destination folder based on its type and creation date.

    Parameters
    ----------
        - item (File): The file object.
        - target (str): The target directory path.
        - sort_spec (str): The sorting specification, e.g., 'year', 'month', 'day'

    Returns
    -------
        - Path | None: The destination path for the file or None if it should be ignored.
    """
    match item.__class__.__name__:
        case "Img":
            return Path(
                target,
                item.capture_date.strftime("%Y/%h"),
                f"{item.capture_date.strftime('%Y-%m-%d_%H:%M:%S')}{item.suffix}",
            )
        case "Video":
            return Path(
                target,
                item.capture_date.strftime("%Y/%h"),
                f"{item.capture_date.strftime('%Y-%m-%d_%H:%M:%S')}{item.suffix}",
            )
        case _:
            raise TypeError(f"Unknown file type: {item.__class__.__name__}")


def main(refresh=False, remove=False) -> None:
    """Sync camera SD card with local storage.

    Parameters
    -----------
        refresh (bool): Refresh the destination index before syncing.
        remove (bool): Move files instead of copying.
    """
    src = Dir(SRC)
    img_dest = Dir(IMG_DEST)
    vid_dest = Dir(VID_DEST)

    # Create/update file indexes.
    src.serialize(replace=True)
    if refresh:
        img_dest.serialize(replace=True)
        vid_dest.serialize(replace=True)

    # Sync media files.
    for img in src.images():
        if img not in img_dest:
            dest = get_dest(img, img_dest.path)
            if not dest.parent.exists():
                dest.parent.mkdir(exist_ok=True, parents=True)

            shutil.move(img.path, img_dest, copy_function=shutil.copy2) if remove else shutil.copy2(
                img.path, dest
            )
            cprint(f"Moved {img.path} to {dest}", fg.green)
        else:
            cprint(f"Skipping {img.path}...", fg.yellow)

    for vid in src.videos():
        if vid not in vid_dest:
            dest = get_dest(vid, vid_dest.path)
            if not dest.parent.exists():
                dest.parent.mkdir(exist_ok=True, parents=True)
            shutil.move(vid.path, vid_dest, copy_function=shutil.copy2) if remove else shutil.copy2(
                vid.path, dest
            )
            cprint(f"Moved {vid.path} to {dest}", fg.green)
        else:
            cprint(f"Skipping {vid.path}...", fg.yellow)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync camera SD card with local storage")
    parser.add_argument(
        "--refresh", action="store_true", help="Refresh the destination index before syncing"
    )
    parser.add_argument("--remove", action="store_true", help="Move files instead of copying")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    mount("/dev/sdd1", "/mnt/flash", "exfat", "rw")
    cprint.info("Mounted /dev/sdd1 to /mnt/flash")
    main(args.refresh, args.remove)
    umount("/mnt/flash")
    cprint.info("Unmounted /mnt/flash")
