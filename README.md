# thewirebranch.com

Static site for *The Wire Branch* by S.J. Barrett. The full book is published
here, free to read — each document styled as the venue and genre it inhabits.

Hosted on GitHub Pages. Push to `main` to deploy.

## The book pipeline

The manuscript repo (`../the_wire_branch/`) is the single source of truth for
the text. Nothing under `read/` is hand-edited.

**To publish a text edit:** edit the markdown in the book repo, then:

```
python3 _gen_book.py     # regenerates read/ (all documents + contents page)
git add -A && git commit && git push
```

`_gen_book.py` reads the numbered manuscript files, converts the constrained
markdown (smart quotes, scene breaks, per-document mastheads) to HTML, and
writes one styled page per document into `read/` plus `read/index.html`
(the contents page). The document list, reading order, and each document's
"room" (its CSS style) live in the `DOCS` table at the top of that script.

### Files

- `index.html` — home page (hand-written: hero, blurb, downloads, authorship note).
- `read/` — **generated**; do not edit by hand. Re-run `_gen_book.py`.
- `style.css` — the constant reading "spine" (measure, size, nav, pager, footer)
  plus the home/contents pages.
- `book.css` — the per-document "rooms". Each document gets a body class
  (`doc-strand`, `doc-report`, `doc-ar19`, …) that restyles only the chrome —
  masthead, headings, accent, paper — never the reading measure or size.
- `downloads/` — `the_wire_branch.pdf` (6×9 interior) and `the_wire_branch.epub`,
  copied from the book repo's build output. Refresh these when the book rebuilds.
- `_gen_social_card.py` — regenerates `images/social-card.png`, the OG share card.
  Placeholder until the real cover exists; re-run after it does.

### Local preview

Serve the folder over HTTP (root-relative links need a server root, not `file://`):

```
python3 -m http.server 4173
# then open http://localhost:4173/
```

## Setup

1. Repo: `sbgeoaiphd/twb_website`
2. Settings → Pages → Source: "Deploy from a branch" → `main` → `/ (root)`
3. Custom domain is set via the `CNAME` file (`thewirebranch.com`). GitHub reads this on deploy.
4. In the domain registrar, add these DNS records for the apex (`thewirebranch.com`):
   - `A` → `185.199.108.153`
   - `A` → `185.199.109.153`
   - `A` → `185.199.110.153`
   - `A` → `185.199.111.153`
   - `CNAME` for `www` → `sbgeoaiphd.github.io`
5. Wait for DNS propagation, then in Settings → Pages enable **Enforce HTTPS** once GitHub provisions the certificate (can take up to 24h).

### Notes from the marenonnostrum.com setup

- The four `A` records are GitHub's fixed Pages IPs; they do not change between projects.
- Do **not** also point the apex at a registrar parking/forwarding record — a stray `A`/`ALIAS`/forwarding rule on the root is what causes the "domain not verified" / cert-stuck problems.
- If the registrar already has old `A` records on the apex (or an `@` forwarding rule), delete them before adding the four above.
- `www` is optional but recommended; the `CNAME` record above lets `www.thewirebranch.com` redirect to the apex.
- "Enforce HTTPS" stays greyed out until the cert is issued. That's normal — check back later, don't keep toggling.
