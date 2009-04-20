# -*- coding: utf-8 -*-


###
# Copyright (c) 2009, Tuxce <tuxce.net@gmail.com>
# All rights reserved.
#
#
###




import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import arch



class Archfr(callbacks.Plugin):
	"""Add the help for "@plugin help Archfr" here
	This should describe *how* to use this plugin."""
	# Sqlite ne gère pas les thread, et de toute façon, pour l'instant,
	# le module arch n'est pas fait pour.
	threaded = False

	def __init__(self, irc):
		self.__parent = super (Archfr, self)
		self.__parent.__init__(irc)
		self.wq = arch.WebQuery ()
		self.ap = arch.ArchPackage ()
		self.reply = arch.Reply ()

	
	def wiki(self, irc, msg, args, site, nick, query):
		"""[site] [nick] terme
		Recherche dans 'site' une page correspondant à
		'terme'.
		"""
		if site is None:
			site = self.registryValue ('wiki.site')
		max = self.registryValue ('wiki.max')
		pages = self.wq.getPages (site, query)
		if pages is None:
			irc.replies("Pas de résultat", to=nick)
		else:
			irc.replies(pages[:max], to=nick)

	wiki = wrap (wiki, [optional (('literal', 
		('wiki_qsearch', 'wiki_search', 'wiki_org'))),
		optional ('nickInChannel'),
		'text'])

	def bug(self, irc, msg, args, site, nick, query):
		"""[nick] terme
		Recherche un bug correspondant à 'terme'.
		"""
		max = self.registryValue ('bug.max')
		pages = self.wq.getPages ('bugs_org', query)
		if pages is None:
			irc.replies("Pas de résultat", to=nick)
		else:
			irc.replies(pages[:max], to=nick)

	bug = wrap (bug, [optional ('nickInChannel'),
		'text'])

	def pkgfile(self, irc, msg, args, nick, query):
		"""[nick] path
		Recherche un paquet dont un fichier correspond à *'path'*.
		"""
		max = self.registryValue ('pkgfile.max')
		pkgs = self.ap.searchFile (query, max)
		if pkgs is None:
			irc.replies("Pas de résultat", to=nick)
		else:
			# arch.ArchPackage.searchFile retourne une liste de lignes
			# chaque ligne:
			#  nom du dépot
			#  nom du paquet
			#  version du paquet
			#  chemin du fichier
			reply = []
			for pkg in pkgs:
				reply += [pkg[0] + '/' + pkg[1] + '-' + pkg[2] + ' ' + pkg[3]]
			irc.replies(reply, to=nick)

	pkgfile = wrap (pkgfile, [optional ('nickInChannel'),
		'text'])

	def pkg(self, irc, msg, args, nick, query):
		"""[nick] path
		Recherche un paquet dont un fichier correspond à *'path'*.
		"""
		max = self.registryValue ('pkg.max')
		pkgs = self.ap.searchPkg (query, max)
		if pkgs is None:
			irc.replies("Pas de résultat", to=nick)
		else:
			# arch.ArchPackage.searchPkg retourne une liste de lignes
			# chaque ligne:
			#  nom du dépot
			#  nom du paquet
			#  version du paquet
			reply = []
			for pkg in pkgs:
				reply += [pkg[0] + '/' + pkg[1] + '-' + pkg[2]]
			irc.replies(reply, to=nick)

	pkg = wrap (pkg, [optional ('nickInChannel'),
		'text'])


	# doPrivmsg est lancé à chaque message
	def doPrivmsg(self, irc, msg):
		(recipients, text) = msg.args
		reply = self.reply.randomReply (text)
		if reply:
			irc.reply (reply.replace ("%n", msg.nick), prefixNick=False)

Class = Archfr



	
