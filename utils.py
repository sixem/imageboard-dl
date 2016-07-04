#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import expanduser
import re
import os
import urllib.request
import shutil
import cfscrape

_GENERAL = {
    'cfs_timeout': 60,
    'save_directory': '{}/Downloads'.format(expanduser("~")),
    'directory_format': '{}-{}'
    }

_CFS_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20150101 Firefox/47.0 (Chrome)',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-us,en;q=0.5',
    }

_REGEX_TABLE = {
    'librechan': '((https?:\/\/)librechan.net\/([A-Za-z]{1,10})\/([A-Za-z]{1,10})\/([0-9]{1,}).html)',
    '2chhk': '((https?:\/\/)2ch.hk\/([A-Za-z]{1,10})\/([A-Za-z]{1,10})\/([0-9]{1,}).html)',
    '4chan': '((https?:\/\/)boards.4chan.org\/([A-Za-z]{1,10})\/([A-Za-z]{1,10})\/([0-9]{1,}))',
    '8chan': '((https?:\/\/)8ch.net\/([A-Za-z]{1,10})\/([A-Za-z]{1,10})\/([0-9]{1,}).html)',
    'arhivach': '((https?:\/\/)arhivach.org\/[A-Za-z]{1,10}\/([0-9]{1,})\/)',
    '4plebs': '((https?:\/\/)archive.4plebs.org\/([A-Za-z]{1,10})\/([A-Za-z]{1,10})\/([0-9]{1,}))',
    'masterchan': '((https?:\/\/)masterchan.org\/([A-Za-z]{1,10})\/([A-Za-z]{1,10})\/([0-9]{1,}))'
    }

_CFS_SITES = [
    'arhivach',
    '8chan',
    '4plebs',
    'masterchan'
    ]

_POSSIBLE_REASONS = {
    403: ['Are you using a VPN / Proxy?']
    }
                

_NUMBER_CONV = {
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

_RETURN_CODES = {
    'ATTEMPT': 1,
    'SKIP': 2,
    'DOWNLOAD': 3,
    'ERROR': 4
    }

def CREATE_DIR(a):
        try:
            if os.path.exists(a) == False:
                os.makedirs(a)
                if os.path.exists(a):
                    return True
        except:
            return False
        return False
    
def SANITIZE_FILENAME(fn):
    return "".join([c for c in fn if c.isalpha() or c.isdigit() or c==' ' or c=='.']).rstrip()
    
def REPORT(site, b):
    print('[{0}] {1}'.format(site, b))

def DOWNLOAD(site, unique_id, url, name=None, destination=None, cf=False):
    cfs = cfscrape.create_scraper()
    
    if name is None:
        name = (url.split('/')[len(url.split('/'))-1])
    else:
        name = (SANITIZE_FILENAME(name))
        
    if site in _CFS_SITES:
        cf = True
        
    if destination is None:
        destination = ('{0}/{1}/{2}'.format(_GENERAL['save_directory'], unique_id, name)).replace('//', '/')
    else:
        destination = ('{0}/{1}'.format(destination, name)).replace('//', '/')

    if not os.path.exists(destination):
        REPORT(site, name)
        CREATE_DIR(os.path.dirname(destination))
        if cf:
            req = cfs.get(url, headers=_CFS_HEADERS, timeout=_GENERAL['cfs_timeout'], stream=True)
            if req.status_code is 200:
                with open(destination, 'wb') as f:
                    req.raw.decode_content = True
                    shutil.copyfileobj(req.raw, f)
                    return _RETURN_CODES['DOWNLOAD']
            else:
                return _RETURN_CODES['ERROR']
        else:
            with urllib.request.urlopen(url) as response, open(destination, 'wb') as of:
                try:
                    shutil.copyfileobj(response, of)
                except IOError as e:
                    return _RETURN_CODES['ERROR']
                else:
                    return _RETURN_CODES['DOWNLOAD']
    else:
        return _RETURN_CODES['SKIP']

def REQUEST(url):
    cfs = cfscrape.create_scraper()
    request = cfs.get(url, headers=_CFS_HEADERS, timeout=_GENERAL['cfs_timeout'])
    if request.status_code is 200:
        return [True, request.text]
    else:
        return [False, request.status_code]

def DETECT_SITE(a):
    for s, r in _REGEX_TABLE.items():
        match = re.search(r, a)
        if match:
            return s
    return None

def FIX_URL(a):
    if a.startswith('//'):
        a = 'https:%s' % a
    return a

def RESULT_TO_STRING(results):
    if len(results) > 0:
            if results.count(_RETURN_CODES['SKIP']) > 0:
                return ('Downloaded {0} file(s), {1} file(s) already exists'.format(results.count(_RETURN_CODES['DOWNLOAD']), results.count(_RETURN_CODES['SKIP'])))
            else:
                return ('Downloaded {0} file(s)'.format(results.count(_RETURN_CODES['DOWNLOAD'])))
            if results.count(_RETURN_CODES['ERROR']) > 0:
                return ('Encountered {0} error(s) when downloading'.format(results.count(_RETURN_CODES['ERROR'])))
    else:
        return ('No result were found')

def REPLACE_NUMBERS(a):
    o = a
    for s, r in _NUMBER_CONV.items():
        o = str.replace(o, s, r)
    return o