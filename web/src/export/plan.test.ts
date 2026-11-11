import { describe, expect, it } from 'vitest';
import type { ExportPlan, Size } from './plan';
import { fits, fitScale, planExport, SAFE_LIMITS } from './plan';

function parts(plan: ExportPlan) {
  if (plan.kind !== 'split') throw new Error(`expected a split, got ${plan.kind}`);
  return plan.parts;
}

function part(plan: ExportPlan, id: string) {
  const found = parts(plan).find((candidate) => candidate.id === id);
  if (!found) throw new Error(`no part ${id}`);
  return found;
}

describe('fits', () => {
  it('checks both scaled sides and the scaled area', () => {
    expect(fits({ width: 1000, height: 1000 }, 2, SAFE_LIMITS)).toBe(true);
    expect(fits({ width: 5000, height: 5000 }, 1, SAFE_LIMITS)).toBe(false);
    expect(fits({ width: 9000, height: 1000 }, 2, SAFE_LIMITS)).toBe(false);
  });
});

describe('fitScale', () => {
  it('takes the tightest of the side and area caps', () => {
    expect(fitScale({ width: 8192, height: 8192 }, SAFE_LIMITS)).toBe(0.5);
    expect(fitScale({ width: 100, height: 100 }, SAFE_LIMITS)).toBe(40.96);
    expect(fitScale({ width: 20000, height: 10 }, SAFE_LIMITS)).toBe(SAFE_LIMITS.maxSide / 20000);
  });
});

describe('planExport', () => {
  it('is a single canvas when the board fits', () => {
    const board: Size = { width: 1000, height: 800 };
    expect(planExport(board, [{ id: 's', size: { width: 1000, height: 200 } }], 1)).toEqual({
      kind: 'single',
      scale: 1,
    });
  });

  it('splits a board that is too tall into one part per lane, all at full scale', () => {
    const lane: Size = { width: 800, height: 6000 };
    const lanes = [
      { id: 's', size: lane },
      { id: 'a', size: lane },
      { id: 'unranked', size: lane },
    ];
    const plan = planExport({ width: 800, height: 18000 }, lanes, 1);
    expect(parts(plan).map((p) => p.id)).toEqual(['s', 'a', 'unranked']);
    expect(parts(plan).map((p) => p.scale)).toEqual([1, 1, 1]);
    expect(parts(plan).map((p) => p.downscaled)).toEqual([false, false, false]);
  });

  it('downscales only the lane that is too big, leaving the rest untouched', () => {
    const lanes = [
      { id: 's', size: { width: 1000, height: 400 } },
      { id: 'a', size: { width: 8192, height: 8192 } },
      { id: 'b', size: { width: 1000, height: 8000 } },
    ];
    const plan = planExport({ width: 8192, height: 16592 }, lanes, 1);
    expect(parts(plan).map((p) => p.downscaled)).toEqual([false, true, false]);
    expect(part(plan, 's')).toEqual({ id: 's', scale: 1, downscaled: false });
    expect(part(plan, 'b')).toEqual({ id: 'b', scale: 1, downscaled: false });

    const big = part(plan, 'a');
    expect(big.scale).toBe(0.5);
    const scaledWidth = 8192 * big.scale;
    const scaledHeight = 8192 * big.scale;
    expect(scaledWidth).toBeLessThanOrEqual(SAFE_LIMITS.maxSide);
    expect(scaledHeight).toBeLessThanOrEqual(SAFE_LIMITS.maxSide);
    expect(scaledWidth * scaledHeight).toBeLessThanOrEqual(SAFE_LIMITS.maxArea);
  });

  it('counts the scale against the limits', () => {
    const lane: Size = { width: 8192, height: 1024 };
    const lanes = [{ id: 's', size: lane }, { id: 'unranked', size: lane }];
    const board: Size = { width: 8192, height: 2048 };

    expect(planExport(board, lanes, 1)).toEqual({ kind: 'single', scale: 1 });

    const doubled = planExport(board, lanes, 2);
    expect(doubled.kind).toBe('split');
    expect(parts(doubled).map((p) => p.downscaled)).toEqual([true, true]);
    expect(part(doubled, 's').scale).toBeCloseTo(Math.SQRT2, 10);
  });

  it('never throws on an empty board', () => {
    expect(planExport({ width: 0, height: 0 }, [], 1)).toEqual({ kind: 'single', scale: 1 });
  });
});
