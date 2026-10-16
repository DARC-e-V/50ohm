# Swiss multilingual preview with `next/ch`

The local DARCdown → MDX → Astro prototype reads the Swiss canonical content
and question repositories. It builds each language in `frontend/i18n.config.json`
with Astro i18n and a language prefix, including the default language. The current
configuration is `de`, `fr`, `it`, with `de` as the default.

Each language contains exactly three course editions from its staged `toc/HB.json`:

| Edition | Content selected from `HB.json` |
| --- | --- |
| `NE` | Sections N and E (HB3) |
| `A` | Sections A (HB3 → HB9 upgrade) |
| `NEA` | Sections N, E and A (complete course) |

The wrapper stages current canonical content through the existing content build
wrapper. `--tag` selects the **question-pool** revision; it does not select an old
content revision. Preparation reads each language's `fragenkatalog_4.json`, merges
historical `metadata3b.json` presentation data, and derives missing metadata for
Swiss questions. No historical question text is substituted into the catalog.

Source trees are linked read-only from their generator export. Do not rerun staging
concurrently with a build that consumes that export. `source-state.json` records
the commits, actual language and input hashes. Each language's audit checks source
stability, catalog and section counts, indexes and question SVGs.

Swiss labels and injected pages come from the extracted resources in
`50ohm-contents-ch/generator_extra_content/<language>/`, through the prepared input.
The header includes the language links, optional BETA warning and feedback control.
The footer displays the explicit release ID. The three language controls point to
the locally generated language home pages. Site preparation, MDX, indexes and
course media remain separated by language.

## Requirements

- Python 3.14 with `uv` and the locked project environments.
- Node.js at least 22.12 and npm at least 9.6.5 for the installed Astro 7 stack.
- The sibling `50ohm-contents-ch` and `50ohm-question-pool` repositories.
- No LaTeX installation for this MDX/Astro preview.

## Build from the orchestrator

Mode: writes generated preview files and content staging; does not publish a
release or change canonical source files. The wrapper reads the locale list from
configuration, then runs staging, preparation, MDX, asset qualification, Astro,
and an audit for each language.

```bash
pushd /home/jjcarron/proj/50-Ohms/ham-translator >/dev/null
pushd 50ohm-generator-next >/dev/null
tools/build_ch_astro_preview.sh \
  --release-id next-2026-10-17-QP_Revision_3.0.3-markup \
  --tag Revision_3.0.3 --beta
popd >/dev/null
popd >/dev/null
```

Use a suitable release ID for subsequent builds. `--feedback-url URL` overrides
feedback destination; omit `--beta` for a non-beta preview. `--fr-url` and
`--it-url` are retired: the multilingual sites are built together. `--help` lists
supported arguments. The wrapper keeps the existing dependencies when installed;
on a first build it runs `npm ci` if `frontend/node_modules/` is absent.

Outputs:

- content staging: `50ohm-contents-ch/work/generator-input/<language>/`;
- prepared inputs: orchestrator `tmp/ch-input/<run-id>/<language>/`;
- MDX: orchestrator `tmp/ch-build/<run-id>/<language>/`;
- logs: orchestrator `tmp/ch-preview-logs/<run-id>/`;
- Astro cache: orchestrator `tmp/astro-cache/<run-id>/`;
- sites: `50ohm-generator-next/frontend/dist/{de,fr,it}/`;
- audits: `50ohm-generator-next/tmp/ch-audit-<run-id>-<language>.json`.

The wrapper stops at the first failed step and prints the log location. Completion
requires all three language audits to succeed; an old or partially written `dist`
is not evidence of success. Its audit records missing question references without
failing by default. `--strict-references` is available on `tools/audit_ch_build.py`
when those curriculum differences must instead be treated as errors.

## Technical markup validation

Before investigating a generator error, compare translated formulas to German
with the deterministic workflow in [TECHNICAL_FORMAT_VALIDATION.md](TECHNICAL_FORMAT_VALIDATION.md).
Its `--markup-only` mode repairs source-backed delimiters and representations while
preserving translated prose and numeric values. A translated HTML math span or a
raw `\qty` where German has `$...$` must be corrected in the canonical translation,
not hidden by an Astro workaround. If German uses a plain measurement, the target
should use the corresponding plain representation. Genuine source defects and
ambiguous translated formulas need separate review.

## View the completed preview

Mode: read-only HTTP serving of `frontend/dist/`.

```bash
pushd /home/jjcarron/proj/50-Ohms/ham-translator/50ohm-generator-next/frontend/dist >/dev/null
python -m http.server 8765 --bind 127.0.0.1
# Stop with Ctrl-C, then run: popd >/dev/null
```

Open `http://127.0.0.1:8765/de/`, `/fr/`, or `/it/`. Each language has `/NE/`,
`/A/`, `/NEA/` and `/suche/` routes below its language prefix. The HTTP root is
`frontend/dist/`; the home directory is not served. Loopback binding restricts
access to this machine. This is a local preview, not a deployment.

## Verified first run (16 October 2026)

- Content commit: `340ade0f185211876a43499046672374ba4aa549`.
- Question commit: `4e29615b2c89510a7a026815be5b83335a7cbd88`
  (`Revision_3.0.2`). This repository also has unrelated uncommitted
  documentation; the staged question catalog was rebuilt from the current pool.
- 1,665 questions emitted; 142 required supplemental metadata. Three of
  those have pictures: `AI307` (57), `EI305` and `EI306` (36).
- Section counts: `NE` 232, `A` 148, `NEA` 380. Astro builds 832 pages, including
  the extracted `todo.html` destination. Both
  search indexes and referenced question SVGs are present.
- Python tests: 114 passed, 3 skipped. Ruff passed. Astro build passed;
  `astro check` found 0 errors, 0 warnings and 37 upstream hints.

## Limits before any release

The source course contains **145 references to question identifiers absent
from the current Swiss pool**. They render as visible “Frage nicht gefunden”
placeholders in this preview. The complete ID list is regenerated in
`tmp/ch-audit-<run-id>.json`; all 145 exist in the historical 3b catalog.
Of these, 40 are recorded under `pruned` in the current full Swiss catalog;
the other 105 are absent from both its active questions and `pruned`.
Resolving those references requires a
content or curriculum decision; this prototype does not substitute historical
question text.

The extracted Swiss source resources themselves still contain some DARC
references, notably the mentor and local-course pages, and the current German
canonical `pruefung.html` still describes the German exam. Those are source
content questions and were not silently rewritten in the generator. The search page remains a localized port of the search interface with nested-URL
adjustments. The Astro shell still has some root-absolute URLs. Slides,
solution pages and the exam simulator are not ported to MDX/Astro. A stray `</tip>` in the
German `relaisfunkstellen` source is omitted from generated MDX with a build
warning; the canonical source is unchanged. These points need separate
review before any public deployment.

## Verified multilingual run (17 October 2026)

Run `20261017-002200` completes preparation, MDX rendering, media, Astro and audits for all configured languages: DE, FR and IT. Each produces 832 pages from 1,665 questions, with the three Swiss editions NE/A/NEA. The 145 known missing question references remain visible placeholders.

Canonical representation corrections and the reviewed Italian dipole correction are recorded in `50ohm-contents-ch/review/technical_format/2026-10-17/` relative to the orchestrator. The build used the working canonical after recovery checkpoint `3e16d02f0`; the checkpoint hash alone does not identify the corrected working tree. `verification.json` records corrected file hashes.

Technical-format tests: 27 passed. Content tests: 62 passed. Astro check: 0 errors, 0 warnings, 39 hints. Re-running the markup repair planner proposes no further automatic representation corrections; broader diagnostics remain for separate review. Logs are in `tmp/ch-preview-logs/20261017-002200` under the orchestrator; the sites are in `frontend/dist/{de,fr,it}/index.html`.
