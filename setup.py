
from setuptools import setup

setup(name="imageboard-dl",
	version="1.0.5",
	description="Python based image downloader for various imageboards and online image albums.",
	url="https://github.com/Sixem/imageboard-dl",
	author="bentkrisell",
	author_email="bentkrisell@gmail.com",
	license='MIT',
	packages=["imageboard-dl"],
	install_requires=['cfscrape','beautifulsoup4',],
	scripts=["bin/imageboard-dl"],
	zip_safe=False)
