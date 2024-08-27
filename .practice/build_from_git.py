#!/usr/bin/env python3

# build_from_git.py -

import subprocess
import os
import argparse


def build(repository_url, build_command):
    """
    Clone the repository, parse repository name from URL, change directory to the cloned repository, and build the project.

    Args:
        repository_url (str): The URL of the repository to clone.
        build_command (str): The command to build the project.

    Raises:
        subprocess.CalledProcessError: If any of the subprocess calls fail.

    Returns:
        None
    """
    # Clone the repository
    try:
        subprocess.check_call(["git", "clone", repository_url])
        print("Repository cloned successfully.")
    except subprocess.CalledProcessError:
        print("Failed to clone the repository.")
        exit(1)

    # Parse repository name from URL
    repo_name = repository_url.split("/")[-1]
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]

    # Change directory to the cloned repository
    os.chdir(repo_name)

    # Build the project
    try:
        subprocess.check_call(build_command.split())
        print("Project built successfully.")
    except subprocess.CalledProcessError:
        print("Failed to build the project")
        exit(1)


def parse_arguments():
    """
    Parse the command line arguments to build a project from a Git repository.

    Returns:
        Namespace: The parsed command-line arguments.
    """

    parser = argparse.ArgumentParser(description="Build a project from a Git repository.")
    parser.add_argument(
        "repository_url",
        help="Enter the URL of the Git repository.",
    )
    parser.add_argument(
        "build_command",
        help="Enter the command to build the project.",
    )
    return parser.parse_args()


# Example usage
if __name__ == "__main__":
    args = parse_arguments()
    build(args.repository_url, args.build_command)
    """
    # URL of the Github repository to download
    repository_url = "https://github.com/username/repository.git"
    # Command to build the project. This is project-specific.
    build_command = "make"  # Replace this with actual build command like 'mvn install' for maven projects
    """
