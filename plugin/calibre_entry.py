"""Zip root entry point: registers the Tier List plugin with calibre."""

from calibre.customize import InterfaceActionBase


class TierListPlugin(InterfaceActionBase):
    name = 'Tier List'
    description = _('Assign books a tier and compile a single offline, interactive HTML tier list of your series.')
    supported_platforms = ('windows', 'osx', 'linux')
    author = 'Andy Palmero'
    version = (0, 1, 0)
    minimum_calibre_version = (9, 0, 0)
    actual_plugin = 'calibre_plugins.tierlist.calibre_ui.action:TierListAction'
