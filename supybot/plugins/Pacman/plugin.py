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
		pkg     -> recherche dans la base des paquets Arch Linux
		pkgfile	-> recherche un paquet contenant un fichier
	"""
	threaded = True

	def __init__(self, irc):
		self.__parent = super (Pacman, self)
		self.__parent.__init__(irc)
		random.seed()
		# Le fichier de la base se trouve par défaut dans le rep 'data' de supybot
		self.ap = archlinux.PacmanDB (conf.supybot.directories.data.dirize('repos'))
		archs=('i686', 'x86_64',)
		repos=('core', 'extra', 'community',)
		for repo in repos:
			for arch in archs:
				self.ap.addRepo (repo, arch, 'http://mir.archlinux.fr/' + repo + '/os/' + arch + '/' + repo + '.files.tar.gz')
		repo='archlinuxfr'
		for arch in archs:
			self.ap.addRepo (repo, arch, 'http://repo.archlinux.fr/' + arch + '/' + repo + '.files.tar.gz')
		self.aur_site = archlinux.Aur ()


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
				replies += [pkg.name + ' ' + pkg.ver + ' ' + 
						self.aur_site.getPkgUrl(pkg.Id)]
			irc.replies(replies[:max], to=nick)
		else:
			irc.reply("Pas de résultat", to=nick)

	aur = wrap (aur_func, [optional ('nickInChannel'), 'text'])

	def pkgfile(self, irc, msg, args, arch, nick, query):
		"""[nick] path
		Recherche un paquet dont un fichier correspond à 'path'.
		"""
		max = self.registryValue ('pkgfile.max')
		pkgs = self.ap.searchFile (arch, query, max)
		#irc.reply (pkgs)
		if not pkgs:
			irc.reply("Pas de résultat", to=nick)
		else:
			reply = []
			for pkg in pkgs:
				reply += [pkg.repo + ' / ' + pkg.name + ' ' + pkg.ver + ' ' + pkg.files[0]]
			irc.replies(reply, to=nick)

	pkgfileany = wrap (pkgfile, [('literal', ('i686', 'x86_64')), optional ('nickInChannel'), 'text'])

	def pkg(self, irc, msg, args, arch, nick, query):
		"""[nick] terme
		Recherche un paquet correspondant à 'terme', ou '*terme*' et bascule 
		éventuellement sur AUR.
		"""
		max = self.registryValue ('pkg.max')
		# Cherche une correpondance exact.
		pkgs = self.ap.getPkg (arch, query, max)
		if pkgs is None: return
		if not pkgs:
			# Sinon bascule sur une recherche à la pacman -Ss
			pkgs = self.ap.searchPkg (arch, query, max)
		if pkgs is None: return
		if not pkgs:
			# Et enfin bascule sur aur
			self.aur_func (irc, msg, args, nick, query)
		else:
			reply = []
			for pkg in pkgs:
				reply += [pkg.repo + ' / ' + pkg.name + ' ' + pkg.ver + ' (' + pkg.description + ')']
			irc.replies(reply, to=nick)

	pkgany = wrap (pkg, [('literal', ('i686', 'x86_64')), optional ('nickInChannel'), 'text'])

	def pkgsync(self, irc, msg, args):
		"""Recharge la base des paquets/fichiers
		"""
		self.ap.sync()
		irc.replySuccess()
		
	pkgsync = wrap (pkgsync, ['admin'])


Class = Pacman

