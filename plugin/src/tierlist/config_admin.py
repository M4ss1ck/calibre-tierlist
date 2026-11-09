"""The use cases behind the config dialog: Tier Config edits, saved-search sync, and orphaned Overrides."""

from collections.abc import Iterable

from . import series_tiers
from .app import TIER_CONFIG_KEY, TierList
from .ports import Library, Prefs, SavedSearches
from .tiers import Tier, TierConfig, dump_config, parse_config, validate


class ConfigAdmin:
    """Tier Config for the config dialog, over the Library, Prefs, and SavedSearches ports."""

    def __init__(self, library: Library, prefs: Prefs, searches: SavedSearches) -> None:
        self._library = library
        self._prefs = prefs
        self._searches = searches

    def tier_config(self) -> TierConfig:
        """The Tier Config stored for this library, or the default when absent."""
        return TierList(self._library, self._prefs).tier_config()

    def book_count(self, tier_id: str) -> int:
        """How many books hold this Tier id, zero when the tier column is missing."""
        config = self.tier_config()
        if not self._library.has_column(config.tier_column):
            return 0
        values = self._library.read_field(config.tier_column, self._library.all_book_ids())
        return sum(1 for value in values.values() if value == tier_id)

    def save(self, new: TierConfig) -> None:
        """Validate and store Tier Config, clear removed Tiers' books, and sync their saved searches."""
        validate(new)
        old = self.tier_config()
        self._clear_removed(old, new)
        self._prefs.set(TIER_CONFIG_KEY, new.to_dict())
        self._sync_searches(old, new)

    def import_json(self, text: str) -> TierConfig:
        """Parse an imported Tier Config without storing it."""
        return parse_config(text)

    def export_json(self) -> str:
        """The stored Tier Config as indented JSON."""
        return dump_config(self.tier_config())

    def orphans(self) -> list[str]:
        """The Override series names that match no series in the library, sorted."""
        return series_tiers.orphans(series_tiers.load_overrides(self._prefs), self._library.series_names())

    def reattach_orphan(self, old_name: str, new_series: str) -> None:
        """Move an orphaned Override to a series that exists, dropping the old name."""
        overrides = series_tiers.load_overrides(self._prefs)
        tier_id = overrides.get(old_name)
        if tier_id is None or not new_series:
            return
        series_tiers.clear_overrides(self._prefs, [old_name])
        series_tiers.set_overrides(self._prefs, [new_series], tier_id)

    def delete_orphans(self, names: Iterable[str]) -> None:
        """Drop these orphaned Overrides."""
        ids = list(names)
        if ids:
            series_tiers.clear_overrides(self._prefs, ids)

    def _clear_removed(self, old: TierConfig, new: TierConfig) -> None:
        removed = {tier.id for tier in old.tiers} - {tier.id for tier in new.tiers}
        if not removed or not self._library.has_column(old.tier_column):
            return
        values = self._library.read_field(old.tier_column, self._library.all_book_ids())
        clearing = {book_id: None for book_id, value in values.items() if value in removed}
        if clearing:
            self._library.write_field(old.tier_column, clearing)

    def _sync_searches(self, old: TierConfig, new: TierConfig) -> None:
        old_by_id = {tier.id: tier for tier in old.tiers}
        new_by_id = {tier.id: tier for tier in new.tiers}
        for tier_id in old_by_id.keys() - new_by_id.keys():
            self._searches.remove(f'Tier {old_by_id[tier_id].label}')
        names = self._searches.names()
        for tier_id, tier in new_by_id.items():
            name = f'Tier {tier.label}'
            query = f'{new.tier_column}:"={tier_id}"'
            old_name = _search_name(old_by_id.get(tier_id))
            if old_name is not None and old_name != name and old_name in names:
                self._searches.rename(old_name, name)
                names = self._searches.names()
            if name in names and self._searches.query(name) == query:
                continue
            if name in names:
                self._searches.remove(name)
            self._searches.add(name, query)


def _search_name(tier: Tier | None) -> str | None:
    return None if tier is None else f'Tier {tier.label}'
