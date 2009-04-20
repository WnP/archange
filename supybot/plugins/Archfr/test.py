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
        self.assertNotError('wiki gnome')

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
