# EcuTek 370Z ProECU documentation in Markdown

Two pages from the EcuTek Support knowledge base in the Confluence `SUPPORT`
space under `EcuTek Knowledge Base / Vehicle Specific Guides / Nissan / 370Z`,
converted into self-contained Markdown with local images. The result supports
both human reading and machine processing.

The 370Z uses the VQ37VHR with VVEL, so both pages are directly relevant to the
VQ HR ECU project.

## Contents

| Document | File | Page ID | Version | Headings | Images | MD size |
|----------|------|---------|---------|---------:|-------:|--------:|
| 370Z ProECU Tuning Guide | [tuning-guide/](tuning-guide/370Z-ProECU-Tuning-Guide.md) | 7143430 | 22 | 72 | 67 | 56 KB |
| 370Z ProECU RaceROM Supplement | [racerom-supplement/](racerom-supplement/370Z-ProECU-RaceROM-Supplement.md) | 6881638 | 25 | 110 | 106 | 76 KB |

Sources:

- Tuning Guide: https://ecutek.atlassian.net/wiki/spaces/SUPPORT/pages/7143430
- RaceROM Supplement: https://ecutek.atlassian.net/wiki/spaces/SUPPORT/pages/6881638

## Layout

```text
markdown/
  README.md
  tuning-guide/
    370Z-ProECU-Tuning-Guide.md
    images/            # 67 files, relative links (images/...)
  racerom-supplement/
    370Z-ProECU-RaceROM-Supplement.md
    images/            # 106 files
```

Each document is self-contained: images are in an adjacent `images/` directory,
so the complete document directory can be moved as one unit. Image filenames
match their Confluence attachment names and encode dates.

## Acquisition

The saved source HTML (`*.html` plus `*_files/`) in the parent directory consists
of Confluence Cloud SPA captures. Media is loaded lazily through blob URLs and
the saved copy does not associate it with text positions; the RaceROM capture
lacked 12 of 13 images. Both pages were therefore rebuilt directly from the
public Confluence REST API in `body.export_view` format, which supplies clean
rendered HTML with `<img>` elements in the correct positions. The HTML was then
converted to Markdown and every attachment was downloaded through its standard
download link. The `SUPPORT` space allows anonymous access.

## Conversion decisions

- Headings use the GitHub anchor algorithm, and internal page links point to
  those anchors. No broken internal links remain. Each file begins with a
  collapsible table of contents using `<details>`.
- Confluence Info/Note/Warning macros become GitHub admonitions while preserving
  color semantics: Warning (red) -> `[!CAUTION]`, Note (yellow) ->
  `[!WARNING]`, Information (blue) -> `[!NOTE]`, and Tip (green) -> `[!TIP]`.
- Multi-column layout macros become sequential text; tables become Markdown
  tables.
- Decorative Unicode punctuation is normalized to ASCII, including paired
  quotes, arrows, and a stray Symbol-font bullet. En dashes, degree signs, and
  the middle dot in `lbs·ft` are preserved. Source typos are not corrected.
- Each file's YAML header records the source URL, page ID, version, and retrieval
  date.

## Unavailable images

Two Tuning Guide images cannot be retrieved anonymously. Inline
`*[image unavailable: ...]*` placeholders preserve their positions, with the
original URLs in HTML comments:

- `Nissan 370z` (`www.ecutek.com/.../image1.jpg.aspx`) is a marketing image that
  returns 404;
- `CPC Enable.jpg` (`api.media.atlassian.com/...`) was embedded with an expired
  token and is not among the page attachments.

The remaining 173 images, 67 plus 106, are stored locally.
