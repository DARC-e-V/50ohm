import { readFile, readdir } from "node:fs/promises";
import { fileURLToPath, pathToFileURL } from "node:url";
import { basename, join, resolve } from "node:path";

import { defineCollection, z } from "astro:content";
import { file, glob, type Loader, type LoaderContext } from "astro/loaders";

import { EDITIONS } from "./lib/editions";

/**
 * The output of `ohm -f mdx -o ./build`, one level above the frontend.
 *
 * The builder writes
 *   <EDITION>/index.mdx                        -> editions
 *   <EDITION>/<chapter>/index.mdx              -> chapters
 *   <EDITION>/<chapter>/<section>.mdx          -> sections
 *   includes/<ident>.html                      -> includes
 *   _data/questions.json                       -> questions
 *   pictures/, photos/, _data/*index.json      -> copied to public/ by the integration
 */
const COURSE_DIR = process.env.OHM_BUILD_DIR
  ? pathToFileURL(`${resolve(process.env.OHM_BUILD_DIR)}/`)
  : new URL("../../build/", import.meta.url);

// The build directory also holds the HTML build, so the patterns are scoped to the known
// editions instead of matching any directory that happens to sit there.
const editionGroup = `{${EDITIONS.join(",")}}`;

// The default would slugify the ids, which lowercases the edition and drops the `index`
// segment. The paths are already the identifiers we want, so keep them verbatim.
const pathAsId = ({ entry }: { entry: string }) => entry.replace(/\.mdx$/, "");

const editions = defineCollection({
  loader: glob({ base: COURSE_DIR, pattern: `${editionGroup}/index.mdx`, generateId: pathAsId }),
  schema: z.object({
    title: z.string(),
    edition: z.string(),
  }),
});

const chapters = defineCollection({
  loader: glob({ base: COURSE_DIR, pattern: `${editionGroup}/*/index.mdx`, generateId: pathAsId }),
  schema: z.object({
    title: z.string(),
    ident: z.string(),
    edition: z.string(),
    chapterNumber: z.number(),
    videoUrl: z.string().optional(),
  }),
});

const sections = defineCollection({
  loader: glob({
    base: COURSE_DIR,
    pattern: [`${editionGroup}/*/*.mdx`, `!${editionGroup}/*/index.mdx`],
    generateId: pathAsId,
  }),
  schema: z.object({
    title: z.string(),
    ident: z.string(),
    edition: z.string(),
    chapterIdent: z.string(),
    chapterNumber: z.number(),
    sectionNumber: z.number(),
    videoUrl: z.string().optional(),
    status: z.string().optional(),
    // The builder emits this key literally; `data.class` is a valid property access.
    class: z.string().optional(),
  }),
});

/**
 * Raw HTML includes (applets), read with `node:fs`.
 *
 * A `?raw` import would work too, but `../../build` sits outside the Vite root, and a loader
 * avoids having to open that up.
 */
function includesLoader(dir: URL): Loader {
  const path = fileURLToPath(dir);

  return {
    name: "includes-loader",
    load: async ({ store, parseData, generateDigest, logger, watcher }: LoaderContext) => {
      store.clear();

      let names: string[];
      try {
        names = (await readdir(path)).filter((name: string) => name.endsWith(".html"));
      } catch {
        logger.warn(`No includes at ${path} — run \`ohm -f mdx -o ./build\` first.`);
        return;
      }

      for (const name of names) {
        const id = basename(name, ".html");
        const html = await readFile(join(path, name), "utf-8");
        store.set({
          id,
          data: await parseData({ id, data: { html } }),
          digest: generateDigest(html),
        });
      }

      watcher?.add(path);
    },
  };
}

const includes = defineCollection({
  loader: includesLoader(new URL("includes/", COURSE_DIR)),
  schema: z.object({
    html: z.string(),
  }),
});

/** A picture of the question pool, served from `/pictures/<id>.svg`. */
const questionPicture = z.object({
  id: z.string(),
  alt: z.string(),
});

/**
 * `_data/questions.json`, the whole question pool keyed by question number.
 *
 * `question` and the answer texts are source text as the BNetzA delivers it: `$…$` for KaTeX and
 * `<u>` for emphasis. Read them through `lib/questions.ts`, which escapes them for HTML.
 */
const questions = defineCollection({
  loader: file(fileURLToPath(new URL("_data/questions.json", COURSE_DIR))),
  schema: z.object({
    // Swiss questions use class 0; the builder omits this optional field for them.
    class: z.enum(["N", "E", "A"]).optional(),
    question: z.string(),
    picture: questionPicture.optional(),
    // Always four, in the order of the pool: the first one is the correct answer. An answer whose
    // picture is missing from the content repository ends up empty, the builder warns about it.
    answers: z
      .array(
        z.object({
          text: z.string().optional(),
          picture: questionPicture.optional(),
        }),
      )
      .length(4),
    // A code from the pool's metadata; style-course.css styles some of them as `.layout-<code>`.
    layout: z.string().optional(),
  }),
});

export const collections = { editions, chapters, sections, includes, questions };
