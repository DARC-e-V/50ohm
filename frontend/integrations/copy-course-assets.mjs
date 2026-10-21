import { cp, mkdir, stat } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { join, resolve } from "node:path";

/** Copy localized images and search indexes into their locale-prefixed public paths. */
export default function copyCourseAssets({ source = "../build", locales = ["de", "fr", "it"] } = {}) {
  let copy;
  return {
    name: "copy-course-assets",
    hooks: {
      "astro:config:setup": ({ config, logger }) => {
        const root = fileURLToPath(config.root);
        const publicDir = fileURLToPath(config.publicDir);
        const from = resolve(root, source);
        copy = async () => {
          if (!(await exists(from))) {
            logger.warn(`No localized builder output at ${from} — prepare all locale builds first.`);
            return;
          }
          for (const locale of locales) {
            const localized = join(from, locale);
            for (const name of ["pictures", "photos"]) {
              if (await exists(join(localized, name))) {
                await cp(join(localized, name), join(publicDir, locale, name), { recursive: true, force: true });
              }
            }
            const assets = join(publicDir, locale, "assets");
            await mkdir(assets, { recursive: true });
            for (const name of ["index.json", "question_index.json"]) {
              const file = join(localized, "_data", name);
              if (await exists(file)) await cp(file, join(assets, name));
            }
          }
        };
      },
      "astro:server:setup": async () => copy(),
      "astro:build:start": async () => copy(),
    },
  };
}

async function exists(path) {
  try { await stat(path); return true; } catch { return false; }
}
