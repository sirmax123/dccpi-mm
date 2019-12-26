from setuptools import setup, Extension
import functools
import os

root = os.path.dirname(__file__)
root = os.path.abspath(root)
root = os.path.normpath(root)

path = functools.partial(os.path.join, root)
run_deps = open(path('requirements.txt')).readlines()

setup(
    name="dccpi_mm",
    packages=["dccpi_mm"],
    version="0.0.5",
    description="DCC protocol implementation for RaspberryPi",
    author="Max Mazur",
    author_email="sirmax123@gmail.com",
    url="https://github.com/sirmax123/dccpi-mm",
    download_url="",
    license="GNU General Public License v3 (GPLv3)",
    keywords=["dcc"],
    ext_modules=[
        Extension('dcc_rpi_encoder_c',
                  sources=['extensions/dcc_rpi_encoder_c.c'],
                  libraries=['wiringPi'])
    ],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Development Status :: 4 - Beta",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "Natural Language :: Russian",
        "Operating System :: POSIX :: Linux",
        "Topic :: System :: Networking",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    long_description="""\
This module implements the DCC protocol for controlling model trains using a
Raspberry Pi
.
To be added!
""",
    install_requires=run_deps
)
