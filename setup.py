# Standard imports
from setuptools import setup, find_namespace_packages

# Long description
with open("README.md", "r") as fh:
    long_description = fh.read()

# Requirements
with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name = "kucoin_websocket",                                      # This is the name of the package
    version = "1.0.1",                                              # The initial release version
    author = "Keivan Ipchi Hagh",                                   # Full name of the author
    url = "https://github.com/keivanipchihagh/kucoin-websocket",    # URL to the github repository
    description = "Faster deployment is what we want!",
    long_description = long_description,                            # Long description read from the the readme file
    long_description_content_type = "text/markdown",
    packages = find_namespace_packages(include = ["kucoin_websocket"]),     # List of all python modules to be installed
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],          # Information to filter the project on PyPi website
    python_requires = '>=3.8',                  # Minimum version requirement of the package
    py_modules = ["kucoin_websocket"],          # Name of the python package
    # package_dir = {'':'kucoin_websocket'},    # Directory of the source code of the package
    install_requires = required                 # Install other dependencies if any
)