import Question from "../Question.astro";

import Anchor from "./Anchor.astro";
import Include from "./Include.astro";
import Index from "./Index.astro";
import Morse from "./Morse.astro";
import Qso from "./Qso.astro";
import QsoLine from "./QsoLine.astro";
import Reference from "./Reference.astro";
import Tag from "./Tag.astro";

/**
 * The components `FiftyOhmMdxRenderer` emits, passed to `<Content components={…} />`.
 *
 * The generated MDX imports nothing, so this map is the whole contract. Everything else the
 * renderer produces — `<figure>`, `<figcaption>`, `<u>`, GFM tables, `![…](/pictures/…)` and
 * `$$ … $$` — is plain HTML or Markdown and needs no component.
 */
export const mdxComponents = {
  Anchor,
  Include,
  Index,
  Morse,
  Qso,
  QsoLine,
  Question,
  Reference,
  Tag,
};
