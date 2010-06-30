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
import ConfigParser
import re
import random

class Talk(callbacks.Plugin):
	"""
	Plugin Talk.
	"""
	threaded = True

	def __init__(self, irc):
		self.__parent = super (Talk, self)
		self.__parent.__init__(irc)
		random.seed()
		self.groups = {}
		# Le fichier de la base se trouve par défaut dans le rep 'data' de supybot
		self.loadConfig (conf.supybot.directories.data.dirize('talk.cfg'))

	def loadConfig (self, file=None):
		cfg = ConfigParser.RawConfigParser()
		if not file:
			file = self.file
		if not cfg.read (file):
			return False
		self.groups = {}
		for sect in cfg.sections():
			sect_valid = True
			self.groups[sect]={}
			self.groups[sect]['rules'] = []
			self.groups[sect]['replies'] = []
			try:
				for opt in cfg.items(sect):
					if opt[0][:4] == "rule":
						self.groups[sect]['rules'] += [re.compile (opt[1])]
					else if opt[0][:4] == "reply":
						self.groups[sect]['replies'] += [opt[1]]
					else:
						sect_valid = False
			except:
				del self.groups[sect]
				continue
			if not sect_valid:
				del self.groups[sect]
		return True

	def writeConfig (self, file=None):
		if not file:
			file = self.file
		try:
			fp = open (file, 'w')
		except IOError:
			print "Error: unable to write ", file
		cfg = ConfigParser.RawConfigParser()
		for sect, group in self.groups.items ():
			cfg.add_section (sect)
			i=0
			for rule in group['rules']:
				cfg.set (sect, 'rule' + str(i), rule.pattern)
				i+=1
			i=0
			for reply in group['replies']:
				cfg.set (sect, 'reply' + str(i), reply)
				i+=1
		cfg.write (fp)
		fp.close ()
			

	def reply (self, s):
		for i, group in self.groups.items():
			for rule in group['rules']:
				if rule.findall (s):
					return group['replies'][random.randint (0, len (group['replies']) - 1)]
		return False

	# doPrivmsg est lancé à chaque message
	def doPrivmsg(self, irc, msg):
		(recipients, text) = msg.args
		reply = self.reply (text)
		if reply:
			irc.reply (reply.replace ("%n", msg.nick), prefixNick=False)

Class = Talk

