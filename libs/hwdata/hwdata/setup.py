from setuptools import setup, find_packages

VERSION = "1.0"
DESCRIPTION = "Query hardware related data"
LONG_DESCRIPTION = "Query hardware information from the system including CPU, GPU, RAM, etc."

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="hwdata",
    version=VERSION,
    author="Joona Mujunen",
    author_email="joona.mujunen@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["psutil"],
    keywords=["python", "hwinfo", "hwdata", "logging"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Personal",
        "Programming Language :: Python :: 3",
        "Operating System :: Linux :: Linux",
    ],
)
