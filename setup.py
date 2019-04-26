from setuptools import setup

setup(name="imageboard-dl",
	version="1.0.61",
	description="Image downloader/scraper for various imageboards and image albums written in Python.",
	url="https://github.com/sixem/imageboard-dl",
	author="emy",
	author_email="admin@eyy.co",
	license='MIT',
	packages=["imageboard-dl"],
	install_requires=['cfscrape','beautifulsoup4',],
	scripts=["bin/imageboard-dl"],
	zip_safe=False)
