# -*- coding: utf-8 -*-


###
# Copyright (c) 2009, Tuxce <tuxce.net@gmail.com>
#
#
###

import supybot.conf as conf
import supybot.registry as registry

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('Quote', True)


Quote = conf.registerPlugin('Quote')


conf.registerGlobalValue(Quote, 'theme',
    registry.String('chuck', """Indique le thème des citations.""",
        private=True))


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
