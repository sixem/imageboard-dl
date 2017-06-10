# Imageboard-DL
Image downloader script for various imageboards and image albums written in Python. 

### Requirements
+ Python 3+

## Installing
## Git
+ `git clone https://github.com/sixem/imageboard-dl`
+ `cd imageboard-dl`
+ `python3 setup.py install`

## Install From PyPI (Python Package Index)
### Using Pip
+ `pip3 install imageboard-dl`
### Using EasyInstall
+ `easy_install3 imageboard-dl`

# Usage

### `imageboard-dl [-h] [-v] [-s] [-d PATH] [-dd DIRECTORY] URL(s)`

+ `-h` : Show a help dialog.
+ `-v` : Print the current version.
+ `-s` : Show a list of supported sites.
+ `-d` : Where to download to. By default it will use your current working directory. Threads will be scraped into this folder with their own unique folder names on top (see -dd for that).
+ `-dd`: What the last directory will be named. By default it will be a unique name to distinguish it from other scraped threads, but a custom one can be set if you want, but that will also make it so that if you are scraping multiple threads it will all go into your custom set folder.

### Basic usage examaple:

`imageboard-dl https://boards.4chan.org/b/thread/1292929292 -d "/home/user/Downloads/"`

### This will store your scraped files here:

`/home/user/Downloads/4chan-t1292929292`

