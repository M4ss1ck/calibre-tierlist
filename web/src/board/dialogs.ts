import type { Selection } from './Detail.svelte';
import type { StackPick } from './stack';

/** Where Detail's back button returns: a series' panel, focused on the row that opened Detail. */
export type ReturnTo = { series: string; row: number };

/**
 * Which of the page's two dialogs is open and how they lead into each other:
 * `opened` is the series whose Series Panel is open, `selection` what Detail
 * shows, `returnTo` where Detail's back button leads when a panel row opened
 * it, and `focusRow` the row whose title takes focus when the panel reopens.
 */
export type Nav = {
  opened?: string | undefined;
  selection?: Selection | undefined;
  returnTo?: ReturnTo | undefined;
  focusRow?: number | undefined;
};

/** A Stack opens its panel; a Card opens Detail with no way back. */
export function openPicked(nav: Nav, picked: Selection | StackPick): Nav {
  if ('stack' in picked) return { ...nav, opened: picked.stack, focusRow: undefined };
  return { ...nav, selection: picked, returnTo: undefined };
}

/**
 * A Series Panel row's title opens Detail in place of the panel, remembering
 * the way back. The panel is marked closed here, not when its close event
 * lands later, so nothing reopens it in between.
 */
export function pick(nav: Nav, selection: Selection, from: ReturnTo): Nav {
  return { ...nav, opened: undefined, selection, returnTo: from };
}

/** Detail's back button: close Detail and reopen the panel it came from, on the row that opened it. */
export function back(nav: Nav): Nav {
  if (!nav.returnTo) return nav;
  return { opened: nav.returnTo.series, focusRow: nav.returnTo.row, selection: undefined, returnTo: undefined };
}

/** Detail closed, by back, ×, or Escape: the way back is forgotten. */
export function closeDetail(nav: Nav): Nav {
  return { ...nav, selection: undefined, returnTo: undefined };
}

/** The Series Panel closed. */
export function closePanel(nav: Nav): Nav {
  return { ...nav, opened: undefined };
}
