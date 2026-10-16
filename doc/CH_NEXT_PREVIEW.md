# Swiss German preview with `next/ch`

This is a local prototype of the DARCdown → MDX → Astro build. It uses the
current Swiss content and question repositories without modifying their
canonical files or publishing a site. The Swiss variant builds exactly three
course editions from `toc/HB.json`:

| Edition | Content selected from `HB.json` |
| --- | --- |
| `NE` | Sections N and E (HB3) |
| `A` | Sections A (HB3 → HB9 upgrade) |
| `NEA` | Sections N, E and A (complete course) |

The current Swiss question pool is `fragenkatalog_4.json`. The preparation
tool merges its 1,665 questions with the historical `metadata3b.json` and
derives missing presentation metadata, including drawing references, in an
ignored preview directory. The source trees are linked read-only from the
German generator export, so do not rerun its staging step while a preview is
being built. `source-state.json` records the source commits and hashes of the
catalog, metadata, TOC, snippets and extracted generator resources. The audit
rejects changed inputs.

The generator-owned Swiss resources live in
`50ohm-contents-ch/generator_extra_content/de/`. The preparation step links
that resource pack and renders its five HTML page templates with the current
canonical snippets. Astro reads those rendered pages and `labels.json` from
the prepared input, rather than carrying copies of their text in this
generator. The Swiss header, footer, page title and navigation use those
labels; `infos` and `pruefung` come from the staged canonical static pages.
The original DARC Astro profile remains available when `PUBLIC_SITE_PROFILE`
is not `ch`.

## Requirements

- Python 3.14 with `uv`; this branch selects 3.14 in `.python-version`.
- Node.js at least 22.12 and npm at least 9.6.5 for Astro 7. On the first
  test machine, npm 9.2.0 emitted an engine warning but the build succeeded.
- The sibling `50ohm-contents-ch` and `50ohm-question-pool` repositories.
- No LaTeX installation is needed for this MDX/Astro preview.

## Rebuild from the orchestrator directory

The following commands create a new ignored input and output for each run.
They write only to `work/` in the Swiss content repository and ignored
`tmp/`, `node_modules/`, `frontend/public/` and `frontend/dist/` in this
generator repository. The public and dist directories are generated preview
assets, not a release.

```bash
pushd /home/jjcarron/proj/50-Ohms/ham-translator >/dev/null

pushd 50ohm-contents-ch >/dev/null
UV_CACHE_DIR=../tmp/next-uv-cache uv run --locked python \
  tools/run_multilingual_canonical_build.py --language de --skip-build
popd >/dev/null

pushd 50ohm-generator-next >/dev/null
run_id="$(date +%Y%m%d-%H%M%S)"
input_dir="tmp/ch-input/de-$run_id"
build_dir="tmp/ch-build/de-$run_id"
UV_CACHE_DIR=../tmp/next-uv-cache uv sync --locked --python 3.14
UV_CACHE_DIR=../tmp/next-uv-cache uv run --locked --python 3.14 python \
  tools/prepare_ch_input.py \
  --source ../50ohm-contents-ch/work/generator-input/de \
  --output "$input_dir" \
  --content-repo ../50ohm-contents-ch \
  --question-repo ../50ohm-question-pool
UV_CACHE_DIR=../tmp/next-uv-cache uv run --locked --python 3.14 ohm \
  --config "$input_dir/build-config.json" \
  --input "$input_dir" --output "$build_dir" \
  --format mdx --edition NE --edition A --edition NEA \
  --no-render-solutions

pushd frontend >/dev/null
npm ci --no-audit --no-fund
env XDG_CONFIG_HOME=../tmp/astro-config ASTRO_TELEMETRY_DISABLED=1 \
  OHM_BUILD_DIR="../$build_dir" \
  OHM_CH_INPUT_DIR="../$input_dir" \
  PUBLIC_SITE_PROFILE=ch PUBLIC_SHUFFLE_ANSWERS=false \
  npm run build
popd >/dev/null

python tools/audit_ch_build.py \
  --source "$input_dir" --build "$build_dir" --site frontend/dist \
  --output "tmp/ch-audit-$run_id.json"
popd >/dev/null
popd >/dev/null
```

The audit lists every course reference absent from the current question
catalog. Add `--strict-references` to make that condition fail the audit.
Serve `frontend/dist/` over HTTP for browser inspection; root-relative URLs
mean `file://` is unsuitable. On the machine that built the preview, run this
in a separate terminal (it does not rebuild anything):

```bash
pushd /home/jjcarron/proj/50-Ohms/ham-translator/50ohm-generator-next/frontend/dist >/dev/null
python -m http.server 8765 --bind 127.0.0.1
# Stop the server with Ctrl-C, then run: popd >/dev/null
```

Open `http://127.0.0.1:8765/` for the Swiss home page, or `/NE/`, `/A/`
and `/NEA/` for the three editions. The generated files are owned by the
local user and readable by that user; binding to loopback restricts the
preview server to the same machine. This is a local preview, not a deployment.

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
content questions and were not silently rewritten in the generator. The
search page remains a port of the canonical German search page with nested-URL
adjustments. The Astro shell still has some root-absolute URLs. Slides,
solution pages and the exam simulator are not ported to MDX/Astro. A stray `</tip>` in the
German `relaisfunkstellen` source is omitted from generated MDX with a build
warning; the canonical source is unchanged. These points need separate
review before any public deployment.
