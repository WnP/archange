# -*- coding: utf-8 -*-


###
# Copyright (c) 2009, Tuxce <tuxce.net@gmail.com>
#
#
###


from supybot.test import *

class PacmanTestCase(PluginTestCase):
    plugins = ('Pacman',)

    def testPacman(self):
        # difficult to test, let's just make sure it works
        self.assertNotError('pkgfile kernel')
        self.assertNotError('pkg kernel')
        self.assertNotError('pkgfile kernel')

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
