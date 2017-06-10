# Imageboard-DL
Image downloader script for various imageboards and image albums written in Python. 

# Install
## Git
+ `git clone https://github.com/sixem/imageboard-dl`
+ `cd imageboard-dl`
+ `python3 setup.py install`

## Install From PyPI (Python Package Index)
### Using Pip
+ `pip3 install imageboard-dl`
### Using EasyInstall
+ `easy_install3 imageboard-dl`

# Requirements
+ Python 3+

# Usage
`imageboard-dl [-h] [-v] [-s] [-d PATH] [-dd DIRECTORY] URL(s)`
+ `-h` : Help.
+ `-v` : Print the current version.
+ `-s` : Show a list of supported sites.
+ `-d` : Where to download to (By default it will use your current working directory).
+ `-dd`: What the last directory will be named, by default it will be a unique name to distinguish it from other scraped threads.
