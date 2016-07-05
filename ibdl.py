#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from os.path import expanduser
import multiprocessing as mp
import re
import os
import urllib.request
import shutil
import cfscrape
import argparse
from builtins import classmethod

def report(site, message):
    print('[{}] {}'.format(site, message))

class variables():
    imageboard_name = None
    always_use_cf = False
    
    dict_general = {
        'cfs_timeout': 60,
        'save_directory': '{}/Downloads'.format(expanduser("~")),
        'directory_format': '{}-{}'
        }

    cfs_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20150101 Firefox/47.0 (Chrome)',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-us,en;q=0.5',
        }

    dict_regex_table = {
        '2chhk': '((https?:\/\/)2ch.hk\/([A-Za-z]{1,10})\/([A-Za-z]{1,10})\/([0-9]{1,}).html)',
        '2channet': '((https?:\/\/)([A-Za-z]{1,5}).2chan.net\/([A-Za-z0-9]{1,})\/(res)\/([0-9]{1,}).html?)',
        '4chan': '((https?:\/\/)boards.4chan.org\/([A-Za-z]{1,10})\/([A-Za-z]{1,10})\/([0-9]{1,}))',
        '4plebs': '((https?:\/\/)archive.4plebs.org\/([A-Za-z]{1,10})\/([A-Za-z]{1,10})\/([0-9]{1,}))',
        '7chanorg': '((https?:\/\/)7chan.org\/([A-Za-z]{1,10})\/([A-Za-z]{1,10})\/([0-9]{1,}).html)',
        '8chan': '((https?:\/\/)8ch.net\/([A-Za-z]{1,10})\/([A-Za-z]{1,10})\/([0-9]{1,}).html)',
        'arhivach': '((https?:\/\/)arhivach.org\/[A-Za-z]{1,10}\/([0-9]{1,})\/)',
        'librechan': '((https?:\/\/)librechan.net\/([A-Za-z]{1,10})\/([A-Za-z]{1,10})\/([0-9]{1,}).html)',
        'masterchan': '((https?:\/\/)masterchan.org\/([A-Za-z]{1,10})\/([A-Za-z]{1,10})\/([0-9]{1,}))'
        }

    cfs_sites = [
        'arhivach',
        '8chan',
        '4plebs',
        'masterchan'
        ]

    possible_reasons = {
        403: ['Are you using a VPN / Proxy?']
        }

    dict_number_converter = {
        '1': 'one',
        '2': 'two',
        '3': 'three',
        '4': 'four',
        '5': 'five',
        '6': 'six',
        '7': 'seven',
        '8': 'eight',
        '9': 'nine',
        '10': 'ten',
        }

    dict_return_codes = {
        'attempt': 1,
        'skip': 2,
        'download': 3,
        'error': 4
        }
    
class downloaders():
    
    box = [[], [], [], []]
    
    @classmethod
    def establish(self, a, site, uniq=None):
        try:
            self.box = [[], [], [], []]
            request = self.request(a)
            report(site, a)
            report(site, 'Connected ..')
            return BeautifulSoup(request, "html.parser")
        except:
            raise ErrorRequest
        
    @classmethod
    def sevenchanorg(self, a ,site="7chanorg", uniq=None):
        p = self.establish(a, site)
        images = p.findAll("p", {"class" : "file_size"})
        uniq = p.find("input", {"name" : "replythread"})['value'].__str__()
        for image in images:
            rm = re.search(
                '(\(([0-9]{1,}.[0-9]{1,}[A-Z]{1,2}), ?([0-9]{1,}x[0-9]{1,}), ?(.{1,}.[a-zA-Z]{1,4})\))',
                image.contents[2].replace('\n', ''))
            url = image.find("a")['href']
            filename = None
            if rm: filename = rm.group(4)
            else: filename = image.find("a").contents[0].__str__().replace('\n', '')
            values = [site, ibdl.const_df(site, uniq), url, filename]
            for i in range(0, 4): self.box[i].append(values[i])
        return self.box
        
    @classmethod
    def twochannet(self, a ,site="2channet", uniq=None):
        p = self.establish(a, site)
        p.find("div", {"class" : "thre"})
        uniq = p.findAll("input")[0]['name'].__str__()
        links = p.findAll("a", {"target" : "_blank"})
        for link in links:
            filename = link.contents[0].__str__()
            if ('<img') not in link.contents[0].__str__():
                filename = ibdl.sanitize_filename(filename)
                url = link['href'].__str__()
                values = [site, ibdl.const_df(site, uniq), url, filename]
                for i in range(0, 4): self.box[i].append(values[i])
        return self.box
    
    @classmethod
    def masterchan(self, a, site="masterchan", uniq=None):
        p = self.establish(a, site)
        media = p.findAll("span", {"class" : "mediaFileAttrb"})
        uniq = p.find("input", {"name" : "fromThreadNumber"})['value']
        for m in media:
            filename = m.find("span", {"class" : "mediaFileName"}).contents[0].__str__()
            url = m.find("a", {"class" : "hyperlinkMediaFileName"})['href'].__str__()
            values = [site, ibdl.const_df(site, uniq), url, filename]
            for i in range(0, 4): self.box[i].append(values[i])
        return self.box

    @classmethod
    def arhivach(self, a, site="arhivach", uniq=None):
        p = self.establish(a, site)
        p.findAll("a", {"class" : ["img_filename"]})
        if uniq is None:
            rm = re.search(variables.dict_regex_table['arhivach'], a)
            if rm:
                uniq = rm.group(3)
            else:
                uniq = ''.join(c for c in a if c.isdigit())
        for img in images:
            url = None
            if img['href'][0] == ('#'):
                match = re.search("'(http(s)?:\/\/(.*).(.{2,5})\/(.*).(.{3,4}))'", img['onclick'].__str__())
                if match:
                    url = match.group(1)
            else:
                if img['href'].startswith('http'):
                    url = img['href'].__str__()
            if url is not None:
                values = [site, ibdl.const_df(site, uniq), url, None]
                for i in range(0, 4): self.box[i].append(values[i])
        return self.box

    @classmethod
    def librechan(self, a, site="librechan", uniq=None):
        p = self.establish(a, site)
        fi = p.findAll("p", {"class" : "fileinfo"})
        uniq = p.find("div", {"class" : "thread"}).find("a", {"class" : "post_anchor"})['id'].__str__()
        for f in fi:
            values = [site, variables.dict_general['directory_format'].format(site, uniq), 
                'https://librechan.net{0}'.format(f.find("a")['href'].__str__()),
                f.find("a").contents[0].__str__()]
            for i in range(0, 4): self.box[i].append(values[i])
        return self.box

    @classmethod
    def twochhk(self, a, site="2chhk"):
        p = self.establish(a, site)
        rm = re.search(variables.dict_regex_table['2chhk'], a)
        const_url = ('{}2ch.hk/{}/src/{}/'.format(rm.group(2), rm.group(3), rm.group(5)))
        posts = p.findAll("div", {"class" :
            ["post-wrapper", "oppost-wrapper"]})
        for post in posts:
            desks = post.findAll("a", {"class" : ["desktop"]})
            for desk in desks:
                values = [site, variables.dict_general['directory_format'].format(site, rm.group(5)),
                    const_url + desk.contents[0].__str__(), desk.contents[0].__str__()]
                for i in range(0, 4): self.box[i].append(values[i])
        return self.box
    
    @classmethod
    def fourchan(self, a, site="4chan", uniq=None):
        p = self.establish(a, site)
        posts = p.findAll("div", {"class" : ["postContainer", "opContainer"]})
        uniq = p.find("div", {"class" : "thread"})['id'].__str__()
        for post in posts:
            file_info = post.findAll("div", {"class" : ["fileText"]})
            for fi in file_info:
                filename = fi.find("a").contents[0].__str__()
                url = ibdl.fix_url(fi.find("a")['href'])
                values = [site, ibdl.const_df(site, uniq), url, filename]
                for i in range(0, 4): self.box[i].append(values[i])
        return self.box
    
    @classmethod
    def eightchan(self, a, site="8chan", uniq=None):
        p = self.establish(a, site)
        fi = p.findAll("p", {"class" : "fileinfo"})
        uniq = p.find("div", {"class" : "thread"}).find("a", {"class" : "post_anchor"})['id']
        for f in fi:
            filename = f.find("span", {"class" : "unimportant"}).find("span", {"class" : "postfilename"}).contents[0].__str__()
            url = f.find("a")['href'].__str__()
            values = [site, ibdl.const_df(site, uniq), url, filename]
            for i in range(0, 4): self.box[i].append(values[i])
        return self.box

    @classmethod
    def fourplebs(self, a, site="4plebs", uniq=None):
        p = self.establish(a, site)
        image_links = p.findAll("a", {"class" : "thread_image_link"})
        uniq = p.find("article")['data-thread-num']
        for link in image_links:
            values = [site, ibdl.const_df(site, uniq), link['href'].__str__(), None]
            for i in range(0, 4): self.box[i].append(values[i])
        return self.box

    @classmethod
    def request(self, url):
        cfs = cfscrape.create_scraper()
        request = cfs.get(url, headers = variables.cfs_headers, timeout = variables.dict_general['cfs_timeout'])
        if request.status_code is 200: return request.text
        else: raise ErrorRequest

class ibdl(object):

    imageboard_name = None

    def __init__(self, site, cf):
        self.current_url = site
        variables.always_use_cf = cf
        
        self.detect_site()
        self.download_images(getattr(downloaders, self.site_to_function(self.imageboard_name))(a=site)) 

    @classmethod
    def sanitize_filename(self, fn):
        return "".join([c for c in fn if c.isalpha() or c.isdigit() or c==' ' or c=='.']).rstrip()
    
    @classmethod
    def create_dir(self, a):
        if not os.path.isdir(a):
            os.makedirs(a)
            
    @classmethod
    def const_df(self, a, b):
        return variables.dict_general['directory_format'].format(a, b)
        
    @classmethod
    def download(self, site, uniq, url, name=None, destination=None, cf=variables.always_use_cf):
        try:
            cfs = cfscrape.create_scraper()
    
            if name is None:
                name = (url.split('/')[len(url.split('/'))-1])
            else:
                name = (self.sanitize_filename(name))
            
            if site in variables.cfs_sites:
                cf = True
        
            if destination is None:
                destination = ('{}/{}/{}'.format(variables.dict_general['save_directory'], uniq, name)).replace('//', '/')
            else:
                destination = ('{}/{}'.format(destination, name)).replace('//', '/')

            if not os.path.exists(destination):
                report(site, name)
                self.create_dir(os.path.dirname(destination))
                if cf:
                    req = cfs.get(url, headers=variables.cfs_headers, timeout=variables.dict_general['cfs_timeout'], stream=True)
                    if req.status_code is 200:
                        with open(destination, 'wb') as f:
                            req.raw.decode_content = True
                            shutil.copyfileobj(req.raw, f)
                            return variables.dict_return_codes['download']
                    else:
                        return variables.dict_return_codes['error']
                else:
                    with urllib.request.urlopen(url) as response, open(destination, 'wb') as of:
                        try:
                            shutil.copyfileobj(response, of)
                        except IOError as e:
                            return variables.dict_return_codes['error']
                        else:
                            return variables.dict_return_codes['download']
            else:
                return variables.dict_return_codes['skip']
        except:
            return variables.dict_return_codes['download']
        
    def detect_site(self):
        for s, r in variables.dict_regex_table.items():
            match = re.search(r, self.current_url)
            if match:
                self.imageboard_name = variables.imageboard_name = s
        if self.imageboard_name is None:
            raise ErrorNotSupported
        
    def site_to_function(self, site):
        o = site
        for s, r in variables.dict_number_converter.items():
            o = str.replace(o, s, r)
        return o
    
    @classmethod
    def fix_url(self, a):
        if a.startswith('//'):
            a = 'https:%s' % a
        return a
    
    def result_to_string(results):
        if len(results) > 0:
            if results.count(variables.dict_return_codes['skip']) > 0:
                return ('Downloaded {} file(s), {} file(s) already exists'.format(
                    results.count(variables.dict_return_codes['download']),
                    results.count(variables.dict_return_codes['skip'])))
            else: return ('Downloaded {} file(s)'.format(results.count
                    (variables.dict_return_codes['download'])))
            if results.count(variables.dict_return_codes['error']) > 0:
                return ('Encountered {} error(s) when downloading'.format(
                    results.count(variables.dict_return_codes['error'])))
        else: return ('No result were found')
    
    @classmethod
    def download_images(self, container):   
        pool = mp.Pool()
        results = pool.starmap(self.download, zip(container[0], container[1], container[2], container[3]))
        report(variables.imageboard_name, self.result_to_string(results))

class ErrorRequest(Exception):
    """Raised if the page returns a bad status code"""
    
class ErrorNotSupported(Exception):
    """Raised if the url can't be parsed and or identified"""

def main():
    parser = argparse.ArgumentParser(description='Imageboard Downloader')
    parser.add_argument('urls', default=[], nargs='*', help='One or more URLs to scrape') 
    parser.add_argument('-cf', dest='cf', action='store_true', help='Force cloudflare scraper')

    args = parser.parse_args() 

    try:
        for url in args.urls:
            scraper = ibdl(url, args.cf)
       
    except ErrorRequest:
        report("?", "Error requesting page")

    except ErrorNotSupported:
        report("?", "Unsupported URL")

if __name__ == '__main__':
    main()
