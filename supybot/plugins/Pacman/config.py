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
    conf.registerPlugin('Pacman', True)


Pacman = conf.registerPlugin('Pacman')
# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(Pacman, 'someConfigVariableName',
#     registry.Boolean(False, """Help for someConfigVariableName."""))

conf.registerGroup(Pacman, 'pkg')
conf.registerGlobalValue(Pacman.pkg, 'max',
    registry.NonNegativeInteger(2, """Indique le maximum de paquets
		à afficher (commande 'pkg' et 'aur')."""))

conf.registerGroup(Pacman, 'pkgfile')
conf.registerGlobalValue(Pacman.pkgfile, 'max',
    registry.NonNegativeInteger(2, """Indique le maximum de paquets/fichiers
		à afficher."""))


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
