# -*- coding: utf-8 -*-


###
# Copyright (c) 2009, Tuxce <tuxce.net@gmail.com>
#
#
###




import supybot.utils as utils
import supybot.conf as conf
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
# installation de pywebsearch nécessaire
import websearch


class WebSearch(callbacks.Plugin):
	"""
	Plugin WebSearch.
	Permet de faire des recherches sur le web.
	Fonctionnalités:
		seach	-> effectue une recherche sur un site
		config	-> configure le plugin
	"""

	threaded = True

	def __init__(self, irc):
		self.__parent = super (WebSearch, self)
		self.__parent.__init__(irc)
		self.wq = websearch.WebSearch (conf.supybot.directories.data.dirize('websearch.cfg'))

	def load(self, irc, msg, args, file):
		if file.find ("/") != -1:
			irc.reply("'%s' n'est pas un fichier valable" % file) 
			return 
		if self.wq.loadConfig (conf.supybot.directories.data.dirize(file)):
			irc.replySuccess()
		else:
			irc.reply("Erreur lors du chargement de '%s'" % file) 

	def save(self, irc, msg, args, file):
		if file.find ("/") != -1:
			irc.reply("'%s' n'est pas un fichier valable" % file) 
			return 
		if self.wq.writeConfig (conf.supybot.directories.data.dirize(file)):
			irc.replySuccess()
		else:
			irc.reply("Erreur lors de la sauvegarde de '%s'" % file) 
			


	def search (self, irc, msg, args, site, nick, query):
		if site not in self.wq.getSites():
			irc.reply("'%s' n'est pas configuré" % site) 
			return 
		pages = self.wq.search (site, query)
		if pages:
			replies = []
			for page in pages:
				replies += page
			irc.replies(replies, to=nick)
		else:
			irc.reply("Pas de résultat", to=nick)
	
	search = wrap (search, ['somethingWithoutSpaces', optional ('nickInChannel'),	'text'])

	def max (self, irc, msg, args, site, m):
		if site not in self.wq.getSites():
			irc.reply("'%s' n'est pas configuré" % site) 
			return 
		self.wq.setSiteMax (site, m)
		irc.replySuccess()

	
		
	max = wrap (max, ['somethingWithoutSpaces', 'int'])



Class = WebSearch

