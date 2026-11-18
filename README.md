# calibre-tierlist

A Calibre 9.0+ plugin that assigns books a tier from the right-click menu and compiles a single offline, interactive HTML tier list of your series, exportable to PNG or PDF.

## Usage

Compile a Tier List from the plugin's toolbar menu and open the generated HTML file in your browser. The **Page** tab in Settings sets the Page Defaults a compiled page opens with: theme, title, Page Width, the header's counts and library name, the Lanes' labels, Tier descriptions, Lane Gap, Unranked Lane and Empty Lane Message, and the covers' Captions, Read Count, Cover Size and Cover Gap.

The **Customize view** button on the page opens the View Panel, which changes those Page Defaults for that opening only — Lanes, Covers and Page, grouped as in Settings, with nothing saved. Its switch shows or hides the Unranked Lane. The theme picker beside it is not saved either.

You can override any Page Default for one opening with a query in the page's address:

| Key | Values | Overrides |
| --- | --- | --- |
| `theme` | `system`, `light`, `dark` | theme |
| `title` | any text, URL-encoded | title |
| `unranked` | `1`/`0`, `true`/`false` | show the Unranked Lane |
| `unranked_label` | any text, URL-encoded | Unranked Lane label |
| `counts` | `1`/`0`, `true`/`false` | show the book and series counts |
| `library` | `1`/`0`, `true`/`false` | show the library name |
| `width` | `narrow`, `normal`, `wide`, `full` | Page Width |
| `labels` | `1`/`0`, `true`/`false` | show each Lane's label |
| `descriptions` | `1`/`0`, `true`/`false` | show each Tier's description |
| `lane_gap` | `none`, `small`, `normal`, `large` | Lane Gap |
| `empty` | `default`, `hidden`, `custom` | Empty Lane Message |
| `empty_text` | any text, URL-encoded | the `custom` Empty Lane Message |
| `captions` | `1`/`0`, `true`/`false` | show Stacks' and Cards' Captions |
| `read_count` | `1`/`0`, `true`/`false` | show each Stack's Read Count |
| `cover_size` | `small`, `normal`, `large` | Cover Size |
| `cover_gap` | `none`, `small`, `normal`, `large` | Cover Gap |

For example, `tierlist.html?theme=dark&counts=0` opens the page dark and without counts. Unknown keys and invalid values are ignored, and a repeated key uses its last value.

Calibre opens the compiled file without a query, so this is for bookmarks and links you open yourself.

### Cover grid emblems

With this on, every tiered book's Tier label, in its Tier's colour, is drawn on its cover in calibre's cover grid and Bookshelf view. Turn it on in Settings > Tiers with "Show tiers as cover grid emblems". It is off by default and kept per library.

When calibre is set to hide cover emblems, ticking the box asks once whether to show them. If you answered no, or calibre still hides them, turn them on under Preferences > Look & feel > Cover grid.

The icons are PNG files named `tierlist_*.png` in calibre's `cc_icons/` folder inside its config directory. They are never deleted automatically, as another library may still use them; delete them by hand to clean up. Calibre has no uninstall hook, so turn the feature off before uninstalling the plugin, or remove the "Advanced rule" under Look & feel > Cover grid emblems, to take the rule back out of calibre.

To see the Tier as text under covers instead, set calibre's field under covers to the Tier column, for example `#tier`.
