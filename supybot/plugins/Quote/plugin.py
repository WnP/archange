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
import random

class Quote(callbacks.Plugin):
	"""
	Plugin Quote.
	"""
	threaded = True

	def __init__(self, irc):
		self.__parent = super (Quote, self)
		self.__parent.__init__(irc)
		random.seed()
		self.groups = {}
		self.quote_file = None
		self.quote_fd = None
		self.quote_theme = ''

	def die(self):
		if self.quote_fd is not None:
			self.quote_fd.close ()


	def quote(self, irc, msg, args):
		"""
		Affiche une citation.
		"""
		theme = self.registryValue ('theme')
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
				irc.reply (reply[:-1], prefixNick=False)
	quote = wrap (quote, [])


Class = Quote

