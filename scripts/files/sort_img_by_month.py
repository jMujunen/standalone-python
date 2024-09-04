#!/usr/bin/env python3

# TODO
# - [ ] Improve performance by using multithreading/multiprocessing

import argparse
import os
import re
import shutil
import sys

from Color import bg, cprint, fg, style
from ExecutionTimer import ExecutionTimer
from fsutils import File, Git, Img, Log, Video, mimecfg
from fsutils.DirNode import Dir, obj
from ProgressBar import ProgressBar

SPECIAL_FILES = {
    re.compile(r"^(DSC|P_\d+|IMG-\d+)"): lambda output_dir, x: rename_file(output_dir, x),
    re.compile(r"^Screenshot"): lambda output_dir, x: screenshots(output_dir, x),
    re.compile(r"joona.and.ella"): lambda output_dir, x: wedding_photos(output_dir, x),
}

MIME = mimecfg.FILE_TYPES

SPECIAL_TAGS = {
    "original_format-eng": lambda x: x,
    "com.android.version": "andriod_phone",
    "com.apple.quicktime.make": "apple_phone",
    "comment": "dashcam",
}

JUNK_FILE_REGEX = re.compile(r"Abakus|.ico$")
JUNK = MIME["ignored"]


def rename_file(output_dir, image_object):
    # If no capture date is found, do nothing
    if not image_object.capture_date:
        return
    capture_date = str(image_object.capture_date).replace(" ", "_")
    capture_year = capture_date[:4]
    if capture_date:
        new_name = f"{capture_date}{image_object.extension}"
        new_path = os.path.join(output_dir, capture_year, new_name)
        return new_path
        # shutil.move(image_object.path, os.path.join(image_object.dir_name, new_name))


def wedding_photos(output_dir, image_object):
    wedding_photo_dir = os.path.join(output_dir, "Wedding")
    wedding_photo_path = os.path.join(wedding_photo_dir, image_object.basename)
    try:
        os.makedirs(wedding_photo_dir, exist_ok=True)
        return wedding_photo_path
        # shutil.move(image_object.path, wedding_photo_path)
    except Exception as e:
        cprint(
            f"Error moving Wedding photo from {image_object.path} -> {wedding_photo_path}: {e}",
            fg.reg,
            style.bold,
        )


def screenshots(output_dir, image_object):
    screenshots_dir = os.path.join(output_dir, "Screenshots")
    screenshot_path = os.path.join(screenshots_dir, image_object.basename)
    try:
        os.makedirs(screenshots_dir, exist_ok=True)
        return screenshot_path
        # shutil.move(image_object.path, screenshot_path)
    except Exception as e:
        cprint(
            f"""Error moving screenshots photo from {image_object.path} -> {screenshot_path}:
            {e}""",
            fg.reg,
            style.bold,
        )


def cleanup(input_dir):
    # Cleanup function to be called upon completion of script execution
    # Check to make sure no files are left behind and remove the Dir Dir tree
    print("\nCleaning up...")
    old_files = [file for root, dirs, files in os.walk(input_dir) for file in files]
    if not old_files:
        shutil.rmtree(input_dir)
        sys.exit("Cleanup completed successfully")
    else:
        print("Could not clean up: Files left behind")
        print("\n".join(old_files))
        sys.exit(1)


def rm_empty_folders(folder: str) -> None:
    # Remove empty folders from parent to child
    try:
        if not os.listdir(folder):
            os.rmdir(folder)
    except (FileNotFoundError, NotADirectoryError):
        pass


def process_file(file: File):
    if isinstance(file, Img):
        prefix = "Photos"
    elif isinstance(file, Video):
        prefix = "Videos"
    else:
        prefix = "Other"
    # Create a new directory in the output directory for each year of capture date
    target_dir = os.path.join(output_dir, f"{prefix}_{file.date.year}")
    os.makedirs(target_dir, exist_ok=True)

    # Move file to new directory based on the original capture date
    shutil.move(file.path, target_dir)
    print(f"Moved {file.basename} to {target_dir}")


def process_video(video: Video):
    tags = video.tags


def remove_item(file: File, other: File) -> None:
    pass
    # """Determine which file is the original and delete the duplicate"""
    # if isinstance(file, Img):
    #     # If the file is an image, compare the EXIF data
    #     if file.exif == other.exif:
    #         os.remove(other.path)
    #         print(f"Removed {other.basename} due to identical EXIF data")
    # elif isinstance(file, Video):
    #     # If the file is a video, compare the metadata
    #     if file.metadata == other.metadata:
    #         os.remove(other.path)
    #         print(f"Removed {other.basename} due to identical metadata")
    # else:
    #     # If the file is neither an image nor a video, delete it
    #     os.remove(other.path)
    #     print(f"Removed {other.basename} as it is neither an image nor a video


def parse_args():
    parser = argparse.ArgumentParser(
        description="Organize images into directories by year, based on the original capture date"
    )
    parser.add_argument("input", type=str, help="Path to the directory containing the images")
    parser.add_argument("output", type=str, help="Path to the output directory")
    return parser.parse_args()


def main(input_dir: str, output_dir: str):
    with ExecutionTimer():
        duplicates = []
        # Initialize objects and variables
        d = Dir(input_dir)
        num_items = len(d)
        removed = 0
        # Create a directory for the images without metadata
        os.makedirs(os.path.join(output_dir, "Videos", "Dashcam"), exist_ok=True)
        # os.makedirs(os.path.join(output_dir, "Videos", "NoMetaData"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "Videos", "Other"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "Videos", ""), exist_ok=True)
        with ProgressBar(num_items) as progress:
            # Iterate over all files in the directory
            for item in d.file_objects:
                progress.increment()
                if item.extension in JUNK or isinstance(item, Git):
                    os.remove(item.path)
                    continue
                # ============================ PHOTO =============================== #
                if item.is_image and isinstance(item, Img):
                    prefix = os.path.join(output_dir, "Photos")
                    if JUNK_FILE_REGEX.match(item.basename):
                        try:
                            os.remove(item.path)
                            removed += 1
                        except FileNotFoundError:
                            cprint(f"FileNotFound: Error removing {item.path}", fg.red)

                    try:
                        # Sort the images into directories by capture date year
                        # If the image does not have a capture date, move it to 'NoMetaData' directory
                        # and rename if necessary to avoid duplicates
                        if not item.capture_date:
                            # Move the file to 'NoMetaData' directory
                            os.makedirs(os.path.join(prefix, "NoMetaData"), exist_ok=True)
                            prefix = os.path.join(prefix, "NoMetaData")
                            no_meta_data_image = os.path.join(prefix, item.basename)
                            # Rename the file if it already exists in 'NoMetaData' directory
                            # to avoid duplicates
                            count = 0
                            while os.path.exists(no_meta_data_image):
                                other = Img(no_meta_data_image)
                                # If destination file is the same as source and is not corrupted, remove the source file and continue to next item
                                if not other.is_corrupt and other == item:
                                    remove_item(item, other)
                                count += 1
                                # Increment the count until we find a filename that does not exist yet
                                try:
                                    new_file_name = f"{item.basename[:-4]}_{count}{item.extension}"
                                    shutil.move(
                                        item.path,
                                        os.path.join(prefix, new_file_name),
                                        copy_function=shutil.copy2,
                                    )
                                    # If the new filename does not exist, break the loop and
                                    # continue execution with the new filename
                                    break
                                except Exception as e:
                                    cprint(e, fg.orange)
                                    continue
                            try:
                                # If the file does not exist in 'NoMetaData' directory yet, move it there
                                shutil.move(
                                    item.path,
                                    os.path.join(prefix, "NoMetaData", ""),
                                    copy_function=shutil.copy2,
                                )
                            except Exception as e:
                                cprint(e, fg.gray)
                        # Meta data found, move it to appropriate year subdirectory based
                        # on metadata date
                        else:
                            capture_year = str(item.capture_date.year)
                            output_file_path = os.path.join(
                                prefix, str(capture_year), item.basename
                            )
                            for regex, func in SPECIAL_FILES.items():
                                if regex.match(item.basename):
                                    output_file_path = func(prefix, item) or f".{output_file_path}"
                            # Check if the file already exists in the destination directory,
                            # if so increment a counter to create a unique name for it.
                            count = 0
                            while os.path.exists(output_file_path):
                                other = Img(output_file_path)
                                # If destination file is the same as source and is not corrupted, remove the source file and continue to next item
                                if not other.is_corrupt and other == item:
                                    remove_item(item, other)
                                    break
                                count += 1
                                try:
                                    filename = os.path.split(output_file_path)[-1][:-4]
                                    output_file_name = f"{filename}_{count}{item.extension}"
                                    output_file_path = os.path.join(
                                        prefix, capture_year, output_file_name
                                    )
                                    shutil.move(
                                        item.path,
                                        output_file_path,
                                        copy_function=shutil.copy2,
                                    )
                                    break
                                except Exception as e:
                                    cprint(e, fg.orange)
                                    continue
                            try:
                                os.makedirs(
                                    os.path.join(prefix, str(capture_year)),
                                    exist_ok=True,
                                )
                                shutil.move(
                                    item.path,
                                    output_file_path,
                                    copy_function=shutil.copy2,
                                )
                            except KeyboardInterrupt:
                                break
                            except (FileNotFoundError, NotADirectoryError):
                                pass
                            except Exception as e:
                                cprint(e, fg.deeppink)
                                continue
                    except TypeError as e:
                        cprint(e, fg.red)
                        try:
                            shutil.move(item.path, prefix)
                        except Exception as e:
                            cprint(f"FATAL ERROR: {e}:", bg.red, fg.black, style.underline)
                    except Exception as e:
                        cprint(e, fg.red)
                    rm_empty_folders(item.dir_name)
                # ============================ VIDEO =============================== #
                elif item.is_video and isinstance(item, Video):
                    prefix = os.path.join(output_dir, "Videos")
                    if not item.capture_date:
                        prefix = os.path.join(prefix, "NoMetaData")
                        os.makedirs(prefix, exist_ok=True)
                        no_meta_data_path = os.path.join(prefix, item.basename)
                        count = 0
                        while os.path.exists(no_meta_data_path):
                            if item == Video(no_meta_data_path):
                                duplicates.append(item.path)
                                break
                            count += 1
                            # Increment the count until we find a filename that does not exist yet
                            try:
                                new_file_name = f"{item.basename[:-4]}_{count}{item.extension}"
                                shutil.move(
                                    item.path,
                                    os.path.join(prefix, new_file_name),
                                    copy_function=shutil.copy2,
                                )
                                # If the new filename does not exist, break the loop and
                                # continue execution with the new filename
                                break
                            except Exception as e:
                                cprint(e, fg.orange)
                                count += 1
                                continue
                        try:
                            # If the file does not exist in 'NoMetaData' directory yet, move it there
                            shutil.move(
                                item.path,
                                os.path.join(prefix, "NoMetaData", ""),
                                copy_function=shutil.copy2,
                            )
                        except Exception as e:
                            cprint(e, fg.gray)
                            continue
                        # Meta data found, move it to appropriate year subdirectory based
                        # on metadata date
                    else:
                        capture_year = str(item.capture_date.year)
                        output_file_path = os.path.join(prefix, capture_year, item.basename)
                        # Check if the file already exists in the destination directory,
                        # if so increment a counter to create a unique name for it.
                        count = 0
                        while os.path.exists(output_file_path):
                            if item == Video(output_file_path):
                                duplicates.append(item.path)
                                break
                            count += 1
                            try:
                                filename = os.path.split(output_file_path)[-1][:-4]
                                output_file_name = f"{filename}_{count}{item.extension}"
                                output_file_path = os.path.join(
                                    prefix, capture_year, output_file_name
                                )
                                shutil.move(
                                    item.path,
                                    output_file_path,
                                    copy_function=shutil.copy2,
                                )
                                break
                            except Exception as e:
                                cprint(e, fg.orange)
                                count += 1
                        try:
                            os.makedirs(os.path.join(prefix, capture_year), exist_ok=True)
                            shutil.move(item.path, output_file_path, copy_function=shutil.copy2)
                        except KeyboardInterrupt:
                            break
                        except (FileNotFoundError, NotADirectoryError):
                            pass
                        except Exception as e:
                            cprint(e, fg.deeppink)
                            continue
                    rm_empty_folders(item.dir_name)
                # ============================ FILE =============================== #

                elif isinstance(item, Log):
                    if "hwinfo" in item.basename.lower():
                        os.makedirs(os.path.join(output_dir, "Logs", "hwinfo"), exist_ok=True)
                        prefix = os.path.join(output_dir, "Logs", "hwinfo")
                    elif "gpuz" in item.basename.lower():
                        os.makedirs(os.path.join(output_dir, "Logs", "gpuz"), exist_ok=True)
                        prefix = os.path.join(output_dir, "Logs", "gpuz")
                    else:
                        os.makedirs(os.path.join(output_dir, "Logs"), exist_ok=True)
                        prefix = os.path.join(output_dir, "Logs")
                    output_file_path = os.path.join(prefix, item.basename)
                    count = 0
                    while os.path.exists(output_file_path):
                        if item == Log(output_file_path):
                            duplicates.append(item.path)
                            break
                        count += 1
                        try:
                            filename = os.path.split(output_file_path)[-1][:-4]
                            output_file_name = f"{filename}_{count}{item.extension}"
                            output_file_path = os.path.join(prefix, output_file_name)
                            shutil.move(item.path, output_file_path, copy_function=shutil.copy2)
                            break
                        except Exception as e:
                            print("Error:", e)
                            continue
                    try:
                        shutil.move(
                            item.path,
                            os.path.join(prefix, item.basename),
                            copy_function=shutil.copy2,
                        )
                    except Exception as e:
                        cprint(e, fg.gray)
                        continue
                    rm_empty_folders(item.dir_name)
                elif item.is_dir:
                    rm_empty_folders(item.path)
                elif not item.is_dir and not isinstance(item, Dir) and item.extension is not None:
                    # ============================ MISC  =============================== #
                    os.makedirs(os.path.join(output_dir, "Misc"), exist_ok=True)
                    prefix = os.path.join(output_dir, "Misc")
                    for mimetype, ext in MIME.items():
                        if item.extension in ext:
                            os.makedirs(os.path.join(prefix, mimetype), exist_ok=True)
                            prefix = os.path.join(prefix, mimetype)
                            break

                    output_file_path = os.path.join(prefix, item.basename)
                    count = 0
                    while os.path.exists(output_file_path):
                        other = obj(output_file_path)
                        if item == other:
                            duplicates.append(item.path)
                            break
                        count += 1
                        try:
                            filename = os.path.split(output_file_path)[-1][:-4]
                            output_file_name = f"{filename}_{count}{item.extension}"
                            output_file_path = os.path.join(prefix, output_file_name)
                            shutil.move(item.path, output_file_path, copy_function=shutil.copy2)
                            break
                        except Exception as e:
                            print("Error:", e)
                            continue
                    try:
                        # if os.path.isdir(input_dir) or os.path.isdir(
                        #     output_file_path
                        # ):  # " #or os.path.is_empty:
                        #     cprint(
                        #         f"Error concatating file paths for file {item.basename}",
                        #         fg.red,
                        #         style.bold,
                        #         style.underline,
                        #     )
                        #     pass
                        shutil.move(
                            item.path,
                            output_file_path,
                            copy_function=shutil.copy2,
                        )
                    except Exception:
                        pass
                    rm_empty_folders(item.path)
                    # cprint(f"Unknown file type{type(item)}, {item.path}", fg.cyan, style.underline)
                # else:

        cprint("Done organizing files", fg.green)
        return removed, num_items, duplicates


if __name__ == "__main__":
    args = parse_args()
    corrupted = []
    try:
        removed, items, dupes = main(args.input, args.output)
        # cprint("Checking validity...")
        # _old = Dir(args.input)
        # _new = Dir(args.output)
        # _items = len(_old)
        # progress = ProgressBar(_items)
        # for item in _old:
        #     try:
        #         progress.increment()
        #         new_file = _new.file_info(item.basename)
        #         if not os.path.exists(new_file.path) and not new_file.is_dir:
        #             cprint(f"{new_file.basename} is missing", fg.red)
        #         elif isinstance(new_file, (Video, Img)) and new_file.is_corrupt:
        #             cprint(f"{new_file.basename} is corrupted", fg.red)
        #             corrupted.append(new_file.path)
        #         else:
        #             continue
        #     except KeyboardInterrupt:
        #         sys.exit(0)

        cprint(f"Done!\n\nBefore: {items}", fg.green)
        cprint(f"Removed: {removed}", fg.red)
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    cleanup(args.input)
    if dupes:
        cprint("Duplicates found:", fg.orange)
        print("\n".join(list(dupes)))
    if input("Save to file?: 1") == "y":
        with open("output.txt", "w+") as f:
            f.write(str(dupes))
        cprint("Saved", fg.green)
