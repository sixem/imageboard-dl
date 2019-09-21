# Imageboard-DL
**Image downloader/scraper for various imageboards and image albums written in Python.**

### Requirements
+ Python 3.4+

# Installing
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

### `imageboard-dl [-h] [-v] [-s] [-x] [-p PATH] [-d DIRECTORY] URL(s)`

+ `-h` : Show a help dialog.
+ `-v` : Print the current version.
+ `-s` : Show a list of supported scrapers.
+ `-p` : Where to download to. By default it will use your current working directory.
+ `-x` : Disables saving files into separate folders (see -d).
+ `-d`: Name of a separate folder for saving files into (this folder will be created inside the current path, default is a unique name fetched from the URL). This feature can be disabled by using `-x`, if so the files will be downloaded directly into the selected path instead.
+ `-t` : Maximum amount of concurrent threads (default is 32).
+ `-s` : Amount of time to sleep before each request in seconds.
+ `--debug` : Print some (very) basic debugging information.

### Basic usage example:

`imageboard-dl https://boards.4chan.org/b/thread/1292929292 -p "/home/user/Downloads/"`

### This will store your scraped files here:

`/home/user/Downloads/4chan-t1292929292`