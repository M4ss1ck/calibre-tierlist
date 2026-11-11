/** What an editable text holds and where a committed edit goes. */
export type EditableParams = { value: string; onchange: (value: string) => void };

/** Collapses runs of whitespace (a pasted newline included) and trims the ends. */
export function cleanText(text: string): string {
  return text.replace(/\s+/g, ' ').trim();
}

/**
 * Makes an element's text editable in place: Enter or leaving it commits the
 * cleaned text, Escape reverts it, and an empty edit falls back to the value
 * it had. The element shows plain text, so print and PNG export see the text.
 */
export function editable(node: HTMLElement, params: EditableParams) {
  let current = params;
  node.textContent = current.value;
  node.contentEditable = 'plaintext-only';
  if (node.contentEditable !== 'plaintext-only') node.contentEditable = 'true';
  node.spellcheck = false;

  function commit() {
    const text = cleanText(node.textContent ?? '');
    if (text === '') node.textContent = current.value;
    else if (text !== current.value) current.onchange(text);
    else node.textContent = text;
  }

  function onkeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      event.preventDefault();
      node.blur();
    } else if (event.key === 'Escape') {
      event.preventDefault();
      node.textContent = current.value;
      node.blur();
    }
  }

  node.addEventListener('blur', commit);
  node.addEventListener('keydown', onkeydown);

  return {
    update(next: EditableParams) {
      current = next;
      if (document.activeElement !== node) node.textContent = next.value;
    },
    destroy() {
      node.removeEventListener('blur', commit);
      node.removeEventListener('keydown', onkeydown);
    },
  };
}
