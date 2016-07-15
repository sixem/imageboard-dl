#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from os.path import expanduser
import multiprocessing as mp
import re
import os
import json
import urllib.parse
import requests
import shutil
import cfscrape
import argparse
import math
import sys

def report(site, message):
    print('[{}] {}'.format(site, message))

class variables():
    imageboard_name = None
    save_directory = '{}/Downloads'.format(expanduser("~"))
    
    version = "1.0.3"
    
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
        'masterchan': '((https?:\/\/)masterchan.org\/([A-Za-z]{1,10})\/([A-Za-z]{1,10})\/([0-9]{1,}))',
        'imgur:album': 'https?:\/\/imgur.com\/(a|gallery)\/([0-9A-Za-z]{1,})',
        'photbucket:album': '(https?:\/\/([a-zA-Z0-9]{1,10}).photobucket.com\/user\/([a-zA-Z0-9]{1,})\/library\/([a-zA-Z0-9 %]{1,}))',
        'xhamster:gallery': '(https?:\/\/xhamster.com\/photos\/gallery\/[0-9]{1,}\/.*.html)'
        }

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
        ':': 'x'
        }

    dict_return_codes = {
        'attempt': 1,
        'skip': 2,
        'download': 3,
        'error': 4
        }
    
class download():
     
    download_type = {
        'generic': 1,
        'cloudflare': 2,
        'content-disposition': 3
        }
    
    def generic(site, url, destination, name, x='generic'):
        try:
            req = requests.get(url, headers=variables.cfs_headers, 
                               timeout=variables.dict_general['cfs_timeout'])
            if req.status_code == 200:
                open(destination, 'wb').write(req.content)
                if os.path.exists(destination):
                    report('download', name)
                    return variables.dict_return_codes['download']
                else: return variables.dict_return_codes['error']
            else:
                report('download', 'ERROR ({}): {}'.format(req.status_code, name))
                return variables.dict_return_codes['error']
        except: return variables.dict_return_codes['error']
                
    def cloudflare(site, url, destination, name, x='cloudflare'):
        try:
            cfs = cfscrape.create_scraper()
            req = cfs.get(url, headers=variables.cfs_headers, 
                         timeout=variables.dict_general['cfs_timeout'], stream=True)
            if req.status_code is 200:
                with open(destination, 'wb') as f:
                    req.raw.decode_content = True
                    shutil.copyfileobj(req.raw, f)
                    if os.path.exists(destination):
                        report('download', name)
                        return variables.dict_return_codes['download']
                    else: return variables.dict_return_codes['error']
            else:
                report('download', 'ERROR ({}): {}'.format(req.status_code, name))
                return variables.dict_return_codes['error']
        except: return variables.dict_return_codes['error']
        
    def contentdisposition(site, url, destination, name, x='content-disposition'):
        try:
            req = requests.get(url, headers=variables.cfs_headers, 
                               timeout=variables.dict_general['cfs_timeout'])
            if req.status_code == 200:
                rm = re.search('attachment; filename="(.*)"', req.headers['Content-Disposition'])
                if rm:
                    open(destination, 'wb').write(req.content)
                    if os.path.exists(destination):
                        report('download', name)
                        return variables.dict_return_codes['download']
                else: return variables.dict_return_codes['error']
            else:
                report('download', 'ERROR ({}): {}'.format(req.status_code, name))
                return variables.dict_return_codes['error']
        except: return variables.dict_return_codes['error']
        
class queue():
    def file(site, uniq, url, filename, downloader):
        values = [site, utils.const_df(site, uniq), url,
                   utils.sanitize_filename(filename), downloader]
        for i in range(0, 5): scrapers.box[i].append(values[i])

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

    def get_filename_from_url(a):
        return a.split('/')[len(a.split('/'))-1]

    def const_df(a, b):
        return variables.dict_general['directory_format'].format(a, b)
    
    def sanitize_filename(fn):
        return "".join([c for c in fn if c.isalpha() or c.isdigit() or c==' ' or c=='.' or c=='_']).rstrip()

    def get_json(js):
        try:
            jso = json.loads(js)
            return jso
        except: raise ErrorParsingJson
    
    def result_to_string(results):
        out = ''
        if len(results) > 0:
            if results.count(variables.dict_return_codes['skip']) > 0:
                out += ('Downloaded {} file(s), {} file(s) already exists'.format(
                    results.count(variables.dict_return_codes['download']),
                    results.count(variables.dict_return_codes['skip'])))
            else: out += ('Downloaded {} file(s)'.format(results.count
                    (variables.dict_return_codes['download'])))
            if results.count(variables.dict_return_codes['error']) > 0:
                out += (' and encountered {} error(s) when downloading'.format(
                    results.count(variables.dict_return_codes['error'])))
            return out
        else: return ('No result were found')
    
class scrapers():
    
    box = [[], [], [], [], []]
    
    @classmethod
    def establish(self, a, site, v=True, bs=True, rb=True):
        try:
            request = self.request(a)
            if rb is True:
                self.box = [[], [], [], [], []]
            if v is True: report(site, 'Connection established ..')
            if bs is True: return BeautifulSoup(request, "html.parser")
            else: return request
        except: raise ErrorRequest
 
    @classmethod
    def xhamsterxgallery(self, a, site="xhamster:gallery", uniq=None, pages=1):
        p = self.establish(a, site)
        uniq = utils.url_to_digits(a)
        data = p.__str__()
        base_url = p.find("link", {"hreflang" : ["en", "ru", "de", "pl", "es", "fr"]})['href'].__str__()
        pager = p.find("div", {"class" : "pager"}).find("a", {"class" : "last"})
        if pager:
            rm = re.search('(\?page=([0-9]{1,}))', pager.__str__())
            if rm: pages = int(rm.group(2))
        report(site, 'Fetching Page 1 ..')
        for page in range(2, pages+1):
            report(site, 'Fetching Page {} ..'.format(page))
            n_url = '{}?page={}'.format(base_url, page)
            data += self.establish(n_url, site, v=False, bs=False, rb=False)
        items = BeautifulSoup(data, "html.parser").findAll("div", {"class" : "iItem"})
        for item in items:
            rm = re.search('i_([0-9]{1,3})([0-9]{3})([0-9]{3})', item['id'].__str__())
            if rm:
                link = item.find("img", {"class" : "vert"})['src'].__str__()
                extension = link.split('.')[len(link.split('.'))-1]
                filename = item['id'].__str__() + '.' + extension
                data = [rm.group(1), rm.group(2), rm.group(3)]
                for i, x in enumerate(data):
                    if len(x) < 3:
                        data[i] = (('0' * (3-len(x))) + data[i])         
                url = 'http://ep.xhamster.com/000/{}/{}/{}_1000.{}'.format(data[0], data[1], data[2], extension)
                queue.file(site, uniq, url, filename, download.download_type['generic'])
        return self.box
        
    @classmethod
    def photbucketxalbum(self, a ,site="photobucket:album", uniq=None):
        p = self.establish(a, site, bs=False)
        rgx_js = '({"contentFetchUrl"(.*)linkerMode":null})'
        rm = re.search(rgx_js, p.__str__().rstrip('\r\n'))
        if rm:        
            jso = utils.get_json((rm.group(1)))
            total = jso['total']
            uniq = jso['albumName']
            report(site, 'Album Name: {}'.format(uniq))
            collected = jso['pageSize']
            pages = math.ceil(int(jso['total']) / int(jso['pageSize']))
            report(site, 'Page: {} (Fetched: {})'.format(jso['pageNumber'], jso['pageSize']))
            for item in jso['items']['objects']:
                url = ('http://{}.photobucket.com/component/Download-File?file={}'
                       .format(item['subdomain'], urllib.parse.unquote(item['rawpath'])))
                queue.file(site, uniq, url, item['name'].__str__(), download.download_type['content-disposition'])
            for page in range(2, pages+1):
                p = self.establish(a, site, False, False, False)
                rm = re.search(rgx_js, p.__str__().rstrip('\r\n'))
                if rm:
                    jso = utils.get_json((rm.group(1)))
                    collected += int(jso['pageSize'])
                    report(site, 'Page: {} (Fetched: {})'.format(page, collected, total))
                    for item in jso['items']['objects']:
                        url = ('http://{}.photobucket.com/component/Download-File?file={}'
                               .format(item['subdomain'], urllib.parse.unquote(item['rawpath'])))
                        queue.file(site, uniq, url, filename, download.download_type['content-disposition'])
                else: raise ErrorParsingJson
        else: raise ErrorParsingJson
        return self.box
        
    @classmethod
    def imgurxalbum(self, a ,site="imgur:album", uniq=None):
        p = self.establish(a, site)
        images = p.findAll("div", {"class" : "post-image"})
        match = re.search(variables.dict_regex_table['imgur:album'], a)
        if match: uniq = match.group(2)
        for i in images:
            source = i.findAll(["img", "source"])
            for x in source:
                url = utils.fix_url(x['src'].__str__())
                queue.file(site, uniq, url, utils.get_filename_from_url(url), download.download_type['generic'])
        return self.box
        
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
            queue.file(site, uniq, url, filename, download.download_type['generic'])
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
                queue.file(site, uniq, url, filename, download.download_type['content-disposition'])
        return self.box
    
    @classmethod
    def masterchan(self, a, site="masterchan", uniq=None):
        p = self.establish(a, site)
        media = p.findAll("span", {"class" : "mediaFileAttrb"})
        uniq = p.find("input", {"name" : "fromThreadNumber"})['value']
        for m in media:
            filename = m.find("span", {"class" : "mediaFileName"}).contents[0].__str__()
            url = m.find("a", {"class" : "hyperlinkMediaFileName"})['href'].__str__()
            queue.file(site, uniq, url, filename, download.download_type['generic'])
        return self.box

    @classmethod
    def arhivach(self, a, site="arhivach", uniq=None):
        p = self.establish(a, site)
        images = p.findAll("a", {"class" : ["img_filename"]})
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
                    filename = utils.get_filename_from_url(url)
            else:
                if img['href'].startswith('/a_cimg/'):
                    url = 'https://arhivach.org/' + img['href'].__str__()
                    filename = img.contents[0].__str__()
                if img['href'].startswith('https://'):
                    url = img['href'].__str__()
                    filename = img.contents[0].__str__()
            if url is not None:
                queue.file(site, uniq, url, filename, download.download_type['cloudflare'])
        return self.box

    @classmethod
    def librechan(self, a, site="librechan", uniq=None):
        p = self.establish(a, site)
        fi = p.findAll("p", {"class" : "fileinfo"})
        uniq = p.find("div", {"class" : "thread"}).find("a", {"class" : "post_anchor"})['id'].__str__()
        for f in fi:
            url = 'https://librechan.net{0}'.format(f.find("a")['href'].__str__())
            filename = f.find("a").contents[0].__str__()
            queue.file(site, uniq, url, filename, download.download_type['generic'])
        return self.box

    @classmethod
    def twochhk(self, a, site="2chhk", uniq=None):
        p = self.establish(a, site)
        rm = re.search(variables.dict_regex_table['2chhk'], a)
        uniq = rm.group(5)
        const_url = ('{}2ch.hk/{}/src/{}/'.format(rm.group(2), rm.group(3), rm.group(5)))
        posts = p.findAll("div", {"class" :
            ["post-wrapper", "oppost-wrapper"]})
        for post in posts:
            desks = post.findAll("a", {"class" : ["desktop"]})
            for desk in desks:
                url = const_url + desk.contents[0].__str__()
                filename = desk.contents[0].__str__()
                queue.file(site, uniq, url, filename, download.download_type['generic'])
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
                queue.file(site, uniq, url, filename, download.download_type['cloudflare'])
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
            queue.file(site, uniq, url, filename, download.download_type['generic'])
        return self.box

    @classmethod
    def fourplebs(self, a, site="4plebs", uniq=None):
        p = self.establish(a, site)
        image_links = p.findAll("a", {"class" : "thread_image_link"})
        uniq = p.find("article")['data-thread-num']
        for link in image_links:
            url = link['href'].__str__()
            queue.file(site, uniq, url, utils.get_filename_from_url(url), download.download_type['generic'])
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

    def __init__(self, site, dest, dirn):
        self.current_url = site
        if dest is not None: variables.save_directory = dest
        
        self.detect_site()
        self.download_images(self.check_list(getattr(scrapers, 
            self.site_to_function(self.imageboard_name))(a=site), cdir=dirn))  
    
    def create_dir(self, a):
        if not os.path.exists(a):
            try: os.makedirs(a)
            except PermissionError: raise ErrorCreatingDirectory
            except: pass
        
    def download(self, site, uniq, url, name=None, dtype=download.download_type['generic']):

        if name is None: name = (url.split('/')[len(url.split('/'))-1])
        else: name = (utils.sanitize_filename(name))
                
        destination = ('{}/{}/{}'.format(variables.save_directory, uniq, name)).replace('//', '/')
        
        if not os.path.exists(destination):
            self.create_dir(os.path.dirname(destination))
            if dtype == download.download_type['cloudflare']: return download.cloudflare(site, url, destination, name)
            elif dtype == download.download_type['generic']: return download.generic(site, url, destination, name)
            elif dtype == download.download_type['content-disposition']: return download.contentdisposition(site, url, destination, name)
            else: return download.generic(site, url, destination, name)
        else: return variables.dict_return_codes['skip']
        
    def detect_site(self):
        for s, r in variables.dict_regex_table.items():
            match = re.search(r, self.current_url)
            if match:
                self.imageboard_name = variables.imageboard_name = s
                report(s, self.current_url)
        if self.imageboard_name is None: raise ErrorNotSupported
        
    def site_to_function(self, site):
        for s, r in variables.dict_number_converter.items(): site = str.replace(site, s, r)
        return site
    
    def check_list(self, lst, cdir=None):
        temp = []; p = 1
        if cdir is not None:
            for c, q in enumerate(lst[1]):
                lst[1][c] = cdir
        for i, x in enumerate(lst[3]):
            if lst[3][i] not in temp:
                temp.append(lst[3][i])
            else:
                file = os.path.splitext(lst[3][i])
                temp.append(file[0]+str(p)+file[1])
                p += 1
        lst[3] = temp
        return lst
    
    def download_images(self, box):
        for value, key in download.download_type.items():
            if len(box[4]) > 0: 
                if key == box[4][0]:
                    report('download', 'Using the {} downloader.'.format(value))
        pool = mp.Pool()
        results = pool.starmap(self.download, zip(box[0], box[1], box[2], box[3], box[4]))
        report('download', utils.result_to_string(results))

class ErrorRequest(Exception):
    """Raised if the page returns a bad status code"""
    
class ErrorNotSupported(Exception):
    """Raised if the url can't be parsed and or identified"""
    
class ErrorCreatingDirectory(Exception):
    """Raised if directory could not be created"""
    
class ErrorParsingJson(Exception):
    """Raised if encountering an error when extracting and or parsing a json object"""

def main():
    parser = argparse.ArgumentParser(description = 'Imageboard Downloader')
    parser.add_argument('urls', default = [], nargs = '*', help = 'One or more URLs to scrape') 
    parser.add_argument('-d', dest = 'destination', default = None, help = 'Where to save images (Path)', required = False)
    parser.add_argument('-dd', dest = 'directory_name',default = None, help = 'Where to save images (Directory name)', required = False)
    parser.add_argument('-s', dest='s', action='store_true', help='Display the available downloaders (Supported sites)')
    parser.add_argument('-v', dest='v', action='store_true', help='Show current version')

    args = parser.parse_args() 

    try:
        if args.v: print('imageboard-dl: version {}'.format(variables.version)); sys.exit(0)
        
        if args.s:
            for i in variables.dict_regex_table: print(i)
            sys.exit(0)
            
        for url in args.urls: scraper = ibdl(url, args.destination, args.directory_name)
       
    except ErrorRequest:
        report("error", "Error requesting page")

    except ErrorNotSupported:
        report("error", "Unsupported URL")
        
    except ErrorCreatingDirectory:
        report("error", "Error creating directory, do you have the required permissions?")
        
    except ErrorParsingJson:
        report("error", "Error parsing JSON")

if __name__ == '__main__':
    main()
