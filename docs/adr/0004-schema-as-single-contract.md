# 0004 Schema as the single contract

Status: Accepted
Date: 2026-11-05

## Context

The plugin produces Tier List Data and the HTML page consumes it. The two halves ship from one repo but are written in different languages, and they cannot be allowed to drift apart unnoticed. The payload also needs a version so a page can tell what it was built for.

## Decision

`contract/tierlist.schema.json` is the single source of truth for Tier List Data, and it carries a schema version field. The top-level shape is the schema version, generation metadata (timestamp, library name, scope, plugin version), the ordered Tiers, the Lanes holding Stacks and Cards by reference, a books map, a series map, and a covers map.

TypeScript types are generated from the schema. Python uses hand-written frozen dataclasses checked against the schema by a test. A contract test produces Tier List Data through the facade from a fixture library, validates it against the schema, and writes the same output as the fixture the web tests render.

## Consequences

- A payload change starts in the schema, then reaches both halves; neither side defines the shape alone.
- The contract test fails when the Python dataclasses and the schema disagree, and when facade output stops validating.
- One fixture drives both the Python contract test and the Playwright page tests, so plugin and page always share an example.
- Generated TypeScript types are not edited by hand.
