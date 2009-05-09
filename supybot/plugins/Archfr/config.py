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
    conf.registerPlugin('Archfr', True)


Archfr = conf.registerPlugin('Archfr')
# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(Archfr, 'someConfigVariableName',
#     registry.Boolean(False, """Help for someConfigVariableName."""))
conf.registerGroup(Archfr, 'wiki')
conf.registerGlobalValue(Archfr.wiki, 'max',
    registry.NonNegativeInteger(2, """Indique le maximum de pages
		à afficher."""))
conf.registerGlobalValue(Archfr.wiki, 'site',
    registry.SpaceSeparatedListOfStrings (['wiki_qsearch', 'wiki_search',
        'wiki_org'], """Indique la méthode de recherche par défaut de 
        la commande 'wiki'."""))

conf.registerGroup(Archfr, 'web')
conf.registerGlobalValue(Archfr.web, 'max',
    registry.NonNegativeInteger(2, """Indique le maximum de pages
		à afficher."""))
conf.registerGlobalValue(Archfr.web, 'site',
    registry.String ('scroogle', """Indique la méthode de recherche par
        défaut de la commande."""))

conf.registerGroup(Archfr, 'bug')
conf.registerGlobalValue(Archfr.bug, 'max',
    registry.NonNegativeInteger(2, """Indique le maximum de bugs
		à afficher."""))

conf.registerGroup(Archfr, 'pkg')
conf.registerGlobalValue(Archfr.pkg, 'max',
    registry.NonNegativeInteger(2, """Indique le maximum de paquets
		à afficher (commande 'pkg' et 'aur'."""))

conf.registerGroup(Archfr, 'pkgfile')
conf.registerGlobalValue(Archfr.pkgfile, 'max',
    registry.NonNegativeInteger(2, """Indique le maximum de paquets/fichiers
		à afficher."""))

conf.registerGroup(Archfr, 'quote')
conf.registerGlobalValue(Archfr.quote, 'theme',
    registry.String('chuck', """Indique le thème des citations.""",
        private=True))


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
