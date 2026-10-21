# Country specialization with the `next` generator

## Purpose

The Swiss Astro preview demonstrates that the `next` generator can produce a
specialized multilingual site from the Swiss canonical content and question
pool without replacing the generator's overall build pipeline. The next step
is to make the boundary explicit: keep rendering and build behavior in a shared
core, put country choices in a profile, and isolate source-specific conversion
in an input adapter.

This document describes the current proof of feasibility and a proposed
architecture. The profile schema and interfaces below are design proposals;
they have not been implemented as a generic country system.

## What the Swiss prototype demonstrates

The local preview currently builds German, French, and Italian routes from
Swiss canonical data. Each language has the `NE`, `A`, and `NEA` course
editions. A verified run emitted 832 pages per language from 1,665 questions,
including localized search pages and indexes. The language selector preserves
the current route when changing locale.

The output also demonstrates country-specific presentation: USKA and Swiss
50ohm branding, the Swiss red palette, localized page-shell labels, the beta
notice and release identifier, and Swiss static pages. The preview is produced
locally by one wrapper and is not itself a deployment workflow.

These results show that a specialized site can be brought up by adapting the
input and presentation layers around the generator. They do not yet prove that
another country's sources can be connected by configuration alone. Swiss
source preparation, page selection, and some frontend components are currently
explicitly Swiss-specific.

## The separation to aim for

| Layer | Responsibility | Swiss example | Intended owner |
| --- | --- | --- | --- |
| Shared generator core | Parse normalized input, render pages/questions, build routes, search indexes, and assets | MDX rendering, Astro page templates, locale-aware URLs | Upstream generator |
| Site profile | Select locales, labels, editions, theme tokens, logos, and optional features | `de/fr/it`, `NE/A/NEA`, Swiss labels, red theme, USKA assets | Country/site configuration |
| Source adapter | Convert a country's canonical files and metadata into the generator's stable input contract | `prepare_ch_input.py`, canonical directory mapping, question metadata preparation | Country integration package or adapter |
| Source data and assets | Actual localized course, questions, images, and static pages | Swiss canonical repositories and extracted resources | Country canonical repositories |
| Content QA | Check translations and technical consistency before generation | Technical-format validation tools | Country workflow; reusable checks can later move to shared tooling |

The boundary should not force every difference into configuration. Values and
simple choices belong in a profile; transformations that understand a source
format belong in an adapter. The core should receive normalized data and should
not know that a field came from a Swiss JSON filename or a DARC-specific
directory layout.

## What belongs in configuration

Configuration is appropriate when a country can select or supply a value
without changing the meaning of the build algorithm:

- supported locales and the default locale;
- translated UI messages and language names;
- edition identifiers and their section/chapter selection rules;
- site title, logo, favicon, footer attribution, and feedback URL;
- semantic theme tokens such as primary, link, hover, and alert colors;
- feature switches such as answer shuffling, beta notice, feedback controls,
  or optional navigation items;
- whether localized routes are prefixed and the public base path.

The existing `frontend/i18n.config.json` already supplies the locale list and
many UI strings. However, its messages and the Swiss build settings are still
mixed with code that knows the Swiss input directory and branding. The current
`style-fiftyohm.css` also contains presentation choices that should eventually
be expressed through a documented theme-token contract.

An illustrative profile could look like this:

```yaml
profile: ch
locales:
  default: de
  enabled: [de, fr, it]
site:
  title: "50ohm.ch"
  logo: "assets/images/50ohm_ch.svg"
  favicon: "assets/favicon/icon-ch.svg"
  theme:
    primary: "#ac2d24"
    primaryHover: "#80221c"
features:
  answerShuffle: false
  betaNotice: true
  feedback: true
editions:
  - id: NE
    sections: [N, E]
  - id: A
    sections: [A]
  - id: NEA
    sections: [N, E, A]
input:
  adapter: ch-canonical
  root: "..."
```

This is an example of the intended division, not a committed configuration
format or a promise that every field can be implemented without adapter work.
In particular, edition selection must be validated against the generator's
current table-of-contents model before it becomes a stable public interface.

## What should remain an adapter

The Swiss preparation step currently knows how to locate canonical content,
load Swiss question catalogues, combine current questions with supplemental
presentation metadata, and prepare extracted static resources. Those are
source-contract concerns. Another country may use different filenames,
metadata, pruning rules, or question identifiers even when the resulting site
looks similar.

The core should define a small normalized input contract—for example, a
localized page tree, a question collection with stable IDs and presentation
metadata, an edition/TOC model, and an asset map. Each adapter should produce
that contract and a provenance manifest containing source revisions and input
hashes. The Astro renderer and search index should consume only this normalized
contract.

This keeps country-specific fallback and compatibility logic out of shared
templates. It also makes adapter errors testable before the website build.

## Portable changes suggested by this prototype

The branch currently contains 76 changed paths relative to its upstream base,
including documentation, content-quality tooling, Swiss assets, tests, and
generator changes. That total is not a useful estimate of the code required
for portability: it combines several independent workstreams. The reusable
generator work should be identified and reviewed as a narrower set:

1. **Profile loading:** define a validated profile schema and load it once at
   build time, with explicit defaults and errors for unsupported settings.
2. **Locale-driven routes:** derive route generation, language links, and
   localized messages from the configured locale list rather than a fixed
   `de/fr/it` set.
3. **Theme and brand interface:** make shared components consume semantic
   labels, logo/icon paths, and CSS variables; move Swiss values and assets
   into the Swiss profile.
4. **Edition model:** make edition definitions data-driven where the current
   TOC semantics permit it. Keep country-specific TOC interpretation in the
   adapter when it cannot be represented by the shared model.
5. **Feature configuration:** expose behavior switches such as answer
   shuffling and optional release UI through documented build options or
   profile values, rather than country-specific conditionals.
6. **Input adapter contract:** define the normalized input and provenance
   manifest so a second country can implement an adapter without editing
   renderer components.
7. **Build interface:** provide one generic build command accepting a profile
   and output location. Country wrappers may remain thin conveniences that
   select the profile and adapter.

The MDX rendering support is a separate candidate for upstream reuse: it is
generic if it accepts the generator's normal content model and does not embed
Swiss paths or policy. Translation/technical-format audits are also separate
from site portability; they should not be counted as required changes to make
the website generator country-aware.

## A practical path to maximize the shared core

The existing Swiss preview should remain the first profile and the regression
fixture. Extract the profile and adapter boundaries around its working output,
then prove the separation by rebuilding Switzerland with no Swiss branches in
shared page components. Add a second small fixture profile with different
branding, locale count, and edition definitions. It need not contain a full
course; it must prove that those choices do not require edits to shared core
files.

For each proposed core change, the acceptance test should be concrete:

- changing a logo or color changes only profile/theme files;
- changing enabled locales creates or removes the corresponding localized
  routes without editing route components;
- changing edition definitions changes generated course routes through the
  profile/adapter contract;
- changing source layout requires adapter changes, not renderer changes;
- the Swiss build retains its current route counts, search behavior, and
  question rendering.

That gives the community a useful demonstration early, while keeping the
generic architecture small and evidence-driven. It avoids attempting a
country-agnostic platform redesign before a second integration has shown which
interfaces are truly common.

## Current constraints to keep visible

The preview still lacks slides, solution pages, and the exam simulator. Some
Swiss pages and source resources retain DARC-specific references. The current
Swiss course also has 145 references to question IDs missing from the active
pool, shown as placeholders. These are content or feature-completeness issues,
not evidence that profile extraction alone will solve them. The current build
and these limits are documented in [`CH_NEXT_PREVIEW.md`](CH_NEXT_PREVIEW.md);
the implemented Swiss layer is summarized in
[`CH_SWISS_ADAPTATIONS.md`](CH_SWISS_ADAPTATIONS.md).
