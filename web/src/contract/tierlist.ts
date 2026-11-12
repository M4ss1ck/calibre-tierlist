/* Generated from contract/tierlist.schema.json by pnpm gen:types. Do not edit. */

export type LaneItem =
  | {
      /**
       * Series name (key of series) of a Stack in this Lane.
       */
      stack: string;
    }
  | {
      /**
       * Book id (key of books) of a standalone Card in this Lane.
       */
      card: string;
    };

/**
 * The versioned payload the plugin embeds in the compiled tier list HTML.
 */
export interface TierListData {
  /**
   * Contract version of this payload. Bumped whenever the shape changes.
   */
  schemaVersion: 7;
  generated: Generated;
  /**
   * Every Tier in Tier Config order.
   */
  tiers: Tier[];
  /**
   * One Lane per Tier in config order, then the Unranked Lane last.
   */
  lanes: Lane[];
  /**
   * Every book on the board, keyed by calibre book id as a string.
   */
  books: {
    [k: string]: Book;
  };
  /**
   * Each series on the board, keyed by series name.
   */
  series: {
    [k: string]: Series;
  };
  /**
   * Each cover embedded once, keyed by book id as a string. A book with no entry has no cover and is drawn in the Placeholder style with a "no cover" mark.
   */
  covers: {
    [k: string]: Cover;
  };
}
export interface Generated {
  /**
   * When the compile ran, ISO 8601 with offset.
   */
  at: string;
  libraryName: string;
  scope: "library" | "virtual_library" | "selection";
  pluginVersion: string;
}
export interface Tier {
  id: string;
  label: string;
  colour: string;
  description: string;
}
export interface Lane {
  /**
   * The Tier id of this Lane, or null for the Unranked Lane.
   */
  tier: string | null;
  /**
   * The Stacks and Cards in this Lane, in Lane Order: stored places first, then unplaced items by date read ascending, undated last, then name or title, then id.
   */
  items: LaneItem[];
}
export interface Book {
  title: string;
  /**
   * Author names in calibre's order.
   */
  authors: string[];
  /**
   * Series name (key of series), or null for a standalone book.
   */
  series: string | null;
  /**
   * The series index as a reader sees it, e.g. "2.5", or null for a standalone book.
   */
  seriesIndex: string | null;
  /**
   * Stars out of 5 in half steps, or null when unrated.
   */
  rating: number | null;
  /**
   * calibre tags.
   */
  tags: string[];
  /**
   * The book's comments as plain text, trimmed at a word boundary near 600 characters with an ellipsis; null when empty.
   */
  blurb: string | null;
  /**
   * Book Tier id, or null when unranked.
   */
  tier: string | null;
  /**
   * Date read as YYYY-MM-DD, or null when Read State has no date (Yes/No column).
   */
  dateRead: string | null;
  /**
   * Whether the book is read, from Read State.
   */
  read: boolean;
}
export interface Series {
  /**
   * Dominant colour of the first owned book with a cover, used to draw this series' Placeholders.
   */
  colour: string;
  /**
   * Every position of the series, index 1 first; a position with no owned book is a Placeholder.
   */
  positions: Position[];
  /**
   * True when this series' Series Tier is an Override, false when it is Auto.
   */
  override: boolean;
}
export interface Position {
  /**
   * The series index as a reader sees it, e.g. "1" or "2.5".
   */
  number: string;
  /**
   * Book id (key of books) at this position, or null for a Placeholder.
   */
  book: string | null;
}
export interface Cover {
  /**
   * data: URI of the 240 px wide thumbnail (AVIF, WebP, or JPEG)
   */
  src: string;
  /**
   * Dominant cover colour
   */
  colour: string;
}
