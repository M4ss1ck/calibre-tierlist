"""Tier Config validation, JSON parsing, and JSON dumping."""

import json

import pytest

from tierlist.tiers import (
    DEFAULT_TIER_CONFIG,
    Tier,
    TierConfig,
    TierConfigError,
    dump_config,
    parse_config,
    validate,
)

VALID = TierConfig(tiers=(Tier('s', 'S', '#ff7f7f'), Tier('a', 'A', '#FFBF7F')))


def test_a_valid_config_passes() -> None:
    validate(VALID)
    validate(DEFAULT_TIER_CONFIG)


def test_no_tiers_is_rejected() -> None:
    with pytest.raises(TierConfigError, match='at least one'):
        validate(TierConfig(tiers=()))


def test_duplicate_ids_are_rejected() -> None:
    config = TierConfig(tiers=(Tier('s', 'S', '#ff7f7f'), Tier('s', 'S2', '#ffbf7f')))
    with pytest.raises(TierConfigError, match='Duplicate'):
        validate(config)


@pytest.mark.parametrize('label', ['S', ' s ', 'S '])
def test_duplicate_labels_are_rejected_ignoring_case_and_space(label: str) -> None:
    config = TierConfig(tiers=(Tier('s', 'S', '#ff7f7f'), Tier('a', label, '#ffbf7f')))
    with pytest.raises(TierConfigError, match='Duplicate'):
        validate(config)


@pytest.mark.parametrize('tier_id', ['', '   '])
def test_an_empty_tier_id_is_rejected(tier_id: str) -> None:
    with pytest.raises(TierConfigError, match='id'):
        validate(TierConfig(tiers=(Tier(tier_id, 'S', '#ff7f7f'),)))


@pytest.mark.parametrize('label', ['', ' \t'])
def test_an_empty_label_is_rejected(label: str) -> None:
    with pytest.raises(TierConfigError, match='label'):
        validate(TierConfig(tiers=(Tier('s', label, '#ff7f7f'),)))


@pytest.mark.parametrize('colour', ['ff7f7f', '#fff', '#gggggg', '#ff7f7'])
def test_a_colour_that_is_not_hex_is_rejected(colour: str) -> None:
    with pytest.raises(TierConfigError, match='colour'):
        validate(TierConfig(tiers=(Tier('s', 'S', colour),)))


def test_an_imported_config_with_an_older_stack_depth_still_parses() -> None:
    older = {**VALID.to_dict(), 'stack_depth': 99}
    assert parse_config(json.dumps(older)) == VALID


def test_parse_accepts_a_dumped_config() -> None:
    assert parse_config(dump_config(VALID)) == VALID


def test_parse_rejects_invalid_json() -> None:
    with pytest.raises(TierConfigError, match='Not valid JSON'):
        parse_config('{not json')


def test_parse_reports_a_missing_tiers_field() -> None:
    with pytest.raises(TierConfigError, match='Missing field: tiers'):
        parse_config('{}')


@pytest.mark.parametrize('text', ['[]', '{"tiers": 5}'])
def test_parse_rejects_a_non_config_shape(text: str) -> None:
    with pytest.raises(TierConfigError):
        parse_config(text)


def test_parse_validates_the_parsed_config() -> None:
    with pytest.raises(TierConfigError, match='at least one'):
        parse_config('{"tiers": []}')


def test_dump_is_indented_json() -> None:
    text = dump_config(VALID)
    assert text.startswith('{')
    assert '\n  "tiers"' in text
