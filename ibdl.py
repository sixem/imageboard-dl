#!/usr/bin/env python
# -*- coding: utf-8 -*-

import utils
import downloaders
import re
import argparse
import multiprocessing as mp

class ibdl():
    def __init__(self):
        self._ARGS = None
        
    def initiate(self, a):
        for url in a:
            site = utils.DETECT_SITE(url)
            if site is not None:
                r = getattr(downloaders, utils.REPLACE_NUMBERS(site))(url)
                if r is not False:
                    if len(r[2]) > 0:
                        pool = mp.Pool()
                        results = pool.starmap(utils.DOWNLOAD, zip(r[0], r[1], r[2], r[3]))
                        utils.REPORT(site, utils.RESULT_TO_STRING(results))
                    else:
                        utils.REPORT(site, 'No images were found')
            else:
                utils.REPORT('?', 'This site is not supported')
    
    def main(self):
        parser = argparse.ArgumentParser(description='Imageboard Downloader')
        
        parser.add_argument(
            '_URLS',
            default=[],
            nargs='*',
            help='One or more URLs to scrape'
            )
        
        parser.add_argument('-cf',
            dest='cf',
            action='store_true',
            help='Force cloudflare scraper')
        
        self._ARGS = parser.parse_args() 
        self.initiate(self._ARGS._URLS)
  
if __name__ == "__main__":
    ibdl().main()