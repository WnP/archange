# -*- coding: utf-8 -*-

###
# Copyright (c) 2011, Tuxce <tuxce.net@gmail.com>
#
#
###


import json
import sys
# Foutu changement de version avec changement d'API...
if sys.version_info < (2, 6, 0):
    json_load = json.read
else:
    json_load = json.loads
import urllib,urllib2

class Wiki:
    def __init__(self, url, index, api):
        self.wiki_url = url
        self.wiki_index = index
        self.wiki_api = api

    def search (self, srwhat, content):
        pages = []
        get_vars = {'format':  'json',
                    'action':  'query',
                    'list':    'search',
                    'srprop':  'size',
                    'srwhat':  srwhat,
                    'srsearch':content
                   }
        encoded_vars = urllib.urlencode (get_vars)
        try:
            fd = urllib2.urlopen (self.wiki_url +
                self.wiki_api + '?' + encoded_vars)
            res = json_load (fd.read())['query']['search']
            for page in res:
               if '(' in page['title']:
			       continue     # contournement pour les pages de localisation
               pages += [ self.wiki_url + self.wiki_index + '/' + page['title'].replace(' ', '_') ]
        except:
            pass
        return pages


    def searchTitle (self, title):
        return self.search ('title', title)

    def searchText (self, text):
        return self.search ('text', text)



# vim: set ts=4 sw=4 et:
