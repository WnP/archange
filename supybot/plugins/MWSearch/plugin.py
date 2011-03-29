# -*- coding: utf-8 -*-


###
# Copyright (c) 2011, Tuxce <tuxce.net@gmail.com>
#
#
###




import supybot.utils as utils
import supybot.conf as conf
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import mediawiki


class MWSearch(callbacks.Plugin):
	"""
	Plugin MWSearch.
	Permet de faire des recherches sur un mediawiki.
	Fonctionnalités:
		seach	-> effectue une recherche sur un site
	"""

	threaded = True

	def __init__(self, irc):
		self.__parent = super (MWSearch, self)
		self.__parent.__init__(irc)
		self.mws = { 'wiki.fr' : 
		    [mediawiki.Wiki ('http://wiki.archlinux.fr', '', '/api.php'), 'wiki.org'],
		    'wiki.org' : 
			[ mediawiki.Wiki ('https://wiki.archlinux.org', '/index.php', '/api.php'), None]
			}
		self.res_max = 2

	def search (self, irc, msg, args, site, nick, query):
		"""search <site> [nick] <terme>
		"""
		pages = None
		while not pages and site in self.mws.keys():
			mw = self.mws[site][0]
			site = self.mws[site][1]
			pages = mw.searchTitle (query)
			if not pages:
				pages = mw.searchText (query)
		if pages:
			irc.replies(pages[:self.res_max], to=nick)
		else:
			irc.reply("Pas de résultat", to=nick)
	
	search = wrap (search, ['somethingWithoutSpaces', optional ('nickInChannel'), 'text'])

Class = MWSearch

