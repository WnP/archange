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
    conf.registerPlugin('Guardian', True)


Guardian = conf.registerPlugin('Guardian')
# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(Guardian, 'someConfigVariableName',
#     registry.Boolean(False, """Help for someConfigVariableName."""))
conf.registerGroup(Guardian, 'flood', private=True)
conf.registerGlobalValue(Guardian.flood, 'interval',
    registry.NonNegativeInteger(7, """Indique l'interval de temps de contrôle
        du flood (en sec)."""))
conf.registerGlobalValue(Guardian.flood, 'max',
    registry.NonNegativeInteger(5, """Indique le nombre de message maximum.
        """))
conf.registerGlobalValue(Guardian.flood, 'maxKick',
    registry.NonNegativeInteger(5, """Indique le nombre de kick minimum avant
    un bannissement."""))
conf.registerGlobalValue(Guardian.flood, 'banPeriod',
    registry.NonNegativeInteger(3600, """Période de bannissement en secondes.
        """))
conf.registerChannelValue(Guardian.flood, 'enable',
    registry.Boolean (False, """Active le contrôle du flood."""))
conf.registerGlobalValue(Guardian.flood, 'kickReason',
    registry.String ("cf. pastebin", """L'insulte (amicale bien sûr) à envoyer au
        boulet (en le kickant évidemment)."""))

conf.registerGroup(Guardian, 'repeat', private=True)
conf.registerGlobalValue(Guardian.repeat, 'interval',
    registry.NonNegativeInteger(20, """Indique l'interval de temps de contrôle
        de la répétition (en sec)."""))
conf.registerGlobalValue(Guardian.repeat, 'max',
    registry.NonNegativeInteger(4, """Indique le nombre de message maximum.
        """))
conf.registerGlobalValue(Guardian.repeat, 'maxKick',
    registry.NonNegativeInteger(5, """Indique le nombre de kick minimum avant
    un bannissement."""))
conf.registerGlobalValue(Guardian.repeat, 'banPeriod',
    registry.NonNegativeInteger(3600, """Période de bannissement en secondes.
        """))
conf.registerChannelValue(Guardian.repeat, 'enable',
    registry.Boolean (False, """Active le contrôle de répétition."""))
conf.registerGlobalValue(Guardian.repeat, 'kickReason',
    registry.String ("C'est bon, on a compris!", """L'insulte (amicale bien sûr) à envoyer au
        boulet (en le kickant évidemment)."""))

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
