# calibre-tierlist

A Calibre 9.0+ plugin that assigns books a tier from the right-click menu and compiles a single offline, interactive HTML tier list of your series, exportable to PNG or PDF.

## Usage

Compile a Tier List from the plugin's toolbar menu and open the generated HTML file in your browser. The **Page** tab in Settings sets the Page Defaults a compiled page opens with: theme, title, Unranked Lane label, and whether the Unranked Lane, counts and library name are shown.

You can override any Page Default for one opening with a query in the page's address:

| Key | Values | Overrides |
| --- | --- | --- |
| `theme` | `system`, `light`, `dark` | theme |
| `title` | any text, URL-encoded | title |
| `unranked` | `1`/`0`, `true`/`false` | show the Unranked Lane |
| `unranked_label` | any text, URL-encoded | Unranked Lane label |
| `counts` | `1`/`0`, `true`/`false` | show the book and series counts |
| `library` | `1`/`0`, `true`/`false` | show the library name |

For example, `tierlist.html?theme=dark&counts=0` opens the page dark and without counts. Unknown keys and invalid values are ignored, and a repeated key uses its last value.

Calibre opens the compiled file without a query, so this is for bookmarks and links you open yourself.
