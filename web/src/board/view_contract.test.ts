import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { COVER_SIZES, EMPTY_LANE_MODES, GAPS, PAGE_WIDTHS } from './view';

type Enum = { enum?: string[]; $ref?: string };
const schema = JSON.parse(readFileSync(new URL('../../../contract/tierlist.schema.json', import.meta.url), 'utf8')) as {
  $defs: { PageDefaults: { properties: Record<string, Enum> }; Gap: { enum: string[] } };
};

/** The allowed values the contract lists for one Page Defaults key, following a `$ref` to Gap. */
function allowed(key: string): string[] | undefined {
  const property = schema.$defs.PageDefaults.properties[key];
  return property?.$ref === '#/$defs/Gap' ? schema.$defs.Gap.enum : property?.enum;
}

describe('the page offers exactly the choices the contract allows', () => {
  it.each([
    ['pageWidth', PAGE_WIDTHS],
    ['laneGap', GAPS],
    ['coverGap', GAPS],
    ['coverSize', COVER_SIZES],
    ['emptyLane', EMPTY_LANE_MODES],
  ])('%s', (key, values) => {
    expect(values).toEqual(allowed(key));
  });
});
