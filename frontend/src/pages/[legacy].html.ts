import type { APIRoute, GetStaticPaths } from "astro";
import { getCollection } from "astro:content";

import {
  LEGACY_PAGES,
  chapterUrl,
  editionUrl,
  legacyChapter,
  legacyEditionIndex,
  legacySection,
  sectionUrl,
} from "../lib/urls";

/**
 * Redirects from the flat file names the HTML build produced to the nested URLs.
 *
 * An endpoint rather than a page: with `build.format: "directory"` a page route would write
 * `N_rufzeichen.html/index.html`, while an endpoint writes the route path verbatim.
 *
 * Not Astro's `redirects` option, and not a bare meta refresh either: the search page links with
 * a fragment (`…#index_rufzeichen`), and a meta refresh to a fixed URL drops it. The inline
 * script carries `location.hash` over; the meta refresh and the canonical link are the fallback
 * for clients without JavaScript.
 */
export const getStaticPaths: GetStaticPaths = async () => {
  const [editions, chapters, sections] = await Promise.all([
    getCollection("editions"),
    getCollection("chapters"),
    getCollection("sections"),
  ]);

  // No redirects for `<ED>_slide_*.html` or `<Fragennummer>.html`: neither the slide decks nor
  // the solution pages are ported yet, so there is nothing to point at.
  const routes = [
    ...Object.entries(LEGACY_PAGES).map(([legacy, target]) => ({ legacy, target })),
    ...editions.map(({ data }) => ({
      legacy: legacyEditionIndex(data.edition),
      target: editionUrl(data.edition),
    })),
    ...chapters.map(({ data }) => ({
      legacy: legacyChapter(data.edition, data.ident),
      target: chapterUrl(data.edition, data.ident),
    })),
    ...sections.map(({ data }) => ({
      legacy: legacySection(data.edition, data.ident),
      target: sectionUrl(data.edition, data.chapterIdent, data.ident),
    })),
  ];

  // Astro rejects duplicate params, and nothing rules out a section ident that collides with
  // another edition's legacy name.
  const seen = new Set<string>();

  return routes.flatMap(({ legacy, target }) => {
    // The route already ends in `.html`, so the parameter must not.
    const param = legacy.replace(/\.html$/, "");
    if (seen.has(param)) return [];
    seen.add(param);
    return [{ params: { legacy: param }, props: { target } }];
  });
};

export const GET: APIRoute = ({ props }) => {
  const target = props.target as string;
  const escaped = target.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");

  const body = `<!doctype html>
<html lang="de">
  <head>
    <meta charset="utf-8">
    <title>Weitergeleitet</title>
    <link rel="canonical" href="${escaped}">
    <meta http-equiv="refresh" content="0; url=${escaped}">
    <meta name="robots" content="noindex">
    <script>location.replace(${JSON.stringify(target)} + location.hash);</script>
  </head>
  <body>
    <p>Diese Seite ist umgezogen: <a href="${escaped}">${escaped}</a></p>
  </body>
</html>
`;

  return new Response(body, { headers: { "Content-Type": "text/html; charset=utf-8" } });
};
