#!/usr/bin/env python3
"""Generate the reading pages + contents page for thewirebranch.com.

The manuscript repo is the single source of truth. This reads the numbered
markdown files, converts the small constrained markdown to site HTML, and
writes one styled page per document into /read/ plus the contents index.

Workflow for a text edit: edit the markdown in the book repo, run this,
`git push`. Nothing under /read/ is hand-edited.

    python3 _gen_book.py
"""

import html
import re
from pathlib import Path

BOOK = Path("/Users/lgnd/Documents/cowork/fiction/the_wire_branch")
SITE = Path("/Users/lgnd/Documents/cowork/fiction/twb_website")
OUT = SITE / "read"

# ── the documents, in reading order ──
# room     → CSS class selecting the "room" (styling) in book.css
# eyebrow  → small site-chrome marker above the masthead ("" = none)
# label    → neutral name used in the contents list + pager (never the title,
#            so the documentary reveal is not spoiled)
DOCS = [
    dict(file="03_prologue.md",        slug="prologue",         room="doc-report",          eyebrow="Prologue",   label="Prologue"),
    dict(file="04_chapter_1.md",       slug="chapter-1",        room="doc-strand",          eyebrow="Chapter 1",  label="1"),
    dict(file="05_chapter_2.md",       slug="chapter-2",        room="doc-commonreader",    eyebrow="Chapter 2",  label="2"),
    dict(file="06_chapter_3.md",       slug="chapter-3",        room="doc-helix",           eyebrow="Chapter 3",  label="3"),
    dict(file="07_chapter_4.md",       slug="chapter-4",        room="doc-concourse",       eyebrow="Chapter 4",  label="4"),
    dict(file="08_chapter_5.md",       slug="chapter-5",        room="doc-anthemis-blog",   eyebrow="Chapter 5",  label="5"),
    dict(file="09_chapter_6.md",       slug="chapter-6",        room="doc-anthemis-report", eyebrow="Chapter 6",  label="6"),
    dict(file="10_chapter_7.md",       slug="chapter-7",        room="doc-ar19",            eyebrow="Chapter 7",  label="7"),
    dict(file="11_epilogue.md",        slug="epilogue",         room="doc-report",          eyebrow="Epilogue",   label="Epilogue"),
    dict(file="12_coda.md",            slug="coda",             room="doc-letter",          eyebrow="Coda",       label="Coda"),
    dict(file="13_authorship_note.md", slug="authorship-note",  room="doc-frame",           eyebrow="",           label="A Note on Authorship", aux=True),
]

# ── inline conversion ──

def smarten(t):
    t = re.sub(r'(^|[\s(\[—-])"', '\\1“', t)   # opening double
    t = t.replace('"', '”')                     # closing double
    t = re.sub(r"(\w)'(\w)", '\\1’\\2', t)      # intra-word apostrophe
    t = re.sub(r"(^|[\s(\[—-])'(\w)", '\\1‘\\2', t)  # opening single
    t = t.replace("'", '’')                     # remaining → ’
    return t

def inline(t):
    t = html.escape(t, quote=False)
    t = smarten(t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)  # links
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)          # bold
    t = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', t)                      # italic
    return t

# ── segment splitting: the manuscript separates blocks with `---` lines ──

def split_segments(text):
    segs, cur = [], []
    for line in text.splitlines():
        if line.strip() == '---':
            segs.append(cur); cur = []
        else:
            cur.append(line)
    segs.append(cur)
    # drop empty leading/trailing segments
    segs = [s for s in segs if any(l.strip() for l in s)]
    return segs

# ── masthead: the header block (venue / title / deck / byline / metadata) ──

BOLD_LINE = re.compile(r'\*\*')
ITALIC_ONLY = re.compile(r'^\*[^*].*\*$')
BYLINE = re.compile(r'^\*?(By|Posted by)\b', re.I)

def render_masthead(lines):
    out, seen_title = [], False
    for raw in lines:
        s = raw.strip()
        if not s:
            continue
        if s.startswith('### '):
            out.append(f'<p class="doc-deck">{inline(s[4:])}</p>')
        elif s.startswith('## '):
            out.append(f'<h2 class="doc-subtitle">{inline(s[3:])}</h2>')
        elif s.startswith('# '):
            out.append(f'<h1 class="doc-title">{inline(s[2:])}</h1>')
            seen_title = True
        elif BOLD_LINE.search(s):
            out.append(f'<p class="meta">{inline(s)}</p>')          # report metadata
        elif BYLINE.match(s):
            out.append(f'<p class="doc-byline">{inline(s)}</p>')
        elif not seen_title:
            out.append(f'<p class="doc-venue">{inline(s)}</p>')     # masthead venue
        else:
            out.append(f'<p class="meta">{inline(s)}</p>')          # sub-metadata after title
    return '<header class="masthead">\n' + '\n'.join(out) + '\n</header>'

# ── body: paragraphs, headings, blockquotes, scene breaks between segments ──

END_MARK = re.compile(r'^\*\*.+\*\*$')

def render_body_segment(lines, first_para_flag):
    out, i, n = [], 0, len(lines)
    while i < n:
        s = lines[i].strip()
        if not s:
            i += 1; continue
        if s.startswith('### '):
            out.append(f'<h3>{inline(s[4:])}</h3>'); i += 1; continue
        if s.startswith('## '):
            out.append(f'<h2>{inline(s[3:])}</h2>'); i += 1; continue
        if s.startswith('# '):
            out.append(f'<h2>{inline(s[2:])}</h2>'); i += 1; continue
        if s.startswith('>'):
            ql = []
            while i < n and lines[i].lstrip().startswith('>'):
                content = lines[i].lstrip()[1:].strip()
                if content:
                    ql.append(content)
                i += 1
            inner = '\n'.join(f'<p>{inline(q)}</p>' for q in ql)
            out.append(f'<blockquote>\n{inner}\n</blockquote>'); continue
        if END_MARK.match(s):
            out.append(f'<p class="end-note">{inline(s[2:-2])}</p>'); i += 1; continue
        # paragraph: gather until blank / structural line
        para = []
        while i < n:
            t = lines[i].strip()
            if (not t or t.startswith('#') or t.startswith('>')
                    or END_MARK.match(t)):
                break
            para.append(t); i += 1
        cls = ' class="first"' if first_para_flag[0] else ''
        first_para_flag[0] = False
        out.append(f'<p{cls}>{inline(" ".join(para))}</p>')
    return '\n'.join(out)

def render_body(segments):
    first_para_flag = [True]
    parts = []
    for idx, seg in enumerate(segments):
        if idx > 0:
            parts.append('<hr class="scene">')
        parts.append(render_body_segment(seg, first_para_flag))
    return '<div class="body">\n' + '\n'.join(parts) + '\n</div>'

# ── page assembly ──

# Reading pages and the contents page both live in read/. Links are relative
# so the site works opened straight off disk (file://) as well as on Pages:
#   root asset  → ../style.css   sibling doc → chapter-2.html   contents → index.html
def reading_bar(prev, nxt):
    prev_l = (f'<a href="{prev["slug"]}.html" title="Previous: {prev["label"]}" '
              f'aria-label="Previous: {prev["label"]}">&larr;</a>'
              if prev else '<span class="rb-off">&larr;</span>')
    next_l = (f'<a href="{nxt["slug"]}.html" title="Next: {nxt["label"]}" '
              f'aria-label="Next: {nxt["label"]}">&rarr;</a>'
              if nxt else '<span class="rb-off">&rarr;</span>')
    return ('<nav class="reading-bar">\n'
            '  <a href="../index.html" class="home-mark">The Wire Branch</a>\n'
            f'  <span class="rb-nav">{prev_l}<a href="index.html">Contents</a>{next_l}</span>\n'
            '</nav>')

def pager(prev, nxt):
    left = (f'<a href="{prev["slug"]}.html">← {prev["label"]}</a>'
            if prev else '<span class="spacer"></span>')
    right = (f'<a href="{nxt["slug"]}.html">{nxt["label"]} →</a>'
             if nxt else '<span class="spacer"></span>')
    return (f'<nav class="pager">\n  {left}\n'
            f'  <a href="index.html" class="contents">Contents</a>\n'
            f'  {right}\n</nav>')

DESC = ("The Wire Branch, by S.J. Barrett — speculative fiction told as a "
        "dossier of documents recovered from a timeline that does not exist.")

def build_page(doc, prev, nxt):
    segs = split_segments((BOOK / doc["file"]).read_text(encoding="utf-8"))
    if len(segs) >= 3:
        # standard shape: seg[0] chapter-number, seg[1] masthead, seg[2:] body.
        # (We ignore seg[0]; the eyebrow comes from DOCS instead.)
        header_seg, body_segs = segs[1], segs[2:]
    else:
        # no `---` dividers (e.g. the authorship note): the leading heading
        # line(s) are the masthead; everything after is a single body segment.
        lines = segs[0] if segs else []
        header_seg, body_lines, in_header = [], [], True
        for l in lines:
            if in_header and l.strip().startswith('#'):
                header_seg.append(l)
            elif in_header and not l.strip():
                continue
            else:
                in_header = False
                body_lines.append(l)
        body_segs = [body_lines]
    eyebrow = (f'<p class="doc-number">{html.escape(doc["eyebrow"])}</p>'
               if doc["eyebrow"] else '')
    masthead = render_masthead(header_seg)
    body = render_body(body_segs)
    tab = f'{doc["eyebrow"] or doc["label"]} — The Wire Branch'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(tab)}</title>
  <meta name="description" content="{DESC}">
  <meta name="robots" content="index,follow">
  <link rel="stylesheet" href="../style.css">
  <link rel="stylesheet" href="../book.css">
</head>
<body class="reading {doc['room']}">

{reading_bar(prev, nxt)}

<article class="document">
{eyebrow}
{masthead}
{body}
</article>

{pager(prev, nxt)}

<footer>
  &copy; 2026 S.J. Barrett &middot; <a href="../index.html"><em>The Wire Branch</em></a>
</footer>

</body>
</html>
"""

# ── contents page ──

SITE_NAV = ('<nav class="site">\n'
            '  <a href="../index.html">Home</a>\n'
            '  <a href="index.html" class="active">Read</a>\n'
            '  <a href="../index.html#contact">Contact</a>\n'
            '  <a href="https://marenonnostrum.com/" class="ext">Mare Non Nostrum</a>\n'
            '</nav>')

COLOPHON = """  <div class="colophon">
    <p><em>The Wire Branch</em> is published here in full, free to read. It is
    also available to download and keep.</p>
    <p>&copy; 2026 S.J. Barrett. You are welcome to read, download, and share it
    in unmodified form; please don&rsquo;t republish it or put it to commercial
    use. The book lives at thewirebranch.com &mdash; link here rather than
    re-hosting it, so a reader always arrives at the whole thing.</p>
    <div class="actions">
      <a class="btn small" href="../downloads/the_wire_branch.pdf">PDF</a>
      <a class="btn small" href="../downloads/the_wire_branch.epub">EPUB</a>
    </div>
  </div>"""

def build_contents():
    rows = []
    for d in DOCS:
        aux = ' aux' if d.get("aux") else ''
        rows.append(f'    <a class="toc-entry{aux}" href="{d["slug"]}.html">'
                    f'<span class="toc-label">{html.escape(d["label"])}</span></a>')
    toc = '\n'.join(rows)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Read — The Wire Branch</title>
  <meta name="description" content="{DESC}">
  <link rel="stylesheet" href="../style.css">
</head>
<body class="home">

{SITE_NAV}

<div class="contents-head">
  <h1>The Wire Branch</h1>
  <div class="byline">Contents</div>
</div>

<nav class="toc">
{toc}
</nav>

{COLOPHON}

<footer>
  &copy; 2026 S.J. Barrett &middot; <em>The Wire Branch</em>
</footer>

</body>
</html>
"""

# ── run ──

def main():
    OUT.mkdir(exist_ok=True)
    for idx, doc in enumerate(DOCS):
        prev = DOCS[idx - 1] if idx > 0 else None
        nxt = DOCS[idx + 1] if idx + 1 < len(DOCS) else None
        (OUT / f'{doc["slug"]}.html').write_text(build_page(doc, prev, nxt), encoding="utf-8")
    (OUT / "index.html").write_text(build_contents(), encoding="utf-8")
    print(f"Wrote {len(DOCS)} reading pages + contents to {OUT}")

if __name__ == "__main__":
    main()
