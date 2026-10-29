import {
  getChapters,
  getEdition,
  getNextChapter,
  getNextSection,
  getSections,
  type ChapterEntry,
  type EditionEntry,
  type SectionEntry,
} from "./course";
import { HOME_URL, chapterUrl, editionUrl, sectionUrl } from "./urls";

export interface Link {
  label: string;
  url: string;
}

/** The trail to the current page, the last entry is the current page itself. */
export type Breadcrumbs = [] | [...Link[], Omit<Link, "url"> & { url?: never }];

/** What every page has, in `Astro.locals.ohmRoute`. */
export interface OhmRoute {
  /** Pages without a title show just the default title. */
  title?: string;
  breadcrumbs: Breadcrumbs;
}

export interface TocItem {
  label: string;
  /** Displayed in front of the label, e.g. "3.2". */
  number: string;
  url: string;
}

export interface Toolbar {
  videoUrl?: string;
  slideUrl: string;
}

export interface NextLink extends Link {
  kind: "section" | "chapter";
}

export interface Edition {
  kind: "edition";
  edition: EditionEntry;
  toc: TocItem[];
}

export interface Chapter {
  kind: "chapter";
  edition: EditionEntry;
  chapter: ChapterEntry;
  toc: TocItem[];
  toolbar: Toolbar;
  next?: NextLink;
}

export interface Section {
  kind: "section";
  edition: EditionEntry;
  chapter: ChapterEntry;
  section: SectionEntry;
  toolbar: Toolbar;
  next?: NextLink;
}

/** A single course page, either edition / chapter index or a section. */
export type CoursePage = Edition | Chapter | Section;

export interface RouteData {
  route: OhmRoute;
  course?: CoursePage;
}

const HOME: Link = { label: "Home", url: HOME_URL };

export function pageRouteData({
  title,
  parents = [],
}: {
  title: string;
  parents?: Link[];
}): RouteData {
  return {
    route: { title, breadcrumbs: [HOME, ...parents, { label: title }] },
  };
}

export async function editionRouteData(
  edition: EditionEntry,
): Promise<RouteData> {
  const { edition: shortName, title } = edition.data;
  const chapters = await getChapters(shortName);

  return {
    route: { title, breadcrumbs: [HOME, { label: title }] },
    course: {
      kind: "edition",
      edition,
      toc: chapters.map((chapter) => ({
        url: chapterUrl(shortName, chapter.data.ident),
        number: String(chapter.data.chapterNumber),
        label: chapter.data.title,
      })),
    },
  };
}

export async function chapterRouteData(
  chapter: ChapterEntry,
): Promise<RouteData> {
  const {
    edition: shortName,
    ident,
    chapterNumber,
    title,
    videoUrl,
  } = chapter.data;
  const edition = await requireEdition(shortName);
  const sections = await getSections(shortName, ident);
  const next = await getNextChapter(chapter);

  return {
    route: {
      title,
      breadcrumbs: [
        HOME,
        { label: edition.data.title, url: editionUrl(shortName) },
        { label: title },
      ],
    },
    course: {
      kind: "chapter",
      edition,
      chapter,
      toc: sections.map((section) => ({
        url: sectionUrl(shortName, ident, section.data.ident),
        number: `${chapterNumber.toFixed(0)}.${section.data.sectionNumber.toFixed(0)}`, // TODO: Use strings
        label: section.data.title,
      })),
      // TODO: Once slides are built in astro, this link should come from a different source.
      toolbar: { videoUrl, slideUrl: `/${shortName}_slide_${ident}.html` },
      next:
        next ?
          {
            kind: "chapter",
            url: chapterUrl(shortName, next.data.ident),
            label: next.data.title,
          }
        : undefined,
    },
  };
}

export async function sectionRouteData(
  section: SectionEntry,
): Promise<RouteData> {
  const {
    edition: shortName,
    chapterIdent,
    sectionNumber,
    title,
    videoUrl,
  } = section.data;
  const edition = await requireEdition(shortName);
  const chapter = await requireChapter(shortName, chapterIdent);
  const nextSection = await getNextSection(section);
  const nextChapter = nextSection ? null : await getNextChapter(chapter);

  return {
    route: {
      title,
      breadcrumbs: [
        HOME,
        { label: edition.data.title, url: editionUrl(shortName) },
        { label: chapter.data.title, url: chapterUrl(shortName, chapterIdent) },
        { label: title },
      ],
    },
    course: {
      kind: "section",
      edition,
      chapter,
      section,
      // TODO: Get url from astro once slides are built here.
      toolbar: {
        videoUrl,
        slideUrl: `/${shortName}_slide_${chapterIdent}.html#${String(sectionNumber)}`,
      },
      next:
        nextSection ?
          {
            kind: "section",
            url: sectionUrl(shortName, chapterIdent, nextSection.data.ident),
            label: nextSection.data.title,
          }
        : nextChapter ?
          {
            kind: "chapter",
            url: chapterUrl(shortName, nextChapter.data.ident),
            label: nextChapter.data.title,
          }
        : undefined,
    },
  };
}

async function requireEdition(edition: string): Promise<EditionEntry> {
  const entry = await getEdition(edition);
  if (!entry) {
    throw new Error(`Edition ${edition} has no index.mdx in the course build.`);
  }
  return entry;
}

async function requireChapter(
  edition: string,
  chapterIdent: string,
): Promise<ChapterEntry> {
  const chapters = await getChapters(edition);
  const chapter = chapters.find(
    (candidate) => candidate.data.ident === chapterIdent,
  );
  if (!chapter) {
    throw new Error(
      `Chapter ${chapterIdent} of edition ${edition} has no index.mdx in the course build.`,
    );
  }
  return chapter;
}
