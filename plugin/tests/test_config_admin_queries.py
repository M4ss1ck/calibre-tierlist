"""The config-dialog facade's read-only library queries: column types and series names."""

from fakes import FakeLibrary, FakePrefs, FakeSavedSearches

from tierlist.config_admin import ConfigAdmin


def make(columns: tuple[str, ...], types: dict[str, str] | None = None) -> tuple[ConfigAdmin, FakeLibrary]:
    library = FakeLibrary(columns, types)
    return ConfigAdmin(library, FakePrefs(), FakeSavedSearches()), library


def test_column_types_reports_every_custom_column() -> None:
    admin, _ = make(('#tier', '#read'), {'#read': 'datetime'})
    assert admin.column_types() == {'#tier': 'text', '#read': 'datetime'}


def test_series_names_are_sorted_and_skip_empty_names() -> None:
    admin, library = make(())
    library.values['series'] = {1: 'Dune', 2: '', 3: 'Earthsea'}
    assert admin.series_names() == ['Dune', 'Earthsea']
