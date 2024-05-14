#!/usr/bin/env python3

# remove_pkg_dupes.py - Removes duplicate packages in an pacman cache

import os, shutil, sys, re

from ExecutionTimer import ExecutionTimer
from ProgressBar import ProgressBar
from MetaData import FileObject, DirectoryObject

PACKAGE_DIRECTORY = '/var/lib/pacman/local/'

# def generate_file_objects(packages):
#     for package in packages:
#         yield DirectoryObject(os.path.join(PACKAGE_DIRECTORY, package))


def main():

    packages = []
    package_names = []
    duplicate_packages = []

    extract_details = re.compile(r'(.*)-(\d+[\.:-]\d+.*\d*)')
    # Get list of packages
    #packages = os.listdir(PACKAGE_DIRECTORY)
    root = DirectoryObject(PACKAGE_DIRECTORY)

    # Generate file objects
    for pkg in root:
        if not pkg.is_dir():
            continue
        # Extract name and version
        try:
            matches = re.findall(extract_details, pkg.file_name)[0]
        except IndexError:
            continue
        pkg.name, pkg.version = matches
        packages.append(matches)
    # Compare
    for name, version in packages:
        if name in package_names:
            duplicate_packages.append((name, version))
        else:
            package_names.append(name)

    print(f'\033[32mFound {len(package_names)} packages\033[0m')
    print(f'\033[31mFound {len(duplicate_packages)} duplicate packages\033[0m')
    print('\033[3m; ----------------------------------------------------\033[0m')
    for name, version in sorted(duplicate_packages):
        # shutil.rmtree(os.path.join(PACKAGE_DIRECTORY, (name + '-' +version)))
        print(f'\033[34mRemoving {name:<37}\033[0m - \033[35m{version}\033[0m')

    # Compare and remove duplicates

    # pkg_objects = generate_file_objects(packages)
    # matches = re.findall(extract_details, '\n'.join(packages))
    



# Example 
if __name__ == "__main__":
    # # Check if running as root
    # try:
    #     if os.getuid() != 0:
    #         print("This script must be run as root.")
    #         sys.exit(1)
    # except Exception as e:
    #     print(e)
    # # Run
    with ExecutionTimer():
        main()







        