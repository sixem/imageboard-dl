
from setuptools import setup

setup(name="imageboard-dl",
	version="1.0.53",
	description="Python based image downloader for various imageboards and online image albums.",
	url="https://github.com/sixem/imageboard-dl",
	author="sixem",
	author_email="sixem.mb99@gmail.com",
	license='MIT',
	packages=["imageboard-dl"],
	install_requires=['cfscrape','beautifulsoup4',],
	scripts=["bin/imageboard-dl"],
	zip_safe=False)
