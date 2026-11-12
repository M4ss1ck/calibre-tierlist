"""The Settings Page tab steps the settings itest drives: change some Page Defaults, then check OK stored them.

calibre runs Python with -OO, which strips ``assert``; callers pass their ``expect``.
"""

from collections.abc import Callable
from typing import Any

Expect = Callable[[bool, object], None]


def change_page_tab(page: Any, expect: Expect) -> None:
    """Pick a theme, a Cover Gap, Tier descriptions and a custom Empty Lane Message on the Page tab."""
    page.theme.setCurrentIndex(page.theme.findData('light'))
    page.covers.cover_gap.setCurrentIndex(page.covers.cover_gap.findData('large'))
    page.lanes.show_descriptions.setChecked(True)
    lanes = page.lanes
    expect(not lanes.empty_lane_text.isEnabled(), 'the custom message field is enabled for the Default text')
    lanes.empty_lane.setCurrentIndex(lanes.empty_lane.findData('custom'))
    expect(lanes.empty_lane_text.isEnabled(), 'choosing Custom did not enable the custom message field')
    lanes.empty_lane_text.setText('  Nothing yet  ')


def expect_page_stored(stored: Any, expect: Expect) -> None:
    """The Page Defaults OK stored are the ones `change_page_tab` picked."""
    picked = (stored.theme, stored.cover_gap, stored.show_descriptions, stored.empty_lane, stored.empty_lane_text)
    expect(picked == ('light', 'large', True, 'custom', 'Nothing yet'), f'OK stored the Page Defaults {picked}')
