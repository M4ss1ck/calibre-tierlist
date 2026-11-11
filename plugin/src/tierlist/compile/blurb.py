"""The blurb: calibre's HTML comments as plain text, trimmed at a word boundary."""

from html.parser import HTMLParser

BLURB_LIMIT = 600
ELLIPSIS = '…'
_HIDDEN = frozenset({'script', 'style'})
_BLOCKS = frozenset(
    {'address', 'article', 'blockquote', 'br', 'dd', 'div', 'dt', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'li'}
    | {'ol', 'p', 'pre', 'section', 'table', 'td', 'th', 'tr', 'ul'}
)


class _Text(HTMLParser):
    """Collects text outside <script> and <style>, with entities already unescaped."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _HIDDEN:
            self._hidden += 1
        elif tag in _BLOCKS:
            self.parts.append(' ')

    def handle_endtag(self, tag: str) -> None:
        if tag in _HIDDEN:
            self._hidden = max(0, self._hidden - 1)
        elif tag in _BLOCKS:
            self.parts.append(' ')

    def handle_data(self, data: str) -> None:
        if not self._hidden:
            self.parts.append(data)


def blurb(comments: object, limit: int = BLURB_LIMIT) -> str | None:
    """Plain text of these HTML comments, whitespace collapsed and trimmed near `limit`; None when empty."""
    if not isinstance(comments, str):
        return None
    parser = _Text()
    parser.feed(comments)
    parser.close()
    text = ' '.join(''.join(parser.parts).split())
    if not text:
        return None
    if len(text) <= limit:
        return text
    cut = text.rfind(' ', 0, limit + 1)
    return text[: cut if cut > 0 else limit].rstrip() + ELLIPSIS
