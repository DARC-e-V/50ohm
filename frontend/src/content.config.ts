import { readFile, readdir } from "node:fs/promises";
import { fileURLToPath, pathToFileURL } from "node:url";
import { basename, join, resolve } from "node:path";

import { defineCollection, z } from "astro:content";
import { glob, type Loader, type LoaderContext } from "astro/loaders";

import { EDITIONS } from "./lib/editions";
import { LOCALES } from "./lib/i18n";

const BUILD_ROOT = process.env.OHM_BUILD_ROOT
  ? pathToFileURL(`${resolve(process.env.OHM_BUILD_ROOT)}/`)
  : new URL("../../build/", import.meta.url);
const editionGroup = `{${EDITIONS.join(",")}}`;
const localizedPatterns = (suffix: string) => LOCALES.map((locale) => `${locale}/${suffix}`);
const pathAsId = ({ entry }: { entry: string }) => entry.replace(/\.mdx$/, "");

const editions = defineCollection({
  loader: glob({ base: BUILD_ROOT, pattern: localizedPatterns(`${editionGroup}/index.mdx`), generateId: pathAsId }),
  schema: z.object({ title: z.string(), edition: z.string() }),
});

const chapters = defineCollection({
  loader: glob({ base: BUILD_ROOT, pattern: localizedPatterns(`${editionGroup}/*/index.mdx`), generateId: pathAsId }),
  schema: z.object({
    title: z.string(), ident: z.string(), edition: z.string(), chapterNumber: z.number(), videoUrl: z.string().optional(),
  }),
});

const sections = defineCollection({
  loader: glob({
    base: BUILD_ROOT,
    pattern: [
      ...localizedPatterns(`${editionGroup}/*/*.mdx`),
      ...localizedPatterns(`${editionGroup}/*/index.mdx`).map((pattern) => `!${pattern}`),
    ],
    generateId: pathAsId,
  }),
  schema: z.object({
    title: z.string(), ident: z.string(), edition: z.string(), chapterIdent: z.string(),
    chapterNumber: z.number(), sectionNumber: z.number(), videoUrl: z.string().optional(),
    status: z.string().optional(), class: z.string().optional(),
  }),
});

function localizedIncludesLoader(root: URL): Loader {
  const path = fileURLToPath(root);
  return {
    name: "localized-includes-loader",
    load: async ({ store, parseData, generateDigest, logger, watcher }: LoaderContext) => {
      store.clear();
      for (const locale of LOCALES) {
        const directory = join(path, locale, "includes");
        let names: string[];
        try { names = (await readdir(directory)).filter((name) => name.endsWith(".html")); }
        catch { logger.warn(`No includes at ${directory}`); continue; }
        for (const name of names) {
          const html = await readFile(join(directory, name), "utf-8");
          const id = `${locale}/${basename(name, ".html")}`;
          store.set({ id, data: await parseData({ id, data: { html } }), digest: generateDigest(html) });
        }
        watcher?.add(directory);
      }
    },
  };
}

const includes = defineCollection({
  loader: localizedIncludesLoader(BUILD_ROOT), schema: z.object({ html: z.string() }),
});

const questionPicture = z.object({ id: z.string(), alt: z.string() });
const questions = defineCollection({
  loader: {
    name: "localized-questions-loader",
    load: async ({ store, parseData, generateDigest, logger, watcher }: LoaderContext) => {
      store.clear();
      for (const locale of LOCALES) {
        const path = fileURLToPath(new URL(`${locale}/_data/questions.json`, BUILD_ROOT));
        try {
          const source = await readFile(path, "utf-8");
          const questions = JSON.parse(source) as Record<string, unknown>;
          for (const [number, value] of Object.entries(questions)) {
            const id = `${locale}/${number}`;
            store.set({ id, data: await parseData({ id, data: { ...(value as object), locale } }), digest: generateDigest(JSON.stringify(value)) });
          }
          watcher?.add(path);
        } catch (error) {
          logger.error(`Cannot load localized questions from ${path}: ${String(error)}`);
          throw error;
        }
      }
    },
  },
  schema: z.object({
    locale: z.enum(LOCALES), class: z.enum(["N", "E", "A"]).optional(),
    question: z.string(), picture: questionPicture.optional(),
    answers: z.array(z.object({ text: z.string().optional(), picture: questionPicture.optional() })).length(4),
    layout: z.string().optional(),
  }),
});

export const collections = { editions, chapters, sections, includes, questions };
