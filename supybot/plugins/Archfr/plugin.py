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
import arch
import random



class Archfr(callbacks.Plugin):
	"""
	Plugin Archfr.
	Apporte une interactivité au chan #archlinux-fr@freenode
	Fonctionnalités:
		wiki	-> effectue une recherche sur le wiki (fr/en)
		bug		-> recherche un ticket ouvert sur le bugtracker
		pkg 	-> recherche dans la base des paquets Arch Linux
		pkgfile	-> recherche un paquet contenant un fichier
		le bot permet également de répondre à certains phrase ou actions
	"""
	# Sqlite ne gère pas les thread, et de toute façon, pour l'instant,
	# le module arch n'est pas fait pour.
	threaded = False

	def __init__(self, irc):
		self.__parent = super (Archfr, self)
		self.__parent.__init__(irc)
		random.seed()
		# Le fichier de la base se trouve par défaut dans le rep 'data' de supybot
		arch.ArchDB._file = conf.supybot.directories.data.dirize('Archfr.sqlite')
		self.wq = arch.WebQuery ()
		self.ap = arch.ArchPackage ()
		self.reply = arch.Reply ()
		# Variables pour les citations
		self.quote_file = None
		self.quote_fd = None
		self.quote_theme = ''

	
	def wiki(self, irc, msg, args, site, nick, query):
		"""[site] [nick] terme
		Recherche dans 'site' une page correspondant à
		'terme'.
		"""
		if site is None:
			sites = self.registryValue ('wiki.site')
		else:
			sites = [site]
		max = self.registryValue ('wiki.max')
		for site in sites: 
			pages = self.wq.getPages (site, query)
			if pages is None:
				continue
			else:
				replies = []
				for page in pages:
					# TODO: modifier l'accès direct à la var WebQuery.sites !
					replies += [self.wq.sites[site][1] + page[0]]
				irc.replies(replies[:max], to=nick)
				return
		irc.reply("Pas de résultat", to=nick)

	wiki = wrap (wiki, [optional (('literal', 
		('wiki_qsearch', 'wiki_search', 'wiki_org'))),
		optional ('nickInChannel'),	'text'])

	def bug(self, irc, msg, args, nick, query):
		"""[nick] terme
		Recherche un bug correspondant à 'terme'.
		"""
		site = 'bugs_org'
		max = self.registryValue ('bug.max')
		pages = self.wq.getPages (site, query)
		if pages is None:
			irc.reply("Pas de résultat", to=nick)
		else:
			replies = []
			for page in pages:
				replies += [self.wq.sites[site][1] + page[0]]
			irc.replies(replies[:max], to=nick)

	bug = wrap (bug, [optional ('nickInChannel'), 'text'])

	def pkgfile(self, irc, msg, args, nick, query):
		"""[nick] path
		Recherche un paquet dont un fichier correspond à *'path'*.
		"""
		max = self.registryValue ('pkgfile.max')
		pkgs = self.ap.searchFile (query, max)
		if not pkgs:
			irc.reply("Pas de résultat", to=nick)
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

	pkgfile = wrap (pkgfile, [optional ('nickInChannel'), 'text'])

	def pkg(self, irc, msg, args, nick, query):
		"""[nick] path
		Recherche un paquet dont un fichier correspond à *'path'*.
		"""
		max = self.registryValue ('pkg.max')
		pkgs = self.ap.searchPkg (query, max)
		if not pkgs:
			irc.reply("Pas de résultat", to=nick)
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

	pkg = wrap (pkg, [optional ('nickInChannel'), 'text'])

	def pkgsync(self, irc, msg, args):
		"""Recharge la base des paquets/fichiers
		"""
		self.ap.sync()
		irc.replySuccess()
		
	pkgsync = wrap (pkgsync, ['admin'])


	# La fonction qui tue... (surtout parce que je sais pas du tout comment 
	# faire pour qu'elle soit plus ou moins simple!)
	# "talk" pour gérer les réponses du bot.
	# usage:
	#	talk <group|rule|reply> <add|del|list> [id] [content]
	def talk (self, irc, msg, args, context, action, id, content):
		"""<group|rule|reply> <add|del|list> [id] [content]
		Configure les réponses du bot.
		"""
		def list (func):
			ret = []
			tab = func()
			if tab is not None:
				for line in tab:
					if len(line) > 2:
						ret += ["(" + str (line[0]) + ") " + line[1] + "(" + str(line[2]) + ")"]
					else:
						ret += ["(" + str (line[0]) + ") " + line[1]]
			return ret

		if action == 'list':
			ret = list ({'group': self.reply.listGroup,
					'rule': self.reply.listRule,
					'reply': self.reply.listReply}[context])
			if not ret:
				ret = ["Pas d'éléments"]
			irc.replies (ret)
		elif action == 'del':
			if not id:
				irc.error ("L'action 'del' requiert un 'id'", Raise=True)
			else:
				{'group': self.reply.delGroup,
						'rule': self.reply.delRule ,
						'reply': self.reply.delReply}[context](id)
				irc.replySuccess()
		elif action == 'add':
			if (context != 'group' and not id) or not content:
				irc.error ("Arguments invalides -> help talk", Raise=True)
			else:
				if context == 'group':
					ret = self.reply.addGroup (content)
				elif context == 'rule':
					ret = self.reply.addRule (id, content)
				elif context == 'reply':
					ret = self.reply.addReply (id, content)
				if ret:
					irc.replySuccess()
				else:
					irc.error('Erreur :/', Raise=True)

	talk = wrap (talk, ['admin', ('literal', ('group', 'rule', 'reply')),
		('literal', ('add', 'del', 'list')),
		optional('id'), optional ('text')])

	def quote(self, irc, msg, args):
		theme = self.registryValue ('quote.theme')
		if theme == '':
			irc.error ("Pas de thème!")
			return
		if self.quote_theme != theme:
			if self.quote_fd is not None:
				self.quote_fd.close ()
			self.quote_theme = theme
			self.quote_file = conf.supybot.directories.data.dirize(theme)
			self.quote_index = [0]
			try:
				self.quote_fd = open (self.quote_file)
			except:
				self.quote_fd = None
				self.quote_theme = ''
				irc.error ("Le thème sélectionné n'existe pas!")
				return
			line = '-'
			while line != '':
				line =  self.quote_fd.readline ()
				if line != '' and (line == '%\n' or line == '%'):
					self.quote_index += [self.quote_fd.tell()]
		if self.quote_fd:
			# Se positionne à une ligne au pif
			self.quote_fd.seek (self.quote_index[random.randint (0,
				len (self.quote_index) - 1)])
			# Passe les '%'
			self.quote_fd.readline ()
			self.quote_fd.readline ()
			line = '-'
			reply = ''
			while line != '' and line != '%' and line != '%\n':
				line =  self.quote_fd.readline ()
				if line != '' and line != '%' and line != '%\n':
					reply += line
			if reply != '':
				irc.reply (reply[:-1])
	quote = wrap (quote, [])

	# doPrivmsg est lancé à chaque message
	def doPrivmsg(self, irc, msg):
		(recipients, text) = msg.args
		reply = self.reply.randomReply (text)
		if reply:
			irc.reply (reply.replace ("%n", msg.nick), prefixNick=False)

Class = Archfr

