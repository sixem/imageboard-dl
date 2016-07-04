#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import utils
import re

box = [
       [],
       [],
       [],
       []
       ]
    
def establish(a, site, uniq=None):
    box = [[], [], [], []]
    request = utils.REQUEST(a)
    if request[0] is not False:
        utils.REPORT(site, 'Successfully retrieved page ..')
        return request[1]
    else:
        utils.REPORT(site, 'Encountered an error when requesting page (Code: {})'.format(request[1]))
        if request[1] in utils._POSSIBLE_REASONS:
            utils.REPORT(site, 'Possible reasons:')
            for reason in utils._POSSIBLE_REASONS[request[1]]:
                utils.REPORT(site, reason)
        return False
    return False

def masterchan(a, site="masterchan", uniq=None):
    p = establish(a, site)
    if p is not False:
        media = BeautifulSoup(p, "html.parser").findAll("span", {"class" : "mediaFileAttrb"})
        for m in media:
            filename = m.find("span", {"class" : "mediaFileName"}).contents[0].__str__()
            url = m.find("a", {"class" : "hyperlinkMediaFileName"})['href'].__str__()
            values = [site, utils._GENERAL['directory_format'].format(site, "123123123"), url, filename]
            for i in range(0, 4):
                box[i].append(values[i])
        return box
    else:
        return False

def arhivach(a, site="arhivach", uniq=None):
    p = establish(a, site)
    if p is not False:
        images = BeautifulSoup(p, "html.parser").findAll("a", {"class" : ["img_filename"]})
        if uniq is None:
            rm = re.search(utils._REGEX_TABLE['arhivach'], a)
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
                values = [site, utils._GENERAL['directory_format'].format(site, uniq), url, None]
                for i in range(0, 4):
                    box[i].append(values[i])
        return box
    else:
        return False

def librechan(a, site="librechan"):
    p = establish(a, site)
    if p is not False:
        wrapper = BeautifulSoup(p, "html.parser")
        fi = wrapper.findAll("p", {"class" : "fileinfo"})
        ti = wrapper.find("div", {"class" : "thread"}).find("a", {"class" : "post_anchor"})
        for f in fi:
            values = [site, utils._GENERAL['directory_format'].format(site, ti['id'].__str__()), 
                'https://librechan.net{0}'.format(f.find("a")['href'].__str__()),
                f.find("a").contents[0].__str__()]
            for i in range(0, 4):
                box[i].append(values[i])
        return box
    return False

def twochhk(a, site="2chhk"):
    p = establish(a, site)
    rm = re.search(utils._REGEX_TABLE['2chhk'], a)
    if rm:
        const_url = ('{0}2ch.hk/{1}/src/{2}/'.format(rm.group(2), rm.group(3), rm.group(5)))
        if p is not False:
            box = [[], [], [], []]
            wrapper = BeautifulSoup(p, "html.parser").findAll("div", {"class" :
                ["post-wrapper", "oppost-wrapper"]})
            for post in wrapper:
                desks = post.findAll("a", {"class" : ["desktop"]})
                for desk in desks:
                    values = [site, utils._GENERAL['directory_format'].format(site, rm.group(5)),
                        const_url + desk.contents[0].__str__(), desk.contents[0].__str__()]
                    for i in range(0, 4):
                        box[i].append(values[i])
            return box
        else:
            return False
    else:
        raise ValueError('Could not parse URL data')
        return False
    return False
    
def fourchan(a, site="4chan"):
    p = establish(a, site)
    if p is not False:
        wrapper = BeautifulSoup(p, "html.parser")
        posts = wrapper.findAll("div", {"class" : ["postContainer", "opContainer"]})
        ti = wrapper.find("div", {"class" : "thread"})['id'].__str__()
        for post in posts:
            file_info = post.findAll("div", {"class" : ["fileText"]})
            for fi in file_info:
                filename = fi.find("a").contents[0].__str__()
                url = utils.FIX_URL(fi.find("a")['href'])
                values = [site, utils._GENERAL['directory_format'].format(site, ti),
                    url, filename]
                for i in range(0, 4):
                    box[i].append(values[i])
        return box
    else:
        return False
    return False
    
def eightchan(a, site="8chan"):
    p = establish(a, site)
    if p is not False:
        wrapper = BeautifulSoup(p, "html.parser")
        fi = wrapper.findAll("p", {"class" : "fileinfo"})
        ti = wrapper.find("div", {"class" : "thread"}).find("a", {"class" : "post_anchor"})
        for f in fi:
            filename = f.find("span", {"class" : "unimportant"}).find("span", {"class" : "postfilename"}).contents[0].__str__()
            url = f.find("a")['href'].__str__()
            values = [site, utils._GENERAL['directory_format'].format(site, ti['id']),
                url, filename]
            for i in range(0, 4):
                box[i].append(values[i])
        return box
    return False

def fourplebs(a, site="4plebs"):
    p = establish(a, site)
    if p is not False:
        wrapper = BeautifulSoup(p, "html.parser")
        image_links = wrapper.findAll("a", {"class" : "thread_image_link"})
        ti = wrapper.find("article")['data-thread-num']
        for link in image_links:
            values = [site, utils._GENERAL['directory_format'].format(site, ti), link['href'].__str__(), None]
            for i in range(0, 4):
                box[i].append(values[i])
        return box
    return False