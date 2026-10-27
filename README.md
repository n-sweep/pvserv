# PVServ

A local server for viewing plotly plots

# TODO

## Image support (matplotlib, etc.)

Goal: support images the way foundry-nvim's plot server does (an image plus a mime type), alongside plotly figures.

### Core change

- The `plot` table needs a `mime` column that defaults to the plotly type, so existing rows keep working.
- Existing databases need an `ALTER TABLE`, because `CREATE TABLE IF NOT EXISTS` won't add the column.
- Store image bytes as a BLOB. Decode base64 on ingest, since base64 costs about 33% more space.

### Ingest

- `POST /plotviewer/plot` already takes a raw body. The least disruptive change is to branch on `Content-Type`.
- `application/json` or no type keeps today's behavior. `image/*` is stored as an image.

### Rendering

- Plotly rows embed the whole figure JSON in `data-plot-json` and render client-side. Embedding base64 images the same way would be much heavier, especially in SSE payloads.
- Serve image bytes from a URL like `/plot/<id>/image` and use a plain `<img src>`. The browser caches them.
- `plot.html` and `plot_list_item.html` both need a branch on mime.
- `renderPlot` and `renderThumbnails` in `plot.js` already skip elements with no `data-plot-json`, so they need little or no change.
- The sidebar thumbnail for an image is just the `<img>`. Plotly thumbnails are rendered to PNG client-side.

### events.js

- The `htmx:afterSwap` handler on `#recent-plots` reads `data-plot-json` from the new first sidebar item. It then hand-builds the `#plot-container` HTML around that JSON and calls `renderPlot()`.
- An image item has no `data-plot-json`, so the handler hits `if (!preview) return;`. The image would appear in the sidebar but never in the main pane.
- Fix: add an image branch there, or have it trigger the sidebar item's existing `hx-get` so the server renders the right partial for each type. The second option avoids duplicating markup in JS.
- The click, resize and SSE connection-indicator handlers don't need to change.

### Things that look different for images

- No theme, so no `paper_bgcolor` or font colors to read. The sidebar item and plot area need a neutral default.
- No `layout.title`, so `#title-text` is empty unless a title is sent.
- Transparent matplotlib PNGs will look odd on the dark background.
