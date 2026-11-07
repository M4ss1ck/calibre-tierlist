"""The application facade: every use case the calibre UI calls, over the ports."""

import time
from collections.abc import Callable, Iterable
from datetime import date, datetime
from pathlib import Path

from . import read_state, series_tiers
from .compile import CompileRequest, TierListData, choose_format, compile_data, count_series
from .compile.data import Generated
from .ports import NULL_COVERS, Covers, Library, Prefs
from .publish import write_html
from .tiers import DEFAULT_TIER_CONFIG, TierConfig

TIER_CONFIG_KEY = 'tier_config'
TIER_COLUMN_OFFERED_KEY = 'tier_column_offered'
READ_COLUMN_OFFERED_KEY = 'read_column_offered'


class TierList:
    """The use cases for one library, constructed with its Library and Prefs ports."""

    def __init__(
        self,
        library: Library,
        prefs: Prefs,
        today: Callable[[], date] = date.today,
        now: Callable[[], datetime] = lambda: datetime.now().astimezone(),
        covers: Covers = NULL_COVERS,
    ) -> None:
        self._library = library
        self._prefs = prefs
        self._today, self._now = today, now
        self._covers = covers

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

    def read_column_ready(self) -> bool:
        """True when the column Tier Config names for Read State is a Date or Yes/No column."""
        return read_state.column_ready(self._library, self.tier_config())

    def read_column_candidates(self) -> list[str]:
        """The lookup names of every Date and Yes/No column in this library, sorted."""
        return read_state.column_candidates(self._library)

    def map_read_column(self, lookup_name: str) -> None:
        """Store the Date or Yes/No column that holds Read State."""
        config = read_state.mapped(self._library, self.tier_config(), lookup_name)
        self._prefs.set(TIER_CONFIG_KEY, config.to_dict())

    def read_column_offered(self) -> bool:
        """True once the first-run offer to map the read column was shown."""
        return self._prefs.get(READ_COLUMN_OFFERED_KEY) is True

    def mark_read_column_offered(self) -> None:
        """Record that the first-run offer was shown, so it never appears again."""
        self._prefs.set(READ_COLUMN_OFFERED_KEY, True)

    def mark_read(self, book_ids: Iterable[int]) -> None:
        """Mark every book id read, filling the Read State column only where it is still empty."""
        read_state.mark_read(self._library, self.tier_config(), book_ids, self._today())

    def mark_unread(self, book_ids: Iterable[int]) -> None:
        """Clear Book Tier and Read State for every book id, one write per ready column."""
        read_state.mark_unread(self._library, self.tier_config(), book_ids)

    def set_book_tier(self, book_ids: Iterable[int], tier_id: str) -> None:
        """Set the Book Tier of every book id to this Tier id, in one write, and mark them read."""
        config = self.tier_config()
        if config.tier(tier_id) is None:
            raise ValueError(f'unknown Tier id: {tier_id!r}')
        ids = list(book_ids)
        self._write_tier(config, ids, tier_id)
        self.mark_read(ids)

    def clear_book_tier(self, book_ids: Iterable[int]) -> None:
        """Clear the Book Tier of every book id, in one write, keeping Read State."""
        self._write_tier(self.tier_config(), book_ids, None)

    def set_series_tier(self, book_ids: Iterable[int], tier_id: str) -> None:
        """Give every distinct series these book ids belong to this Series Tier as an Override."""
        if self.tier_config().tier(tier_id) is None:
            raise ValueError(f'unknown Tier id: {tier_id!r}')
        series_tiers.set_series_tier(self._library, self._prefs, book_ids, tier_id)

    def clear_series_tier(self, book_ids: Iterable[int]) -> None:
        """Return every series these book ids belong to to Auto, by dropping its Override."""
        series_tiers.clear_series_tier(self._library, self._prefs, book_ids)

    def series_tier_overrides(self) -> dict[str, str]:
        """Every Override in this library, by series name."""
        return series_tiers.load_overrides(self._prefs)

    def series_tier_orphans(self) -> list[str]:
        """The Override series names that match no series in the library, sorted."""
        return series_tiers.orphans(self.series_tier_overrides(), self._library.series_names())

    def _write_tier(self, config: TierConfig, book_ids: Iterable[int], tier_id: str | None) -> None:
        values: dict[int, str | None] = {book_id: tier_id for book_id in book_ids}
        if values:
            self._library.write_field(config.tier_column, values)

    def compile(self, request: CompileRequest) -> TierListData:
        """Compile Tier List Data for one Compile Request."""
        generated = Generated(self._now(), request.library_name, request.scope, request.plugin_version)
        fmt = choose_format(self._covers.formats())
        overrides = self.series_tier_overrides()
        return compile_data(
            generated, self._library, self._covers, fmt, self.tier_config(), request.book_ids, overrides
        )

    def output_path(self) -> str:
        """The remembered output path, or today's default."""
        stored = self._prefs.get('output_path')
        return str(stored or Path.home() / 'Tierlists' / f'tierlist-{self._today().isoformat()}.html')

    def remember_output_path(self, path: str) -> None:
        """Remember where the next compiled tier list should be written."""
        self._prefs.set('output_path', path)

    def compile_to_file(self, request: CompileRequest, template: str, path: Path, log: Callable[[str], None]) -> None:
        """Compile, render, and write the HTML file, then log one summary line."""
        started = time.perf_counter()
        data = self.compile(request)
        fmt = choose_format(self._covers.formats())
        size = write_html(template, data, path)
        seconds = time.perf_counter() - started
        series = count_series(self._library, [book.id for book in data.books])
        log(
            f'Tier List compiled: {len(data.books)} of {len(request.book_ids)} books, {series} series, '
            f'{len(data.covers)} covers as {fmt} in {seconds:.2f}s, {size} bytes -> {path}'
        )
