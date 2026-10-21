# Canonical technical-format review and correction

## Purpose and review sequence

The German canonical is the reference for technical values and LaTeX
structure in the French and Italian canonical bodies. Whenever notation is
deterministically equivalent, this workflow imposes the German technical
form in the target locale. It preserves translated words used as formula
labels, reports genuine value or structural differences for review, and never
edits source files during the audit. It does not use AI.

The intended sequence is:

1. Run the comparison. It creates a detailed JSON manifest, a CSV review
   sheet and a short Markdown summary.
2. Review the findings CSV and critical cases. In the separate decisions
   CSV, keep `apply` for deterministic format-equivalent cases: these must use
   the exact German technical form and cannot be changed to `keep` or `manual`.
   Leave genuine value or structural differences blank pending human
   validation. Use `keep` for accepted translated formula labels and
   `manual` where an editorial correction is still needed.
3. Run the apply tool without `--apply` first. This verifies file hashes and
   spans and writes a dry-run manifest without changing canonical files.
4. After the dry run is correct, rerun with `--apply`. The tool checks the
   same preconditions again, applies only approved spans and records before
   and after hashes in an applied manifest.
5. Rerun the comparison and inspect the Git diff. Commit the canonical files
   together with the approved review CSV and applied manifest in a tracked
   review record.

The generator and the human review of the questions remain separate. This
check helps ensure that format and technical-notation defects in translated
content are not mistaken for generator defects. It does not replace the
editorial or question review.

## Run from the orchestrator

The locale list comes from `frontend/i18n.config.json`; `defaultLocale` is the
reference and all other configured locales are targets.

```bash
pushd /home/jjcarron/proj/50-Ohms/ham-translator >/dev/null
pushd 50ohm-generator-next >/dev/null
uv run --locked python tools/validate_canonical_technical_format.py
popd >/dev/null
popd >/dev/null
```

By default this reads `../50ohm-contents-ch/canonical/` and writes only to the
orchestrator's ignored `tmp/` directory:

```text
tmp/canonical-technical-format-validation.json
tmp/canonical-technical-format-review.csv
tmp/canonical-technical-format-critical-review.csv
tmp/canonical-technical-format-decisions.csv
tmp/canonical-technical-format-review.md
```

The comparison exits with status `1` if the report contains findings. Read
the manifest and review files; this status is a review signal, not a claim
that every finding is an error. The manifest records the canonical Git commit,
canonical worktree state, locale configuration hash, and per-file hashes.

## Findings and correction proposals

- `technical_format_mismatch`: the tokens and values are equivalent, but the
  exact technical text differs. This includes spacing and decimal comma/dot
  differences such as `20 dB` versus `20dB` or `3,0 kHz` versus `3.0 kHz`, as
  well as supported forms such as `\\frac{5}{8}` versus `5/8` and known aliases
  for the same unit command. The CSV proposes the German text; the decisions
  file preselects `apply`, and the apply tool rejects any other decision for
  these cases. Equivalent forms are normalized to German.
- `localized_unit_word_case`: the value is identical, while capitalization of
  a translated unit word such as `Bit`/`bit` follows the target language. Keep
  the localized form; it is reported with other translated labels, not as a fix.
- `localized_formula_label`: only words inside matched math-label arguments
  differ, such as `\mathrm{Sender}` versus `\mathrm{émetteur}`. Codex
  recommends keeping the translated words; these are not data mismatches.
- `localized_label_markup_mismatch`: a translated label is retained while its
  LaTeX wrapper differs. The CSV proposes German wrapper syntax with the
  translated label text preserved.
- `technical_token_mismatch`: a value, unit, symbol or command differs. If
  the regions still line up one-to-one, the CSV proposes the exact German
  region but marks it critical for human review. The proposal must not be
  accepted merely because it is mechanically available.
- `same_technical_tokens_different_order`: the tokens are present in a
  different sequence. No automatic replacement is proposed.
- `same_technical_tokens_different_boundaries`: formula boundaries or
  delimiters differ, which can indicate a split expression. No automatic
  replacement is proposed.
- `malformed_technical_markup`: a math delimiter, span or brace is unmatched or
  nested. Source-backed missing delimiters can be repaired by the markup phase;
  unresolved syntax remains a manual case.
- `missing_translation_body` and `missing_german_source_body`: one side of a
  language pair is absent. These are coverage decisions, not text patches.

The scanner reads canonical `body.<locale>.md` and `body.<locale>.html`
files. It extracts delimited math, HTML math spans, TeX commands (including isolated commands) outside math, and a finite set of common number/unit expressions
in prose. It ignores fenced/inline code and HTML `script`/`style` content.
Comparison is exact for region text; token equivalence is used to distinguish
format-only changes from changed values or commands. Decimal comma/dot pairs
with the same numeric value are classified as format differences, not value
changes.

The parser is not a TeX engine or symbolic algebra system. It recognizes a
limited set of syntax-level equivalences, including explicit fraction
commands versus slash notation and listed unit-command aliases; it does not
prove arbitrary algebraic equivalence or convert between different units.
New or domain-specific plain-text units may require extending the unit
recognizer. Equal notation does not prove that the translated sentence is
correct; a region pairing can also be misleading if the source and target
reorder content. Such cases are not auto-paired where the tool detects order,
boundary or syntax differences.

## Review sheet and application

The findings CSV contains one row per proposed technical-region replacement,
localized label, or manual case. It includes the German, current and proposed
fragments, target payload offsets, canonical-relative paths, source and
target hashes, priority and explanation. Treat it as read-only. Record
decisions in the separate, formula-free decisions CSV, keyed by stable case
ID. The only executable decision is `apply`, and only proposal rows can be
applied. `keep` decisions for localized labels are recorded but never write
canonical files. Deterministic format-equivalent proposals must be `apply`;
the apply tool rejects blank, `keep` or `manual` decisions for them. Manual
cases remain in the report and must be resolved separately. The
critical-review CSV filters one-to-one proposals where a value, symbol or TeX
token differs. It includes the token sequences and nearby source/translation
context so a human can decide whether each difference is an error, legitimate
localized notation, or an intentional conversion.

First validate approved rows without changing files:

```bash
pushd /home/jjcarron/proj/50-Ohms/ham-translator >/dev/null
pushd 50ohm-generator-next >/dev/null
uv run --locked python tools/apply_canonical_technical_format_review.py \
  --manifest ../tmp/canonical-technical-format-validation.json \
  --decisions-csv ../tmp/canonical-technical-format-decisions.csv
popd >/dev/null
popd >/dev/null
```

When the dry-run manifest and proposed changes are accepted, apply them:

```bash
pushd /home/jjcarron/proj/50-Ohms/ham-translator >/dev/null
pushd 50ohm-generator-next >/dev/null
uv run --locked python tools/apply_canonical_technical_format_review.py \
  --manifest ../tmp/canonical-technical-format-validation.json \
  --decisions-csv ../tmp/canonical-technical-format-decisions.csv \
  --apply \
  --applied-manifest ../tmp/canonical-technical-format-applied.json
popd >/dev/null
popd >/dev/null
```

The apply step refuses path traversal, unknown decisions, manual cases marked
`apply`, stale source or target hashes, changed text at a recorded offset, and
overlapping edits. The applied manifest records the exact decision file,
input-manifest hash, each operation and before/after file hashes. Use a
tracked review location for the approved decisions and applied manifest when
committing canonical changes; `tmp/` is only for the working review run.

## Source-backed markup repair (`--markup-only`)

Use `--markup-only` to select corrections of the mathematical representation
without accepting positional value-change proposals. The complete diagnostic
inventory remains in the report. This option is suitable for cleaning translated
DARCdown before testing MDX/Astro.

The planner matches equivalent expressions by their payload, not their ordinal
position among different quantities. It can:

- restore missing `$` delimiters around raw TeX expressions present in German;
- replace translated HTML math spans or `\(...\)` with the German delimiters;
- close a translated formula whose missing delimiter accidentally includes prose;
- restore an isolated Greek macro whose backslash was lost inside math;
- remove target-only math around a plain German measurement, matching equal
  value/unit occurrences, while translating an ordinary unit word when necessary.

A plain `360°` in German therefore remains plain `360°` in the translation.
A German `$\qty{8}{\volt}$` requires the same math representation in the target.
The planner never invents an algebraic conversion or a new quantity. Extra
ambiguous occurrences and expressions with no proven source counterpart remain
for review. Translated descriptive labels are retained. Numeric subscripts and
single-letter physical indices cannot be assumed to be translated words.

Each planned operation checks that the ordered numeric values are unchanged.
Reordered values with equivalent unit macros are detected as an order difference;
the planner may repair `\m` to `\meter` without exchanging 315 and 630 to match
the order of a differently worded German sentence.

Markup proposals contain the complete current and corrected target field and a
`markup_operations` list with the exact intermediate spans and German reference
regions. The apply tool verifies source/target hashes and **replays the planner**;
it refuses a proposal whose corrected field or operation history cannot be
reproduced. This also prevents a changed numeric proposal from being presented as
a markup-only repair. Separately reviewed semantic corrections remain explicitly
critical, and need their own decisions.

Always choose fresh output paths so reviewed decisions are not overwritten:

```bash
pushd /home/jjcarron/proj/50-Ohms/ham-translator >/dev/null
format_run_dir="$PWD/tmp/technical-markup-$(date +%Y%m%d-%H%M%S)"
pushd 50ohm-generator-next >/dev/null
uv run --locked python tools/validate_canonical_technical_format.py --markup-only \
  --manifest "$format_run_dir/plan.json" \
  --review-csv "$format_run_dir/review.csv" \
  --critical-csv "$format_run_dir/critical.csv" \
  --decisions-csv "$format_run_dir/decisions.csv" \
  --review-md "$format_run_dir/review.md"
# Exit 1 means findings were recorded. Inspect the plan and decisions.
uv run --locked python tools/apply_canonical_technical_format_review.py \
  --manifest "$format_run_dir/plan.json" \
  --decisions-csv "$format_run_dir/decisions.csv" \
  --applied-manifest "$format_run_dir/dry-run.json"
popd >/dev/null
popd >/dev/null
```

For an accepted apply, archive the exact plan and decisions in a new directory
under `50ohm-contents-ch/review/technical_format/`, rerun the dry run with those
archived inputs, then use the same command with `--apply` and an applied manifest
in that directory. Keep the records with the canonical corrections in Git.
The 17 October record also identifies the separate, explicitly reviewed dipole
regression correction. A successful markup repair or Astro build is not a claim
that every remaining diagnostic finding is a confirmed error or already resolved.
