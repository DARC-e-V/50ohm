# Swiss adaptations in the `next` generator

This note summarizes the Swiss-specific layer used by the local Astro preview on
`next/ch-astro-preview`. The goal is to make the current Swiss course usable for
a demonstration while keeping the changes identifiable for possible reuse in
the upstream generator. This is a country profile, not a generic redesign.

## Inputs and course structure

- Course content is staged from the Swiss canonical repository;
  question data comes separately from the Swiss question-pool canonical. The
  build wrapper records the actual source revisions and hashes.
- The selected question catalog is the current `fragenkatalog_4.json`. The
  preparation step derives the presentation metadata required by the frontend,
  using historical `metadata3b.json` entries where available and filling gaps
  for current questions. It does not substitute historical question text.
- The Swiss table of contents produces three editions: `NE` (N and E sections,
  HB3), `A` (A sections, HB3-to-HB9 upgrade), and `NEA` (the complete course).
  Section selection is based on the TOC; it does not infer a question class.
- Current canonical questions use `class: 0`. The Astro schema permits this
  Swiss catalog value without inventing an N/E/A mapping. Answer shuffling is
  disabled for review builds so the catalog order is preserved.

## Localization and page shell

Astro i18n builds `de`, `fr`, and `it` from the configured locale list, with
language-prefixed routes. Prepared Swiss resources provide the localized
header, navigation labels, footer, and extracted static pages. The Swiss header
also supports the optional BETA notice, feedback link, and language selector;
the footer displays the release identifier. It uses the USKA emblem and the
Swiss `50ohm_ch.svg` wordmark rather than the DARC `50ohm.svg` asset.

The language selector preserves the current route and changes only its locale
prefix. The three generated sites currently have matching paths for all 832
pages, so a section, search page, or other route remains open after switching
between `de`, `fr`, and `it`.

The home route owns the page layout. `SwissHome.astro` now renders only the
extracted page body, preventing a second nested header and footer and ensuring
the route's locale is used for the single page shell.

## Swiss theme and shared assets

The frontend reuses the generator's shared styles and assets, with a Swiss
country theme in `frontend/public/assets/style-fiftyohm.css`. The primary
controls, links, alerts, and mobile navigation use the Swiss red palette
(`#ac2d24`, with `#80221c` for hover/link states), consistent with the existing
Swiss releases. Course styles read the theme's CSS variables for links and
primary accents so they do not reintroduce the generic blue. Relative image and
asset paths in extracted pages are rooted at `/assets/`, which keeps them
resolvable under locale-prefixed routes such as `/de/`. This keeps the demo
visually coherent while making country-specific assets and colors easy to
separate or configure later.

The Swiss favicon assets use the same red (`#ac2d24`). `BaseLayout.astro` links
to the explicitly named `icon-ch.png`, `icon-ch.svg`, and `mask-icon-ch.svg`
files. The root-level `public/icon.*` fallbacks are red as well. The `-ch`
filenames distinguish these assets from the upstream blue icons and avoid
stale browser favicon caches.

## Question answer presentation

Answer labels (`A:` through `D:`) are generated with CSS pseudo-elements in
`style-course.css`; their `margin-right` supplies the space after each colon
for every question without changing pool text.

The frontend's `questionHtml()` presents a standalone
`\qty{number}{\degree}` as plain degree text (for example, `90°`) so it uses
the same Roboto face as the other answer text. Other standalone `\qty`
expressions receive math delimiters so the existing KaTeX auto-renderer can
typeset them. This is a presentation fallback for source quantities without
`$…$` delimiters; it does not rewrite canonical question data.

## Build and current boundaries

`tools/build_ch_astro_preview.sh` stages the two canonical inputs, prepares
localized MDX and media, runs Astro, then writes per-language audits. The
preview includes localized question search and indexes, nested course URLs, and
visible placeholders for unresolved question references. It is generated
locally and is not a deployment workflow.

Slides, solution pages, and the exam simulator are not yet ported. Some extracted
pages still contain DARC-specific references, and the current course includes
145 references to question identifiers absent from the active Swiss pool; these
remain visible as placeholders and need separate content decisions. See
[`CH_NEXT_PREVIEW.md`](CH_NEXT_PREVIEW.md) for build commands, requirements,
audit details, and the dated results of the verified runs.
