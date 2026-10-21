import { getCollection, getEntry, type CollectionEntry } from "astro:content";
import type { Locale } from "./i18n";

export type EditionEntry = CollectionEntry<"editions">;
export type ChapterEntry = CollectionEntry<"chapters">;
export type SectionEntry = CollectionEntry<"sections">;

const localeOf = (entry: { id: string }) => entry.id.split("/", 1)[0];
const byChapterNumber = (a: ChapterEntry, b: ChapterEntry) => a.data.chapterNumber - b.data.chapterNumber;
const bySectionNumber = (a: SectionEntry, b: SectionEntry) => a.data.sectionNumber - b.data.sectionNumber;

export const getLocale = localeOf;
export const getEdition = (locale: Locale, edition: string) => getEntry("editions", `${locale}/${edition}/index`);

export async function getChapters(locale: Locale, edition: string): Promise<ChapterEntry[]> {
  const entries = await getCollection("chapters", ({ id, data }) => localeOf({ id }) === locale && data.edition === edition);
  return entries.sort(byChapterNumber);
}

export async function getSections(locale: Locale, edition: string, chapterIdent: string): Promise<SectionEntry[]> {
  const entries = await getCollection("sections", ({ id, data }) =>
    localeOf({ id }) === locale && data.edition === edition && data.chapterIdent === chapterIdent,
  );
  return entries.sort(bySectionNumber);
}

export async function getNextChapter(chapter: ChapterEntry): Promise<ChapterEntry | null> {
  const locale = localeOf(chapter);
  const chapters = await getChapters(locale as Locale, chapter.data.edition);
  return chapters[chapters.findIndex((candidate) => candidate.id === chapter.id) + 1] ?? null;
}

export async function getNextSection(section: SectionEntry): Promise<SectionEntry | null> {
  const locale = localeOf(section);
  const sections = await getSections(locale as Locale, section.data.edition, section.data.chapterIdent);
  return sections[sections.findIndex((candidate) => candidate.id === section.id) + 1] ?? null;
}
