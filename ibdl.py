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

def report(site, message):
    print('[{}] {}'.format(site, message))

class variables():
    imageboard_name = None
    use_cf = False
    save_directory = '{}/Downloads'.format(expanduser("~"))
    
    dict_general = {
        'cfs_timeout': 60,
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
        '7chanorg': '((https?:\/\/)7chan.org\/([A-Za-z0-9]{1,10})\/([A-Za-z]{1,10})\/([0-9]{1,}).html)',
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

class utils():
    def url_to_digits(str, cutoff=0):
        if str is None or str == '':
            return 0
        out_number = ''
        for ele in str:
            if ele.isdigit():
                out_number += ele
        return out_number[cutoff:]
    
    def fix_url(a):
        if a.startswith('//'): a = 'https:%s' % a
        return a

    def const_df(a, b):
        return variables.dict_general['directory_format'].format(a, b)
    
    def sanitize_filename(fn):
        return "".join([c for c in fn if c.isalpha() or c.isdigit() or c==' ' or c=='.']).rstrip()
    
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
    
class downloaders():
    
    box = [[], [], [], []]
    
    @classmethod
    def establish(self, a, site, uniq=None):
        try:
            self.box = [[], [], [], []]
            request = self.request(a)
            report(site, 'Connection established ..')
            return BeautifulSoup(request, "html.parser")
        except:
            raise ErrorRequest
        
    @classmethod
    def sevenchanorg(self, a ,site="7chanorg", uniq=None):
        p = self.establish(a, site)
        rgx = '(\(([0-9]{1,}.[0-9]{1,}[A-Z]{1,2}), ?([0-9]{1,}x[0-9]{1,}), ?(.{1,}.[a-zA-Z]{1,4})\))'
        images = p.findAll("p", {"class" : "file_size"})
        uniq = p.find("input", {"name" : "replythread"})['value'].__str__()
        multi_images = p.findAll("img", {"class" : ["multithumb", "multithumbfirst"]})
        for image in images:
            url = image.find("a")['href']
            filename = None
            rm = re.search(rgx, image.contents[2].replace('\n', ''))
            if rm: filename = rm.group(4)
            else: filename = image.find("a").contents[0].__str__().replace('\n', '')
            values = [site, utils.const_df(site, uniq), url, filename]
            for i in range(0, 4): self.box[i].append(values[i])
        for m_image in multi_images:
            url = m_image['src'].replace('thumb', 'src').replace('s.', '.')
            filename = None
            rm = re.search(rgx, m_image['title'])
            if rm: filename = rm.group(4)
            else: filename = m_image['title'].__str__()
            values = [site, utils.const_df(site, uniq), url, utils.sanitize_filename(filename)]
            for i in range(0, 4): self.box[i].append(values[i])
        return self.box
        
    @classmethod
    def twochannet(self, a ,site="2channet", uniq=None):
        p = self.establish(a, site)
        p.find("div", {"class" : "thre"})
        uniq = p.find("input", {"name" : "resto"})['value'].__str__()
        if len(uniq) < 1 and uniq.isdigit() is False: uniq = utils.url_to_digits(a, 1)
        links = p.findAll("a", {"target" : "_blank"})
        for link in links:
            filename = link.contents[0].__str__()
            if ('<img') not in link.contents[0].__str__() and ('src') in link['href'].__str__():
                filename = utils.sanitize_filename(filename)
                url = link['href'].__str__()
                values = [site, utils.const_df(site, uniq), url, utils.sanitize_filename(filename)]
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
            values = [site, utils.const_df(site, uniq), url, utils.sanitize_filename(filename)]
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
                values = [site, utils.const_df(site, uniq), url, None]
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
                utils.sanitize_filename(f.find("a").contents[0].__str__())]
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
                file_a = fi.find("a")
                filename = file_a.contents[0].__str__()
                if file_a.has_attr('title'): filename = file_a['title'].__str__()
                url = utils.fix_url(fi.find("a")['href'])
                values = [site, utils.const_df(site, uniq), url, filename]
                for i in range(0, 4): self.box[i].append(values[i])
        return self.box
    
    @classmethod
    def eightchan(self, a, site="8chan", uniq=None):
        p = self.establish(a, site)
        fi = p.findAll("p", {"class" : "fileinfo"})
        uniq = p.find("div", {"class" : "thread"}).find("a", {"class" : "post_anchor"})['id']
        for f in fi:
            filename = f.find("span", {"class" : "unimportant"}).find("span",
                {"class" : "postfilename"}).contents[0].__str__()
            url = f.find("a")['href'].__str__()
            values = [site, utils.const_df(site, uniq), url, filename]
            for i in range(0, 4): self.box[i].append(values[i])
        return self.box

    @classmethod
    def fourplebs(self, a, site="4plebs", uniq=None):
        p = self.establish(a, site)
        image_links = p.findAll("a", {"class" : "thread_image_link"})
        uniq = p.find("article")['data-thread-num']
        for link in image_links:
            values = [site, utils.const_df(site, uniq), link['href'].__str__(), None]
            for i in range(0, 4): self.box[i].append(values[i])
        return self.box

    @classmethod
    def request(self, url):
        cfs = cfscrape.create_scraper()
        request = cfs.get(url, headers = variables.cfs_headers,
            timeout = variables.dict_general['cfs_timeout'])
        if request.status_code is 200: return request.text
        else: raise ErrorRequest

class ibdl(object):

    imageboard_name = destination = None

    def __init__(self, site, dest, dirn, cf):
        self.current_url = site
        variables.use_cf = cf
        if dest is not None: variables.save_directory = args.destination
        
        self.detect_site()
        self.download_images(self.modify_list(getattr(downloaders, 
            self.site_to_function(self.imageboard_name))(a=site), cdir=dirn))  
    
    def create_dir(self, a):
        if not os.path.exists(a):
            try: os.makedirs(a)
            except PermissionError: raise ErrorCreatingDirectory
            except: pass
        
    def download(self, site, uniq, url, name=None, cf=variables.use_cf):
        cfs = cfscrape.create_scraper()
    
        if name is None: name = (url.split('/')[len(url.split('/'))-1])
        else: name = (utils.sanitize_filename(name))
            
        if site in variables.cfs_sites: cf = True
                
        destination = ('{}/{}/{}'.format(variables.save_directory, uniq, name)).replace('//', '/')
        
        if not os.path.exists(destination):
            self.create_dir(os.path.dirname(destination))
            if cf:
                req = cfs.get(url, headers=variables.cfs_headers, timeout=variables.dict_general['cfs_timeout'], stream=True)
                if req.status_code is 200:
                    with open(destination, 'wb') as f:
                        req.raw.decode_content = True
                        shutil.copyfileobj(req.raw, f)
                        if os.path.exists(destination): report(site, name)
                        return variables.dict_return_codes['download']
                else:
                    return variables.dict_return_codes['error']
            else:
                with urllib.request.urlopen(url) as response, open(destination, 'wb') as of:
                    try:
                        shutil.copyfileobj(response, of)
                        if os.path.exists(destination): report(site, name)
                    except IOError as e:
                        return variables.dict_return_codes['error']
                    else:
                        return variables.dict_return_codes['download']
        else:
            return variables.dict_return_codes['skip']
        
    def detect_site(self):
        for s, r in variables.dict_regex_table.items():
            match = re.search(r, self.current_url)
            if match:
                self.imageboard_name = variables.imageboard_name = s
                report(s, self.current_url)
        if self.imageboard_name is None: raise ErrorNotSupported
        
    def site_to_function(self, site):
        o = site
        for s, r in variables.dict_number_converter.items(): o = str.replace(o, s, r)
        return o
    
    def modify_list(self, lst, cdir=None, ind=3, temp=[]):
        if cdir is not None:
            for c, q in enumerate(lst[1]):
                lst[1][c] = cdir
        p = 1
        for i, x in enumerate(lst[ind]):
            if lst[ind][i] not in temp:
                temp.append(lst[ind][i])
            else:
                file = os.path.splitext(lst[ind][i])
                temp.append(file[0]+str(p)+file[1])
                p += 1
        lst[ind] = temp
        return lst
    
    def download_images(self, box):   
        pool = mp.Pool()
        results = pool.starmap(self.download, zip(box[0], box[1], box[2], box[3]))
        report(variables.imageboard_name, utils.result_to_string(results))

class ErrorRequest(Exception):
    """Raised if the page returns a bad status code"""
    
class ErrorNotSupported(Exception):
    """Raised if the url can't be parsed and or identified"""
    
class ErrorCreatingDirectory(Exception):
    """Raised if directory could not be created"""

def main():
    parser = argparse.ArgumentParser(description = 'Imageboard Downloader')
    parser.add_argument('urls', default = [], nargs = '*', help = 'One or more URLs to scrape') 
    parser.add_argument('-cf', dest = 'cf', action = 'store_true', help = 'Force cloudflare scraper')
    parser.add_argument('-d', dest = 'destination', default = None, help = 'Where to save images (Path)', required = False)
    parser.add_argument('-dd', dest = 'directory_name',default = None, help = 'Where to save images (Directory name)', required = False)

    args = parser.parse_args() 

    try:
        for url in args.urls:
            scraper = ibdl(url, args.destination, args.directory_name, args.cf)
       
    except ErrorRequest:
        report("Error", "Error requesting page")

    except ErrorNotSupported:
        report("Error", "Unsupported URL")
        
    except ErrorCreatingDirectory:
        report("Error", "Error creating directory, do you have the required permissions?")

if __name__ == '__main__':
    main()
