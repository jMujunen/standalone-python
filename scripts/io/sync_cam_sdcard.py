#!/usr/bin/env python3

import argparse
import ctypes
import ctypes.util
import os
import shutil
from pathlib import Path

from Color import cprint, fg
from fsutils.dir import Dir
from fsutils.img import Img
from fsutils.video import Video

libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)

SRC = "/mnt/flash/DCIM/107D5600/"
SRC2 = "/mnt/flash/DCIM/108D5600/"
IMG_DEST = "/mnt/hddred/MediaRoot/SERVER_MEDIA/RAW"
VID_DEST = "/mnt/hddred/MediaRoot/SERVER_MEDIA/Videos"


def mount(source: str, target: str, fs: str, options: str) -> int:
    """Mount a filesystem.

    Parameters
    -----------
        source (str): The source of the filesystem.
        target (str): The target directory to mount the filesystem on.
        fs (str): The type of filesystem to use.
        options (str): Options for mounting the filesystem.

    Returns:
    ---------
        int: The return code of the mount call.

    Raises:
    -------
        OSError: If the mount fails.

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

    Parameters:
    -----------
        target (str): The target directory to unmount the filesystem from.

    Returns:
    ---------
        int: The return code of the umount call.

    Raises:
    -------
        OSError: If an error occurs while unmounting the filesystem.
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
        item (File): The file object.
        target (str): The target directory path.
        sort_spec (str): The sorting specification, e.g., 'year', 'month', 'day'

    Returns:
    -------
        Path | None: The destination path for the file or None if it should be ignored.

    Raises:
    --------
       TypeError: If the item is not an instance of Video or Img.
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
            msg = f"Unknown file type: {item.__class__.__name__}"
            raise TypeError(msg)


def main(refresh=True, remove=False) -> None:
    """Sync camera SD card with local storage.

    Parameters
    -----------
        refresh (bool): Refresh the destination index before syncing.
        remove (bool): Move files instead of copying.
    """
    # src = Dir(SRC)
    src2 = Dir(SRC2)
    img_dest = Dir(IMG_DEST)
    vid_dest = Dir(VID_DEST)

    # Create/update file indexes.
    src2.serialize(replace=True)
    if refresh:
        img_dest.serialize(replace=True)
        vid_dest.serialize(replace=True)

    # Sync media files.
    for img in src2.images():
        if img not in img_dest:
            dest = get_dest(img, img_dest.path)
            if not dest.parent.exists():
                dest.parent.mkdir(exist_ok=True, parents=True)

            shutil.move(
                img.path,
                img_dest.path,
                copy_function=shutil.copy2,
            ) if remove else shutil.copy2(img.path, dest)
            # cprint(f"Moved {img.path} to {dest}", fg.green)
        else:
            cprint(f"Skipping {img.path}...", fg.yellow)

    for vid in src2.videos():
        if vid not in vid_dest:
            dest = get_dest(vid, vid_dest.path)
            if not dest.parent.exists():
                dest.parent.mkdir(exist_ok=True, parents=True)
            shutil.move(
                vid.path,
                vid_dest.path,
                copy_function=shutil.copy2,
            ) if remove else shutil.copy2(vid.path, dest)
            # cprint(f"Moved {vid.path} to {dest}", fg.green)
        else:
            cprint(f"Skipping {vid.path}...", fg.yellow)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync camera SD card with local storage",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "device",
        help="Device path of the SD card to sync",
        default="/dev/sdd1",
    )
    parser.add_argument(
        "--no-refresh",
        action="store_true",
        help="Dont recalculate destination index before syncing",
        default=False,
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Move files instead of copying",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    dev = args.device
    mount(dev, "/mnt/flash", "exfat", "rw")
    cprint.info("Mounted /dev/sdd1 to /mnt/flash")
    main(not args.no_refresh, args.remove)
    umount("/mnt/flash")
    cprint.info("Unmounted /mnt/flash")
