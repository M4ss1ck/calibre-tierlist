"""The application facade: every use case the calibre UI calls, over the ports."""

from collections.abc import Iterable

from .ports import Library, Prefs
from .tiers import DEFAULT_TIER_CONFIG, TierConfig

TIER_CONFIG_KEY = 'tier_config'
TIER_COLUMN_OFFERED_KEY = 'tier_column_offered'


class TierList:
    """The use cases for one library, constructed with its Library and Prefs ports."""

    def __init__(self, library: Library, prefs: Prefs) -> None:
        self._library = library
        self._prefs = prefs

    def tier_config(self) -> TierConfig:
        """The Tier Config stored for this library, or the default when absent."""
        stored = self._prefs.get(TIER_CONFIG_KEY)
        if stored is None:
            return DEFAULT_TIER_CONFIG
        return TierConfig.from_dict(stored)

    def tier_column_ready(self) -> bool:
        """True when the Text column Tier Config names exists in this library."""
        return self._library.has_column(self.tier_config().tier_column)

    def tier_column_offered(self) -> bool:
        """True once the first-run offer to create the tier column was shown."""
        return self._prefs.get(TIER_COLUMN_OFFERED_KEY) is True

    def mark_tier_column_offered(self) -> None:
        """Record that the first-run offer was shown, so it never appears again."""
        self._prefs.set(TIER_COLUMN_OFFERED_KEY, True)

    def set_book_tier(self, book_ids: Iterable[int], tier_id: str) -> None:
        """Set the Book Tier of every book id to this Tier id, in one write."""
        config = self.tier_config()
        if config.tier(tier_id) is None:
            raise ValueError(f'unknown Tier id: {tier_id!r}')
        self._write_tier(config, book_ids, tier_id)

    def clear_book_tier(self, book_ids: Iterable[int]) -> None:
        """Clear the Book Tier of every book id, in one write."""
        self._write_tier(self.tier_config(), book_ids, None)

    def _write_tier(self, config: TierConfig, book_ids: Iterable[int], tier_id: str | None) -> None:
        values: dict[int, str | None] = {book_id: tier_id for book_id in book_ids}
        if values:
            self._library.write_text(config.tier_column, values)
