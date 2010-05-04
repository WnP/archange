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
import supybot.schedule as schedule
import chiffre
import time

class Chiffre(callbacks.Plugin):
	"""
	Plugin Chiffre.
	"""
	threaded = True

	def __init__(self, irc):
		self.__parent = super (Chiffre, self)
		self.__parent.__init__(irc)
		self.c = chiffre.Chiffre ()
		self.en_cours = False
		self.tache = 0
		self.tries = False
		# scores: { nick: [ essais, réussis, gagnés ] } 
		self.scores = {}


	def _check_chan (self, msg):
		return self.registryValue ('game.enable', msg.args[0].split(',')[0])

	def _start (self, irc, prefix=True):
		if self.tache != 0:
			schedule.removeEvent(self.tache)
			self.tache = 0
		if self.en_cours:
			s = self.c.getSolution ()
			sr = ""
			if s[0] == 0:
				sr = "Le compte est bon: "
			else:
				sr = "Loin de %s: " % str(s[0])
			sr += "|".join (s[1])
			irc.reply (sr, prefixNick=False)
			self.en_cours = False
			if not self.tries:
				irc.reply ("Fin du jeu", prefixNick=prefix)
				return
		self.tries = False
		self.c.generate ()
		irc.reply (self.c.nombres, prefixNick=prefix)
		irc.reply ("Cible: %d" % self.c.res_cible, prefixNick=prefix)
		self.en_cours = True
		def f():
			self.tache = 0
			self._start (irc, prefix=False)
		self.tache = schedule.addEvent(f, time.time() + 300)
		
	def start (self, irc, msg, args):
		if not self._check_chan (msg) or self.en_cours:
			return
		self.tries = True
		self._start (irc)

	start = wrap (start)	

	def startw (self, irc, msg, args):
		if not self._check_chan (msg):
			return
		self.tries = True
		self._start (irc)

	startw = wrap (startw, ['admin'])	

	def what (self, irc, msg, args):
		if not self._check_chan (msg):
			return
		if not self.en_cours:
			return
		irc.reply (self.c.nombres)
		irc.reply ("Cible: %d" % self.c.res_cible)

	what = wrap (what)	

	def stop (self, irc, msg, args):
		if not self._check_chan (msg):
			return
		self.tries = False
		self._start(irc)
		self.en_cours = False

	stop = wrap (stop, ['admin'])	

	def _check_formula (self, irc, msg):
		if not self._check_chan (msg):
			return
		if not self.en_cours:
			return
		res = self.c.check_formula (msg.args[1])
		if res == 0:
			self.tries = True
			self.en_cours = False
			self._start (irc)
		elif res > 0:
			self.tries = True
			irc.reply ("loin de %d" % res)
		
	
	# doPrivmsg est lancé à chaque message
	def doPrivmsg(self, irc, msg):
		self._check_formula (irc, msg)

Class = Chiffre

