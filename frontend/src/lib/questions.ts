import { getEntry, type CollectionEntry } from "astro:content";

/**
 * The questions of the BNetzA pool, as `_data/questions.json` carries them.
 *
 * Everything that reads a question goes through here, so the data format and the escaping of
 * its text stay in one place.
 */

export type QuestionData = CollectionEntry<"questions">["data"];

export async function getQuestion(locale: string, number: string): Promise<QuestionData | undefined> {
  return (await getEntry("questions", `${locale}/${number}`))?.data;
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
  const escaped = text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll("&lt;u&gt;", "<u>")
    .replaceAll("&lt;/u&gt;", "</u>");

  // The pool sometimes stores standalone siunitx quantities without the `$…$` delimiters
  // that the legacy HTML template added around answer formulas. Handle simple angle values as
  // ordinary answer text; other quantities are delimited so KaTeX's auto-render can process them.
  const trimmed = escaped.trim();
  const quantity = parseStandaloneQuantity(trimmed);
  if (quantity?.unit === "\\degree") {
    const leading = escaped.slice(0, escaped.indexOf(trimmed));
    const trailing = escaped.slice(escaped.indexOf(trimmed) + trimmed.length);
    // A bare angle is an answer label/value, not a displayed equation. Keep it in the
    // answer's Roboto font, as with the surrounding text, instead of KaTeX's math face.
    return `${leading}${quantity.value}°${trailing}`;
  }
  if (quantity) {
    const leading = escaped.slice(0, escaped.indexOf(trimmed));
    const trailing = escaped.slice(escaped.indexOf(trimmed) + trimmed.length);
    return `${leading}$${trimmed}$${trailing}`;
  }
  return escaped;
}

function parseStandaloneQuantity(text: string): { value: string; unit: string } | undefined {
  if (!text.startsWith("\\qty{") || text.includes("$")) return undefined;

  let position = 4; // after `\qty`
  const arguments_: string[] = [];
  for (let argument = 0; argument < 2; argument += 1) {
    if (text[position] !== "{") return undefined;
    const start = position + 1;
    let depth = 0;
    do {
      if (text[position] === "{") depth += 1;
      else if (text[position] === "}") depth -= 1;
      position += 1;
    } while (position < text.length && depth > 0);
    if (depth !== 0) return undefined;
    arguments_.push(text.slice(start, position - 1));
  }
  return position === text.length ? { value: arguments_[0], unit: arguments_[1] } : undefined;
}
