/* Generated from contract/tierlist.schema.json by pnpm gen:types. Do not edit. */

/**
 * The versioned payload the plugin embeds in the compiled tier list HTML.
 */
export interface TierListData {
  /**
   * Contract version of this payload. Bumped whenever the shape changes.
   */
  schemaVersion: 2;
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
   * Book ids (keys of books), ordered by date read ascending, undated last, then title.
   */
  cards: string[];
}
export interface Book {
  title: string;
  /**
   * Book Tier id, or null when unranked.
   */
  tier: string | null;
  /**
   * Date read as YYYY-MM-DD, or null when Read State has no date (Yes/No column).
   */
  dateRead: string | null;
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
