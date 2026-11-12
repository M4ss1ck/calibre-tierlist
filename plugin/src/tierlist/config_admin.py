"""The use cases behind the config dialog: Tier Config edits, saved-search sync, and orphaned Overrides."""

from collections.abc import Callable, Iterable, Mapping
from datetime import date, datetime

from . import lane_order, page_defaults, series_tiers, settings_export
from .app import TIER_CONFIG_KEY, TierList
from .arrange import THUMB_WIDTH, Arrange
from .compile import Generated, build_data, choose_format
from .page_defaults import PageDefaults
from .ports import NULL_COVERS, Cover, Covers, Library, Prefs, SavedSearches
from .tiers import TierConfig, validate


class ConfigAdmin:
    """Tier Config and the Arrange board for the config dialog, over the Library, Prefs, and SavedSearches ports."""

    def __init__(
        self,
        library: Library,
        prefs: Prefs,
        searches: SavedSearches,
        covers: Covers = NULL_COVERS,
        today: Callable[[], date] = date.today,
    ) -> None:
        self._library = library
        self._prefs = prefs
        self._searches = searches
        self._covers = covers
        self._today = today

    def tier_config(self) -> TierConfig:
        """The Tier Config stored for this library, or the default when absent."""
        return TierList(self._library, self._prefs).tier_config()

    def page_defaults(self) -> PageDefaults:
        """The Page Defaults stored for this library, or the built-in ones."""
        return page_defaults.load_defaults(self._prefs)

    def save_page_defaults(self, defaults: PageDefaults) -> None:
        """Store Page Defaults for this library."""
        page_defaults.save_defaults(self._prefs, defaults)

    def arrange(self) -> Arrange:
        """The whole-library board the Arrange View shows, built without reading cover images."""
        generated = Generated(datetime.now().astimezone(), '', 'library', '')
        ids = tuple(sorted(self._library.all_book_ids()))
        overrides = series_tiers.load_overrides(self._prefs)
        order = lane_order.load_order(self._prefs)
        data = build_data(generated, self._library, self.tier_config(), ids, overrides, order)
        return Arrange.from_data(data, overrides)

    def save_arrange(self, staged: Arrange) -> None:
        """Write staged Book Tiers, Overrides, and Lane Order, then prune Lane Order."""
        app = TierList(self._library, self._prefs, self._today, covers=self._covers)
        for book_id, tier_id in staged.book_tiers().items():
            if tier_id is None:
                app.clear_book_tier([book_id])
            else:
                app.set_book_tier([book_id], tier_id)
        series_tiers.save_overrides(self._prefs, staged.overrides())
        lane_order.save_order(self._prefs, staged.order())
        lane_order.prune(self._prefs, self._library.series_names(), self._library.all_book_ids())

    def thumbnail(self, book_id: int) -> Cover | None:
        """A small cover thumbnail for the Arrange View, or None when the book has no cover."""
        return self._covers.cover(book_id, choose_format(self._covers.formats()), THUMB_WIDTH)

    def book_count(self, tier_id: str) -> int:
        """How many books hold this Tier id, zero when the tier column is missing."""
        values = self._column_values(self.tier_config().tier_column)
        return sum(1 for value in values.values() if value == tier_id)

    def column_types(self) -> Mapping[str, str]:
        """Every custom column lookup name mapped to its datatype."""
        return self._library.column_types()

    def series_names(self) -> list[str]:
        """Every series name in the library, sorted."""
        return sorted(self._library.series_names())

    def save(self, new: TierConfig) -> None:
        """Validate and store Tier Config, clear removed Tiers' books, and sync their saved searches."""
        validate(new)
        old = self.tier_config()
        self._clear_removed(old, new)
        self._prefs.set(TIER_CONFIG_KEY, new.to_dict())
        self._sync_searches(old, new)
        lane_order.prune(self._prefs, self._library.series_names(), self._library.all_book_ids())

    def export_settings(self, config: TierConfig, defaults: PageDefaults, include: bool) -> str:
        """The Settings Export JSON for these settings, with Overrides and Lane Order when asked."""
        return settings_export.export_settings(self._prefs, config, defaults, include)

    def parse_settings_export(self, text: str) -> settings_export.SettingsExport:
        """Parse an imported Settings Export without storing it."""
        return settings_export.parse_export(text)

    def apply_import(self, export: settings_export.SettingsExport) -> None:
        """Replace the stored Overrides and Lane Order the export carries, then prune stale places."""
        settings_export.apply_import(self._prefs, self._library, export)

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
        names = list(names)
        if names:
            series_tiers.clear_overrides(self._prefs, names)

    def _column_values(self, lookup_name: str) -> dict[int, object | None]:
        if not self._library.has_column(lookup_name):
            return {}
        return self._library.read_field(lookup_name, self._library.all_book_ids())

    def _clear_removed(self, old: TierConfig, new: TierConfig) -> None:
        removed = {tier.id for tier in old.tiers} - {tier.id for tier in new.tiers}
        if not removed:
            return
        values = self._column_values(old.tier_column)
        clearing = {book_id: None for book_id, value in values.items() if value in removed}
        if clearing:
            self._library.write_field(old.tier_column, clearing)

    def _sync_searches(self, old: TierConfig, new: TierConfig) -> None:
        target = {f'Tier {tier.label}': f'{new.tier_column}:"={tier.id}"' for tier in new.tiers}
        labels = {f'Tier {tier.label}' for tier in (*old.tiers, *new.tiers)}
        existing = self._searches.names()
        for name in existing:
            if name in labels and name not in target:
                self._searches.remove(name)
        for name, query in target.items():
            if self._searches.query(name) == query:
                continue
            if name in existing:
                self._searches.remove(name)
            self._searches.add(name, query)
