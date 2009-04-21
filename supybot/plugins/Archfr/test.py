# -*- coding: utf-8 -*-


###
# Copyright (c) 2009, Tuxce <tuxce.net@gmail.com>
# All rights reserved.
#
#
###


from supybot.test import *

class ArchfrTestCase(PluginTestCase):
    plugins = ('Archfr',)

    def testArchfr(self):
        # difficult to test, let's just make sure it works
        self.assertResponse('wiki gnome', 'Pas de résultat')
        self.assertNotError('wiki wiki_search gnome')
        self.assertNotError('bug hal fails with ntfs')
        self.assertNotError('pkgfile kernel')
        self.assertNotError('pkg kernel')
        self.assertNotError('pkgfile kernel')
        self.assertNotError('talk group list')
        self.assertError('talk list')
        self.assertError('talk group add')
        self.assertNotError('talk group add test')
        self.assertNotError('talk group del 1')

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
