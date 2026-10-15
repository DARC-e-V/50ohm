/**
 * The site's URLs in one place, so pages, breadcrumbs, next-links and the legacy redirects
 * cannot drift apart.
 *
 * The HTML build used flat file names (`N_chapter_n_erste_schritte.html`); the Astro build
 * nests them. `legacy*` produces the old names, which `[legacy].html.astro` redirects from.
 */

export const editionUrl = (edition: string) => `/${edition}/`;

export const chapterUrl = (edition: string, chapterIdent: string) => `/${edition}/${chapterIdent}/`;

export const sectionUrl = (edition: string, chapterIdent: string, sectionIdent: string) =>
  `/${edition}/${chapterIdent}/${sectionIdent}/`;

/** The solution pages are not ported yet, but `question.html` links to them. */
export const solutionUrl = (number: string) => `/loesung/${number}/`;

/** A drawing, copied to public/pictures/ by the copy-course-assets integration. */
export const pictureUrl = (id: string) => `/pictures/${id}.svg`;

export const HOME_URL = "/";
export const LEARN_URL = "/#lernen";
export const SEARCH_URL = "/suche/";
export const INFO_URL = "/infos/";
export const EXAM_URL = "/pruefung/";
export const MENTORS_URL = "/patenkarte/";
export const COURSES_MAP_URL = "/kurse-vor-ort/karte/";
export const COURSES_LIST_URL = "/kurse-vor-ort/liste/";

export const legacyEditionIndex = (edition: string) => `${edition}_course_index.html`;

export const legacyChapter = (edition: string, chapterIdent: string) => `${edition}_chapter_${chapterIdent}.html`;

export const legacySection = (edition: string, sectionIdent: string) => `${edition}_${sectionIdent}.html`;

/**
 * The pages of the surrounding website, keyed by their old file name.
 *
 * No entry for `index.html`: in a static build that file *is* the home page, so a redirect
 * would collide with it.
 */
export const LEGACY_PAGES: Record<string, string> = {
  "infos.html": INFO_URL,
  "pruefung.html": EXAM_URL,
  "suche.html": SEARCH_URL,
  "patenkarte.html": MENTORS_URL,
  "kurse_vor_ort_karte.html": COURSES_MAP_URL,
  "kurse_vor_ort_liste.html": COURSES_LIST_URL,
};
