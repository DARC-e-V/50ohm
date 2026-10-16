import { getRelativeLocaleUrl } from "astro:i18n";
import type { Locale } from "./i18n";

export const homeUrl = (locale: Locale) => getRelativeLocaleUrl(locale, "");
export const editionUrl = (locale: Locale, edition: string) => getRelativeLocaleUrl(locale, edition);
export const chapterUrl = (locale: Locale, edition: string, chapterIdent: string) =>
  getRelativeLocaleUrl(locale, `${edition}/${chapterIdent}`);
export const sectionUrl = (locale: Locale, edition: string, chapterIdent: string, sectionIdent: string) =>
  getRelativeLocaleUrl(locale, `${edition}/${chapterIdent}/${sectionIdent}`);
export const solutionUrl = (locale: Locale, number: string) => getRelativeLocaleUrl(locale, `loesung/${number}`);
export const pictureUrl = (locale: Locale, id: string) => `/${locale}/pictures/${id}.svg`;
export const searchIndexUrl = (locale: Locale, name: string) => `/${locale}/assets/${name}`;

export const INFO_URL = (locale: Locale) => getRelativeLocaleUrl(locale, "infos");
export const LEARN_URL = (locale: Locale) => `${homeUrl(locale)}#lernen`;
export const SEARCH_URL = (locale: Locale) => getRelativeLocaleUrl(locale, "suche");
export const EXAM_URL = (locale: Locale) => getRelativeLocaleUrl(locale, "pruefung");
export const MENTORS_URL = (locale: Locale) => getRelativeLocaleUrl(locale, "patenkarte");
export const COURSES_MAP_URL = (locale: Locale) => getRelativeLocaleUrl(locale, "kurse-vor-ort/karte");
export const COURSES_LIST_URL = (locale: Locale) => getRelativeLocaleUrl(locale, "kurse-vor-ort/liste");

export const legacyEditionIndex = (edition: string) => `${edition}_course_index.html`;
export const legacyChapter = (edition: string, chapterIdent: string) => `${edition}_chapter_${chapterIdent}.html`;
export const legacySection = (edition: string, sectionIdent: string) => `${edition}_${sectionIdent}.html`;
export const LEGACY_PAGES: Record<string, string> = {
  "infos.html": "infos", "pruefung.html": "pruefung", "suche.html": "suche",
  "patenkarte.html": "patenkarte", "kurse_vor_ort_karte.html": "kurse-vor-ort/karte",
  "kurse_vor_ort_liste.html": "kurse-vor-ort/liste", "todo.html": "todo",
};
