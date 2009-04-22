# -*- coding: utf-8 -*-


###
# Copyright (c) 2009, Tuxce <tuxce.net@gmail.com>
#
#
###


from supybot.test import *

class GuardianTestCase(PluginTestCase):
    plugins = ('Guardian',)

    def testGuardian(self):
        # difficult to test, let's just make sure it works
        self.assertNotError('faudrait chercher comment tester...')

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
