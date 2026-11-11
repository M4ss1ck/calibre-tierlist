"""Compile through the facade: the book details the detail panel shows, and the sanitised blurb."""

from datetime import UTC, date, datetime

from fakes import FakeLibrary, FakePrefs

from tierlist.app import TierList
from tierlist.compile import CompileRequest
from tierlist.compile.blurb import BLURB_LIMIT, blurb

NOW = datetime(2026, 11, 6, 12, 0, tzinfo=UTC)
TODAY = date(2026, 11, 6)


def compile_one(**fields: object) -> dict[str, object]:
    library = FakeLibrary(types={'#date_read': 'datetime'})
    library.values['title'] = {1: 'One'}
    library.values['#date_read'] = {1: TODAY}
    for name, value in fields.items():
        library.values[name] = {1: value}
    app = TierList(library, FakePrefs(), lambda: TODAY, lambda: NOW)
    return app.compile(CompileRequest('library', (1,), 'Lib', '0.1.0')).to_dict()['books']['1']


def test_a_blurb_with_html_and_scripts_comes_out_as_trimmed_plain_text() -> None:
    words = ' '.join(f'word{n}' for n in range(200))
    comments = (
        '<script>alert("x")</script><style>p { color: red }</style>'
        f'<p>Fish &amp; chips&nbsp;are <b>great</b>.</p>\n\n<div>  {words}  </div>'
    )

    text = compile_one(comments=comments)['blurb']

    assert isinstance(text, str)
    assert text.startswith('Fish & chips are great. word0 word1')
    assert 'alert' not in text and 'color' not in text and '<' not in text
    assert text.endswith('…')
    assert BLURB_LIMIT - 20 <= len(text) <= BLURB_LIMIT + 1
    assert text[:-1].split(' ')[-1] in words.split(' ')


def test_a_short_blurb_is_kept_whole_and_an_empty_one_is_none() -> None:
    assert blurb('<p>Short &lt;3</p>') == 'Short <3'
    assert blurb('<script>only()</script>  ') is None
    assert blurb(None) is None


def test_book_details_carry_authors_series_rating_and_tags() -> None:
    book = compile_one(
        authors=('Ursula K. Le Guin', 'Someone Else'),
        series='Earthsea',
        series_index=2.5,
        rating=7,
        tags=('fantasy', 'classic'),
    )

    assert book['authors'] == ['Ursula K. Le Guin', 'Someone Else']
    assert book['series'] == 'Earthsea'
    assert book['seriesIndex'] == '2.5'
    assert book['rating'] == 3.5
    assert book['tags'] == ['fantasy', 'classic']


def test_missing_details_are_empty_or_null() -> None:
    book = compile_one(rating=0)

    assert book['authors'] == []
    assert book['series'] is None
    assert book['seriesIndex'] is None
    assert book['rating'] is None
    assert book['tags'] == []
    assert book['blurb'] is None
