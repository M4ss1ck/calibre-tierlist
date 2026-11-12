"""The labels the Page tab shows for each Page Defaults choice, built at call time so `_` translates them and
xgettext sees every one. Qt-free so tests can check them against the values Page Defaults accepts."""


def theme_choices() -> list[tuple[str, str]]:
    """The theme values with their labels."""
    return [('system', _('System')), ('light', _('Light')), ('dark', _('Dark'))]


def page_width_choices() -> list[tuple[str, str]]:
    """The Page Width values with their labels."""
    return [('narrow', _('Narrow')), ('normal', _('Normal')), ('wide', _('Wide')), ('full', _('Full window'))]


def gap_choices() -> list[tuple[str, str]]:
    """The Lane Gap and Cover Gap values with their labels."""
    return [('none', _('None')), ('small', _('Small')), ('normal', _('Normal')), ('large', _('Large'))]


def cover_size_choices() -> list[tuple[str, str]]:
    """The Cover Size values with their labels."""
    return [('small', _('Small')), ('normal', _('Normal')), ('large', _('Large'))]


def empty_lane_choices() -> list[tuple[str, str]]:
    """The Empty Lane Message modes with their labels."""
    return [('default', _('Default text')), ('hidden', _('Hidden')), ('custom', _('Custom'))]
