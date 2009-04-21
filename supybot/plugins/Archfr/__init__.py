# -*- coding: utf-8 -*-


###
# Copyright (c) 2009, Tuxce <tuxce.net@gmail.com>
# All rights reserved.
#
#
###


"""
Plugin Archfr.
Apporte une interactivité au chan #archlinux-fr@freenode
Fonctionnalités:
	wiki	-> effectue une recherche sur le wiki (fr/en)
	bug	-> recherche un ticket ouvert sur le bugtracker
	pkg 	-> recherche dans la base des paquets Arch Linux
	pkgfile	-> recherche un paquet contenant un fichier
	le bot permet également de répondre à certains phrase ou actions
"""

import supybot
import supybot.world as world

# Use this for the version of this plugin.  You may wish to put a CVS keyword
# in here if you're keeping the plugin in CVS or some similar system.
__version__ = "0.1"

# XXX Replace this with an appropriate author or supybot.Author instance.
__author__ = supybot.Author ('Tuxce', 'tuxce', 'tuxce.net@gmail.com')

# This is a dictionary mapping supybot.Author instances to lists of
# contributions.
__contributors__ = {}

# This is a url where the most recent plugin package can be downloaded.
__url__ = 'http://www.archlinux.fr/' 

import config
import plugin
import arch
reload(plugin) # In case we're being reloaded.
reload(arch)
# Add more reloads here if you add third-party modules and want them to be
# reloaded when this plugin is reloaded.  Don't forget to import them as well!

if world.testing:
    import test

Class = plugin.Class
configure = config.configure


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
