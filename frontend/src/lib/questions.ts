import { getEntry, type CollectionEntry } from "astro:content";

/**
 * The questions of the BNetzA pool, as `_data/questions.json` carries them.
 *
 * Everything that reads a question goes through here, so the data format and the escaping of
 * its text stay in one place.
 */

export type QuestionData = CollectionEntry<"questions">["data"];

export async function getQuestion(number: string): Promise<QuestionData | undefined> {
  return (await getEntry("questions", number))?.data;
}

/**
 * Whether there is a solution page to link to.
 *
 * TODO: the solution pages are not ported yet, so there is none. Once they are, this becomes a
 * lookup in their collection, so a button can never point to a page that was not built.
 */
// eslint-disable-next-line @typescript-eslint/no-unused-vars -- used once the solution pages exist
export function hasSolution(number: string): boolean {
  return false;
}

/**
 * The source text of a question or answer as HTML.
 *
 * The text is plain text with two exceptions: `$…$` is left alone for KaTeX, which reads the
 * text content in the browser, and `<u>` is the only markup the pool uses. Everything else is
 * escaped, so `(< 1 Ohm` or `$d > \frac…$` cannot turn into broken tags.
 */
export function questionHtml(text: string): string {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll("&lt;u&gt;", "<u>")
    .replaceAll("&lt;/u&gt;", "</u>");
}
