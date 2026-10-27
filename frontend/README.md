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

Dieses Projekt erwartet in `build` folgende Dateistruktur, um daraus die Webseite zu erzeugen:

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
| `src/layouts/` | Seitenlayouts `BaseLayout` (Dokument, Assets, Navigation) und `PageLayout` (Inhaltsspalte, Sidebar, Footer) |
| `src/components/` | Einzelne Bestandteile der Seiten `SiteHeader`, `SiteFooter`, `NextChapter`, `NextSection` |
| `src/mdx-components/` | die Komponenten, die der MDX-Renderer aufruft, darunter `Question` |
| `src/lib/` | Helferfunktionen für URL-Aufbau, Kursnavigation, Fragendaten, Ports von `index_anchor_id` und der Morse-Tabelle |
| `src/scripts/` | Übernommene clientseitige Skripte: Marginalien, Mischen von Antwortoptionen |
| `src/pages/[edition]/…` | Editions-, Kapitel- und Abschnittsseiten |
| `src/pages/[legacy].html.astro` | Weiterleitungen von den flachen Dateinamen des HTML-Builds |
| `public/assets/` | Kopie von `ohm_builder/assets` (wird noch zu npm-Packages aufgeräumt) |

### Virtuelle Module

Das Projekt verwendet virtuelle Module, um eine einfache Konfigurierbarkeit und Überschreibbarkeit der Templates zu gewährleisten.
Es gibt folgende Namespaces:

- `virtual:ohm/layouts/`: Seitenlayouts
- `virtual:ohm/components/<Name>`: Sonstige Komponenten für Seiten
- `virtual:ohm/mdx-components/<Name>`: Komponenten, die im MDX aufgerufen werden und zwingend verfügbar sein müssen.
- `virtual:ohm/mdx-components`: Eine Map, um beim Rendern von MDX alle MDX-Komponenten einfacher übergeben zu können.

## Entwicklung

```sh
astro dev --background     # astro dev stop | status | logs
```

Vollständige Astro-Dokumentation: https://docs.astro.build
