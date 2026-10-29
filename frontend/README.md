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
| `src/site/` | Komponenten für beliebige Seiten: `Head`, `BaseLayout` (Dokument), `PageLayout` (Inhaltsspalte, Sidebar, Footer), `SiteHeader`, `SiteFooter`, `Breadcrumbs`, außerdem `OhmPage` als Einstieg für eigene Seiten |
| `src/course/` | Komponenten für Kursseiten: `CourseToolbar`, `CourseContent`, `TableOfContents`, `NextLink`, `QuestionSearch` |
| `src/page-components/` | Fertige Kursseiten: `EditionPage`, `ChapterPage`, `SectionPage` |
| `src/mdx-components/` | die Komponenten, die der MDX-Renderer aufruft, darunter `Question` |
| `src/lib/` | Helferfunktionen für Seitendaten (`route-data.ts`), URL-Aufbau, Kursnavigation, Fragendaten, Ports von `index_anchor_id` und der Morse-Tabelle |
| `src/locals.ts` | Middleware, die die Seitendaten in `Astro.locals` vorbereitet |
| `src/scripts/` | Übernommene clientseitige Skripte: Marginalien, Mischen von Antwortoptionen, Quizmodus, KaTeX-Rendering mit den Makros für Einheiten |
| `src/styles/` | Die Stylesheets der Seite und des Kurses samt Fonts. |
| `src/pages/[edition]/…`, `src/pages/suche.astro` | Die am Ende gerenderten Routen |
| `src/pages/[legacy].html.astro` | Weiterleitungen von den flachen Dateinamen des HTML-Builds |
| `public/assets/` | Rest der Kopie von `ohm_builder/assets`, primär Inhalte für Applets und ein paar Assets. Wird noch weiter aufgeräumt. |

### Virtuelle Module

Das Projekt verwendet virtuelle Module, um eine einfache Konfigurierbarkeit und Überschreibbarkeit der Templates zu gewährleisten.
Es gibt folgende Namespaces:

- `virtual:ohm/site/<Name>`: Komponenten für beliebige Seiten der Website.
- `virtual:ohm/course/<Name>`: Komponenten für Kursseiten.
- `virtual:ohm/page-components/<Name>`: Fertig zusammengestellte Kursseiten.
- `virtual:ohm/mdx-components/<Name>`: Komponenten, die im MDX aufgerufen werden und zwingend verfügbar sein müssen.
- `virtual:ohm/mdx-components`: Eine Map, um beim Rendern von MDX alle MDX-Komponenten einfacher übergeben zu können.

### Seitendaten

Die Komponenten bekommen ihre Daten nicht als Props, sondern lesen sie aus `Astro.locals`. So kommt jedes Override an alle Daten der Seite:

- `Astro.locals.ohmRoute` gibt es auf jeder Seite: `title` und `breadcrumbs`.
- `Astro.locals.ohmCourse` gibt es innerhalb von Kursseiten (Editionsübersicht, Kapitelübersicht, Abschnitt): Sie enthalten konkrete Daten zum Rendern eines Kurses.

Eine eigene Seite sollte in `OhmPage` gewrapped werden, diese nimmt Attribute über Props entgegen und schreibt diese in `Astro.locals.ohmRoute`:

```astro
<OhmPage title="Ausbildungspaten" parents={[{ label: "Lernen", url: LEARN_URL }]}>
  <Breadcrumbs /> <!-- Optional -->
  …
</OhmPage>
```

## Entwicklung

```sh
astro dev --background     # astro dev stop | status | logs
```

Vollständige Astro-Dokumentation: https://docs.astro.build
