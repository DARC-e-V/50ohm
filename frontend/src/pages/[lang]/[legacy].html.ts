import type { APIRoute, GetStaticPaths } from "astro";
import { getCollection } from "astro:content";
import { getRelativeLocaleUrl } from "astro:i18n";

import { LEGACY_PAGES, chapterUrl, editionUrl, legacyChapter, legacyEditionIndex, legacySection, sectionUrl } from "../../lib/urls";
import { LOCALES, type Locale } from "../../lib/i18n";

export const getStaticPaths: GetStaticPaths = async () => {
  const [editions, chapters, sections] = await Promise.all([
    getCollection("editions"), getCollection("chapters"), getCollection("sections"),
  ]);
  const routes: { locale: Locale; legacy: string; target: string }[] = [];
  for (const locale of LOCALES) {
    for (const [legacy, path] of Object.entries(LEGACY_PAGES)) {
      routes.push({ locale, legacy, target: getRelativeLocaleUrl(locale, path) });
    }
    for (const entry of editions.filter(({ id }) => id.startsWith(`${locale}/`))) {
      routes.push({ locale, legacy: legacyEditionIndex(entry.data.edition), target: editionUrl(locale, entry.data.edition) });
    }
    for (const entry of chapters.filter(({ id }) => id.startsWith(`${locale}/`))) {
      routes.push({ locale, legacy: legacyChapter(entry.data.edition, entry.data.ident), target: chapterUrl(locale, entry.data.edition, entry.data.ident) });
    }
    for (const entry of sections.filter(({ id }) => id.startsWith(`${locale}/`))) {
      routes.push({ locale, legacy: legacySection(entry.data.edition, entry.data.ident), target: sectionUrl(locale, entry.data.edition, entry.data.chapterIdent, entry.data.ident) });
    }
  }

  const seen = new Set<string>();
  return routes.flatMap(({ locale, legacy, target }) => {
    const param = legacy.replace(/\.html$/, "");
    const key = `${locale}/${param}`;
    if (seen.has(key)) return [];
    seen.add(key);
    return [{ params: { lang: locale, legacy: param }, props: { target, locale } }];
  });
};

export const GET: APIRoute = ({ props }) => {
  const target = props.target as string;
  const locale = props.locale as Locale;
  const escaped = target.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
  const html = `<!doctype html><html lang="${locale}"><head><meta charset="utf-8"><title>Redirect</title><link rel="canonical" href="${escaped}"><meta http-equiv="refresh" content="0; url=${escaped}"><meta name="robots" content="noindex"><script>location.replace(${JSON.stringify(target)} + location.hash);</script></head><body><a href="${escaped}">${escaped}</a></body></html>`;
  return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
};
