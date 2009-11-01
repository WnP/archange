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
# installation de pyarchlinux et pywebsearch nécessaire
import archlinux
import random


class Pacman(callbacks.Plugin):
	"""
	Plugin Pacman.
	Apporte une interactivité au chan #archlinux-fr@freenode
	Fonctionnalités:
		pkg 	-> recherche dans la base des paquets Arch Linux
		pkgfile	-> recherche un paquet contenant un fichier
	"""
	threaded = True

	def __init__(self, irc):
		self.__parent = super (Pacman, self)
		self.__parent.__init__(irc)
		random.seed()
		# Le fichier de la base se trouve par défaut dans le rep 'data' de supybot
		self.ap = archlinux.PacmanDB (conf.supybot.directories.data.dirize('Pacman.sqlite'))
		self.aur_site = archlinux.Aur ()


	def die(self):
		self.ap.setDB (None)
		del self.ap

	# La fonction est appelée par 'pkg', d'où la différence de nom avec la
	# commande IRC.
	def aur_func(self, irc, msg, args, nick, query):
		"""[nick] terme
		Recherche un paquet correspondant à 'terme' dans AUR.
		"""
		max = self.registryValue ('pkg.max')
		pkgs = self.aur_site.search (query)
		if pkgs:
			replies = []
			for pkg in pkgs:
				replies += [pkg[0] + ' ' + pkg[1] + ' ' + 
						self.aur_site.getPkgUrl(pkg[2])]
			irc.replies(replies[:max], to=nick)
		else:
			irc.reply("Pas de résultat", to=nick)

	aur = wrap (aur_func, [optional ('nickInChannel'), 'text'])

	def _pkgfile(self, irc, msg, args, nick, query):
		"""[nick] path
		Recherche un paquet dont un fichier correspond à 'path'.
		"""
		max = self.registryValue ('pkgfile.max')
		pkgs = self.ap.searchFile (query, max)
		#irc.reply (pkgs)
		if not pkgs:
			irc.reply("Pas de résultat", to=nick)
		else:
			# arch.ArchPackage.searchFile retourne une liste de lignes
			# chaque ligne:
			#  nom du dépot
			#  nom du paquet
			#  version du paquet
			#  release du paquet
			#  chemin du fichier
			reply = []
			for pkg in pkgs:
				reply += [pkg[0] + ' / ' + pkg[1] + ' ' + pkg[2] + '-' + pkg[3] + ' ' + pkg[4]]
			irc.replies(reply, to=nick)

	def filelike(self, irc, msg, args, nick, query):
		"""[nick] path
		Recherche un paquet dont un fichier correspond à 'path'.
		'path' étant un motif compris par la syntaxe SQL LIKE.
		"""
		self._pkgfile (irc, msg, args, nick, query)

	filelike = wrap (filelike, [optional ('nickInChannel'), 'text'])

	def pkgfile(self, irc, msg, args, nick, query):
		"""[nick] path
		Recherche un paquet dont un fichier correspond à *'path'*.
		"""
		self._pkgfile (irc, msg, args, nick, "%" + query + "%")

	pkgfile = wrap (pkgfile, [optional ('nickInChannel'), 'text'])

	def pkg(self, irc, msg, args, nick, query):
		"""[nick] terme
		Recherche un paquet correspondant à 'terme', ou '*terme*' et bascule 
		éventuellement sur AUR.
		"""
		max = self.registryValue ('pkg.max')
		# Cherche une correpondance exact.
		pkgs = self.ap.getPkg (query)
		if not pkgs:
			# Sinon bascule sur une recherche à la pacman -Ss
			pkgs = self.ap.searchPkg (query)
		if not pkgs:
			# Et enfin bascule sur aur
			self.aur_func (irc, msg, args, nick, query)
		else:
			# arch.ArchPackage.searchPkg retourne une liste de lignes
			# chaque ligne:
			#  nom du dépot
			#  nom du paquet
			#  version du paquet
			#  release du paquet
			#  description du paquet
			reply = []
			for pkg in pkgs:
				reply += [pkg[0] + ' / ' + pkg[1] + ' ' + pkg[2] + '-' + pkg[3] + ' (' + pkg[4] + ')']
			irc.replies(reply[:max], to=nick)

	pkg = wrap (pkg, [optional ('nickInChannel'), 'text'])

	def pkgsync(self, irc, msg, args):
		"""Recharge la base des paquets/fichiers
		"""
		self.ap.sync()
		irc.replySuccess()
		
	pkgsync = wrap (pkgsync, ['admin'])


Class = Pacman

