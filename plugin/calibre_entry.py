"""Zip root entry point: registers the Tier List plugin with calibre."""

from typing import Any

from calibre.customize import InterfaceActionBase


class TierListPlugin(InterfaceActionBase):
    name = 'Tier List'
    description = _('Assign books a tier and compile a single offline, interactive HTML tier list of your series.')
    supported_platforms = ('windows', 'osx', 'linux')
    author = 'Andy Palmero'
    version = (
        0,  # x-release-please-major
        3,  # x-release-please-minor
        0,  # x-release-please-patch
    )
    minimum_calibre_version = (9, 0, 0)
    actual_plugin = 'calibre_plugins.tierlist.calibre_ui.action:TierListAction'

    def is_customizable(self) -> bool:
        """True: Preferences > Plugins > Tier List > Customize opens the Tier Config dialog."""
        return True

    def config_widget(self) -> Any:
        """The Tier Config dialog widget, over the library the running calibre window shows."""
        from calibre.gui2.ui import get_gui
        from calibre_plugins.tierlist.calibre_ui.config_widget import ConfigWidget

        return ConfigWidget(get_gui())

    def save_settings(self, config_widget: Any) -> None:
        """Store what the config dialog gathered, once calibre accepts it."""
        config_widget.save()
