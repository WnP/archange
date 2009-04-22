# -*- coding: utf-8 -*-


###
# Copyright (c) 2009, Tuxce <tuxce.net@gmail.com>
#
#
###




import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs

import arch



class Guardian(callbacks.Plugin):
	"""
	Plugin Guardian.
	Implémente une protection au bot.
	Flood / Répétition
	"""
	threaded = True

	def __init__(self, irc):
		self.__parent = super (Guardian, self)
		self.__parent.__init__(irc)
		# Variable contenant des infos sur les nicks:
		# {nick: { channel : [ flood list, repeat [msg, time list] ] }}
		self.nicks = {}


	def ctrlAbus (self, tab, interval, max)
		while tab[len (tab) - 1] - tab[0] > interval:
			tab.pop (0)
		if len (tab) >= max:
			return True
		else:
			return False

	def flood(self, irc, msg):
		(chans, text) = msg.args
		for channel in chans.split (','):
			if not self.registryValue ('flood.enable', channel):
				continue
			try:
				self.nicks[msg.nick][channel]
			except:
				self.nicks[msg.nick] = {}
				self.nicks[msg.nick][channel] = [list (), ['', list()]]
			interval = self.registryValue ('flood.interval')
			max = self.registryValue ('flood.max')
			self.nicks[msg.nick][channel][0].append (int (time.time()))
			if self.ctrlAbus (self.nicks[msg.nick][channel][0],
					self.registryValue ('flood.interval'),
					self.registryValue ('flood.max')):
				# kick le boulet!
				#irc.sendMsg(ircmsgs.kick(recipients, msg.nick, "flood"))
				# remise à 0
				self.nicks[msg.nick][channel][0] = list ()


	def repeat(self, irc, msg):
		(chans, text) = msg.args
		for channel in chans.split (','):
			if not self.registryValue ('repeat.enable', channel):
				continue
			try:
				self.nicks[msg.nick][channel]
			except:
				self.nicks[msg.nick] = {}
				self.nicks[msg.nick][channel] = [list (), ['', list()]]
			if self.nicks[msg.nick][channel][1][0] != text:
				self.nicks[msg.nick][channel][1][0] = text
				self.nicks[msg.nick][channel][1][1] = list()
				self.nicks[msg.nick][channel][1][1].append (int (time.time()))
				# Pas besoin de contrôler, c'est le premier msg
			else:
				self.nicks[msg.nick][channel][1][1].append (int (time.time()))
				if self.ctrlAbus (self.nicks[msg.nick][channel][1][1],
						self.registryValue ('repeat.interval'),
						self.registryValue ('repeat.max')):
					# kick le boulet!
					#irc.sendMsg(ircmsgs.kick(recipients, msg.nick, "flood"))
					# remise à 0
					self.nicks[msg.nick][channel][1][0] = ''
					self.nicks[msg.nick][channel][1][1] = list()




		

	# doPrivmsg est lancé à chaque message
	def doPrivmsg(self, irc, msg):
		self.flood (irc, msg)
		self.repeat (irc, msg)

Class = Guardian

