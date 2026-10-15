# ohm-frontend

Das Astro-Frontend für [50ohm.de](https://50ohm.de). Es rendert die MDX-Ausgabe des
Python-Generators aus `packages/ohm-builder`.

## Ablauf

Der Generator schreibt die Editionen als MDX in ein Build-Verzeichnis, das Frontend liest es:

```sh
# 1. Inhalte übersetzen (aus dem Repo-Root, Content-Repo daneben)
uv run ohm -f mdx -i ../50ohm-contents-dl -o ./build

# 2. Frontend bauen
npm install
npm run build
```

Die Content-Collections in [src/content.config.ts](src/content.config.ts) zeigen auf `../build`.
Ohne einen vorherigen Generator-Lauf sind sie leer.

```
build/
├── <EDITION>/index.mdx                 → Collection `editions`
├── <EDITION>/<kapitel>/index.mdx       → Collection `chapters`
├── <EDITION>/<kapitel>/<abschnitt>.mdx → Collection `sections`
├── includes/<ident>.html               → Collection `includes`
├── _data/questions.json                → Collection `questions`
├── _data/index.json  _data/question_index.json  pictures/  photos/
└──   ↳ kopiert nach public/ von integrations/copy-course-assets.mjs
```

## Struktur

| Pfad | Inhalt |
| --- | --- |
| `src/layouts/` | `BaseLayout` (Dokument, Assets, Navigation) und `PageLayout` (Inhaltsspalte, Sidebar, Footer) |
| `src/components/` | `SiteHeader`, `SiteFooter`, `Question` |
| `src/components/mdx/` | die Komponenten, die der MDX-Renderer aufruft; `components.ts` ist die Zuordnung |
| `src/lib/` | URL-Aufbau, Kursnavigation, Fragendaten, Ports von `index_anchor_id` und der Morse-Tabelle |
| `src/scripts/` | Client-Skripte: Randboxen, Mischen und Auswerten der Antworten |
| `src/pages/[edition]/…` | Editions-, Kapitel- und Abschnittsseiten |
| `src/pages/[legacy].html.astro` | Weiterleitungen von den flachen Dateinamen des HTML-Builds |
| `public/assets/` | Kopie von `ohm_builder/assets` (wird später zu npm-Packages aufgeräumt); die Antwortlogik ist aus `script.js` nach `src/scripts/questions.ts` gewandert |

## Entwicklung

```sh
astro dev --background     # astro dev stop | status | logs
```

Nicht portiert: Folien, Lösungsseiten, und die Snippets der Startseite. Solange es keine
Lösungsseiten gibt, zeigt `Question` keinen Button „Lösungsweg anzeigen“ (`hasSolution()` in
`src/lib/questions.ts`).

Vollständige Astro-Dokumentation: https://docs.astro.build
