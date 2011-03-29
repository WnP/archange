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
import supybot.schedule as schedule
import time
import comparestrings



class Guardian(callbacks.Plugin):
	"""
	Plugin Guardian.
	Implémente une protection au bot.
	Flood / Répétition
	"""
	threaded = True
	noIgnore = True

	def __init__(self, irc):
		self.__parent = super (Guardian, self)
		self.__parent.__init__(irc)
		# Variable contenant des infos sur les nicks:
		# {nick: { channel : { "kick": nbre_kick,
		#					   "last_msg": msg,
		#                      "flood": flood_list, 
		#                      "repeat": repeat list }}}
		self.nicks = {}
		self.nicks_moderated = list ()
		self.t = 0
		self.m = 0


	def sameMsg (self, s1, s2):
		# TODO: fixer les seuils dans la config !
		if len (s1) > len (s2):
			p1 = s1
			p2 = s2
		else:
			p1 = s2
			p2 = s1
		t = len (p1) + 1.0
		m = comparestrings.compare (s1, s2)
		self.t = t
		self.m = m
		if m / t > 0.8: #0.75:
			return True
		else:
			return False
		m = t - len (p2)
		t *= 1.0
		if m / t > 0.9:
			return False
		j = 0
		for l in p2:
			if l != p1[j]:
				m += 1
			j += 1
		if m / t  < 0.1:
			return True
		return False

		
	def addNickMsg (self, nick, channel, msg):
		try:
			self.nicks[nick][channel]
		except:
			try:
				self.nicks[nick]
			except:
				self.nicks[nick] = {}
			self.nicks[nick][channel] = { "kick": 0, "last_msg": '',
					"flood": list (), "repeat": list () } 
		self.nicks[nick][channel]["flood"].append (int (time.time()))
		if not self.sameMsg (self.nicks[nick][channel]["last_msg"], msg):
			self.nicks[nick][channel]["repeat"] = list ()
			self.nicks[nick][channel]["last_msg"] = msg
		self.nicks[nick][channel]["repeat"].append (int (time.time()))
			


	def banNick (self, irc, channel, nick, period):
		# Inspiré de la fonction kban du plugin Channel
		banmask = irc.state.nickToHostmask(nick)
		if irc.state.channels[channel].isOp(nick):
			return
		else:
			irc.sendMsg(ircmsgs.ban(channel, banmask))
			if period > 0:
				def f():
					if channel in irc.state.channels and \
					   banmask in irc.state.channels[channel].bans:
						irc.sendMsg(ircmsgs.unban(channel, banmask))
				schedule.addEvent(f, time.time () + period)

	def removeNick (self, irc, channel, nick, reason):
		irc.sendMsg(ircmsgs.IrcMsg('remove %s %s : %s' % (channel, 
					nick, reason)))

	def kickNick (self, irc, channel, nick, reason, max, period):
		self.nicks[nick][channel]["kick"] += 1
		if max !=0  and self.nicks[nick][channel]["kick"] > max:
			self.nicks[nick][channel]["kick"] = 0
			self.banNick (irc, channel, nick, period)
		self.removeNick (irc, channel, nick, reason)


	def abus (self, tab, interval, max):
		while tab[len (tab) - 1] - tab[0] > interval:
			tab.pop (0)
		if len (tab) >= max:
			return True
		else:
			return False 


	def controle(self, irc, msg):
		(chans, text) = msg.args 
		for channel in chans.split (','):
			flood_enable = self.registryValue ('flood.enable', channel)
			repeat_enable = self.registryValue ('repeat.enable', channel)
			ctrl_types = []
			if flood_enable:
				ctrl_types += [ "flood" ]
			if repeat_enable:
				ctrl_types += [ "repeat" ]
			if not ctrl_types:
				continue
			self.addNickMsg (msg.nick, channel, text)
			for ctrl_type in ctrl_types:
				if self.abus (self.nicks[msg.nick][channel][ctrl_type],
					self.registryValue (ctrl_type + ".interval"),
					self.registryValue (ctrl_type + ".max")):


					self.kickNick (irc, channel, msg.nick,
							self.registryValue (ctrl_type + ".kickReason"),
							self.registryValue (ctrl_type + ".maxKick"),
							self.registryValue (ctrl_type + ".banPeriod"))
					# Réinitialise la liste de la fonction contrôlée... p-e
					# faudrait réinitialiser les 2 !
					self.nicks[msg.nick][channel][ctrl_type] = list ()
					break


	def voice_func (self, irc, msg, args, channel):
		"""[channel]
		Bascule tous les utilisateurs du canal en mode +v
		"""
		if not channel:
			channel = msg.args[0]
		users = []
		if channel in irc.state.channels:
			for user in irc.state.channels[channel].users:
				if user not in irc.state.channels[channel].voices \
					and user not in irc.state.channels[channel].ops \
					and user not in self.nicks_moderated:
					users += [user]
					if len(users) > 3:
						irc.queueMsg (ircmsgs.voices(channel, users))
						users = []
			if len(users) != 0:
				irc.queueMsg (ircmsgs.voices(channel, users))
 
 	voice = wrap(voice_func, [optional ('channel'), 'admin'])

	
	def moderate (self, irc, msg, args, channel, nick):
		"""[channel] nick
		Bascule tous les utilisateurs du canal en mode +v excépté 'nick' puis
		passe le canal en mode +m
		"""
		if not channel:
			channel = msg.args[0]
		if channel in irc.state.channels:
			# TODO: Spécifier la liste des nick au différents canaux
			self.nicks_moderated.append (nick)
			self.voice_func (irc, msg, args, channel)
			irc.queueMsg (ircmsgs.devoice(channel, nick))
			#self.removeNick (irc, channel, nick, "Avertissement")
			irc.queueMsg (ircmsgs.mode(channel, ['+m']))

	moderate = wrap(moderate, [optional ('channel'), 'nickInChannel','admin'])

	def rmnick (self, irc, msg, args, channel, nick, reason):
		"""[channel] nick reason
		Enlève l'utilisateur au lieu de le kicker, évite l'autojoin
		"""
		if not channel:
			channel = msg.args[0]
		self.removeNick (irc, channel, nick, reason)

	rmnick = wrap(rmnick, [optional ('channel'), 'nickInChannel', 'text', 'admin'])

	def unmoderate (self, irc, msg, args, channel, nick):
		"""[channel] nick
		Enlève l'utilisateur 'nick' de la liste des personnes modérés.
		"""
		# TODO: Spécifier la liste des nick au différents canaux
		try:
			self.nicks_moderated.remove (nick)
		except:
			pass
		irc.replySuccess ()

	unmoderate = wrap(unmoderate, [optional ('channel'), 'nickInChannel','admin'])

	# doPrivmsg est lancé à chaque message
	def doPrivmsg(self, irc, msg):
		self.controle (irc, msg)

Class = Guardian

