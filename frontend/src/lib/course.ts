import { getCollection, getEntry, type CollectionEntry } from "astro:content";

/**
 * The navigation data the HTML builder had in `ChapterContext` / `SectionContext` but that the
 * MDX frontmatter does not carry: the edition title, the chapter's sections, and what comes next.
 * All of it is derived from `chapterNumber` / `sectionNumber`.
 */

export type EditionEntry = CollectionEntry<"editions">;
export type ChapterEntry = CollectionEntry<"chapters">;
export type SectionEntry = CollectionEntry<"sections">;

const byChapterNumber = (a: ChapterEntry, b: ChapterEntry) => a.data.chapterNumber - b.data.chapterNumber;
const bySectionNumber = (a: SectionEntry, b: SectionEntry) => a.data.sectionNumber - b.data.sectionNumber;

/** The edition overview, whose `title` is the `name` the breadcrumbs use. */
export const getEdition = (edition: string) => getEntry("editions", `${edition}/index`);

export async function getChapters(edition: string): Promise<ChapterEntry[]> {
  const chapters = await getCollection("chapters", ({ data }) => data.edition === edition);
  return chapters.sort(byChapterNumber);
}

export async function getSections(edition: string, chapterIdent: string): Promise<SectionEntry[]> {
  const sections = await getCollection(
    "sections",
    ({ data }) => data.edition === edition && data.chapterIdent === chapterIdent,
  );
  return sections.sort(bySectionNumber);
}

/** The chapter after this one, or null at the end of the edition. */
export async function getNextChapter(chapter: ChapterEntry): Promise<ChapterEntry | null> {
  const chapters = await getChapters(chapter.data.edition);
  const index = chapters.findIndex((candidate) => candidate.id === chapter.id);
  return chapters[index + 1] ?? null;
}

/** The section after this one, or null at the end of the chapter. */
export async function getNextSection(section: SectionEntry): Promise<SectionEntry | null> {
  const sections = await getSections(section.data.edition, section.data.chapterIdent);
  const index = sections.findIndex((candidate) => candidate.id === section.id);
  return sections[index + 1] ?? null;
}
