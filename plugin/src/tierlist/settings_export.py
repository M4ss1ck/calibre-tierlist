"""Settings Export: the JSON file that carries Tier Config, Page Defaults, and optional Overrides and Lane Order."""

import builtins
import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, cast

from .lane_order import Place, load_order, place_from_dict, place_to_dict, prune, save_order
from .page_defaults import PageDefaults
from .ports import Library, Prefs
from .series_tiers import load_overrides, save_overrides
from .tiers import TierConfig, TierConfigError, parse_config_data

KIND = 'tierlist-settings'
VERSION = 1


def _untranslated(text: str) -> str:
    return text


# calibre installs `_` as a builtin at runtime; pytest has none.
_ = getattr(builtins, '_', _untranslated)


@dataclass(frozen=True)
class SettingsExport:
    """One library's exported settings; a section that is None was absent and leaves the stored value unchanged."""

    tier_config: TierConfig | None = None
    page_defaults: PageDefaults | None = None
    overrides: dict[str, str] | None = None
    lane_order: dict[str, list[Place]] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialise to the JSON shape a Settings Export file holds."""
        data: dict[str, Any] = {'kind': KIND, 'version': VERSION}
        if self.tier_config is not None:
            data['tier_config'] = self.tier_config.to_dict()
        if self.page_defaults is not None:
            data['page_defaults'] = self.page_defaults.to_dict()
        if self.overrides is not None:
            data['overrides'] = dict(self.overrides)
        if self.lane_order is not None:
            data['lane_order'] = {
                lane: [place_to_dict(place) for place in places] for lane, places in self.lane_order.items()
            }
        return data


def dump_export(export: SettingsExport) -> str:
    """Serialise a Settings Export as the indented JSON the Export tab writes."""
    return json.dumps(export.to_dict(), indent=2)


def export_settings(prefs: Prefs, config: TierConfig, defaults: PageDefaults, include: bool) -> str:
    """The Settings Export JSON for these settings, with Overrides and Lane Order when asked."""
    overrides = load_overrides(prefs) if include else None
    order = load_order(prefs) if include else None
    return dump_export(SettingsExport(config, defaults, overrides, order))


def stored_extras(prefs: Prefs) -> SettingsExport:
    """The Overrides and Lane Order stored now, which an import of them would replace."""
    return SettingsExport(overrides=load_overrides(prefs), lane_order=load_order(prefs))


def apply_import(prefs: Prefs, library: Library, export: SettingsExport) -> None:
    """Replace the stored Overrides and Lane Order the export carries, then prune stale places."""
    if export.overrides is not None:
        save_overrides(prefs, export.overrides)
    if export.lane_order is not None:
        save_order(prefs, export.lane_order)
    if export.overrides is not None or export.lane_order is not None:
        prune(prefs, library.series_names(), library.all_book_ids())


def parse_export(text: str) -> SettingsExport:
    """Parse a Settings Export or an old bare Tier Config, turning every failure into a readable TierConfigError."""
    try:
        data: Any = json.loads(text)
    except json.JSONDecodeError as exc:
        raise TierConfigError(_('Not valid JSON: %s') % exc) from exc
    if not isinstance(data, dict):
        raise TierConfigError(_('Settings Export must be a JSON object'))
    entries = cast('dict[str, Any]', data)
    if 'kind' not in entries and 'tier_config' not in entries:
        return SettingsExport(tier_config=parse_config_data(entries))
    _check_marker(entries)
    return SettingsExport(
        tier_config=parse_config_data(entries['tier_config']) if 'tier_config' in entries else None,
        page_defaults=_parse_defaults(entries['page_defaults']) if 'page_defaults' in entries else None,
        overrides=_parse_overrides(entries['overrides']) if 'overrides' in entries else None,
        lane_order=_parse_order(entries['lane_order']) if 'lane_order' in entries else None,
    )


def _check_marker(entries: Mapping[str, Any]) -> None:
    kind = entries.get('kind')
    if kind != KIND:
        raise TierConfigError(_('Not a Tier List Settings Export: unknown kind %r') % kind)
    version = entries.get('version')
    if version != VERSION:
        raise TierConfigError(_('Settings Export version %r is not supported') % version)


def _parse_defaults(data: object) -> PageDefaults:
    if not isinstance(data, Mapping):
        raise TierConfigError(_('page_defaults must be a JSON object'))
    try:
        return PageDefaults.from_dict(cast('Mapping[str, Any]', data))
    except (AttributeError, TypeError, ValueError) as exc:
        raise TierConfigError(_('Invalid page_defaults: %s') % exc) from exc


def _parse_overrides(data: object) -> dict[str, str]:
    if not isinstance(data, Mapping):
        raise TierConfigError(_('overrides must map series names to Tier ids'))
    overrides: dict[str, str] = {}
    for name, tier_id in cast('Mapping[object, object]', data).items():
        if not isinstance(name, str) or not name or not isinstance(tier_id, str) or not tier_id:
            raise TierConfigError(_('overrides must map series names to Tier ids'))
        overrides[name] = tier_id
    return overrides


def _parse_order(data: object) -> dict[str, list[Place]]:
    if not isinstance(data, Mapping):
        raise TierConfigError(_('lane_order must map each Lane to a list of places'))
    order: dict[str, list[Place]] = {}
    for lane, items in cast('Mapping[object, object]', data).items():
        if not isinstance(lane, str) or not lane or not isinstance(items, list):
            raise TierConfigError(_('lane_order must map each Lane to a list of places'))
        places = [place_from_dict(item) for item in cast('list[object]', items)]
        if any(place is None for place in places):
            raise TierConfigError(_('Lane Order places must be {"series": name} or {"book": id}'))
        if places:
            order[lane] = cast('list[Place]', places)
    return order
