import { describe, expect, it } from 'vitest';
import { cleanText } from './editable';

describe('cleanText', () => {
  it('keeps plain text as it is', () => {
    expect(cleanText('Must read')).toBe('Must read');
  });

  it('trims both ends', () => {
    expect(cleanText('  S  ')).toBe('S');
  });

  it('collapses runs of spaces, tabs and pasted newlines to one space', () => {
    expect(cleanText('My\n\nfavourite\t  books\r\n')).toBe('My favourite books');
  });

  it('collapses non-breaking spaces a contenteditable inserts', () => {
    expect(cleanText('Read  next')).toBe('Read next');
  });

  it('reduces whitespace-only text to empty, which the editor reverts', () => {
    expect(cleanText(' \n\t ')).toBe('');
    expect(cleanText('')).toBe('');
  });

  it('keeps non-ASCII letters and punctuation', () => {
    expect(cleanText(' Cien años · 100% ')).toBe('Cien años · 100%');
  });
});
