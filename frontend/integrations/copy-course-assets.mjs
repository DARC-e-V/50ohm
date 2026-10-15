import { cp, mkdir, stat } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { join } from "node:path";

/**
 * Copies the generated parts of the course build into `public/`.
 *
 * The MDX the builder emits references its images with root-absolute URLs
 * (`![…](/pictures/<id>.svg)`), and the copied search page fetches the indices from
 * `/assets/…`. Both have to be served from the site root, so they cannot stay in the
 * builder's output directory next to the MDX the content collections read from there.
 *
 * @param {{ source?: string }} [options] Builder output directory, relative to the Astro root.
 */
export default function copyCourseAssets({ source = "../build" } = {}) {
  /** @type {() => Promise<void>} */
  let copy;

  return {
    name: "copy-course-assets",
    hooks: {
      "astro:config:setup": ({ config, logger }) => {
        const root = fileURLToPath(config.root);
        const publicDir = fileURLToPath(config.publicDir);
        const from = join(root, source);

        copy = async () => {
          if (!(await exists(from))) {
            logger.warn(`No builder output at ${from} — run \`ohm -f mdx -o ${source}\` first.`);
            return;
          }

          // Directories: copied wholesale, keeping files a previous run left behind.
          for (const name of ["pictures", "photos"]) {
            if (await exists(join(from, name))) {
              await cp(join(from, name), join(publicDir, name), { recursive: true });
            }
          }

          // The search indices: the copied suche.html fetches them from /assets/.
          const assets = join(publicDir, "assets");
          await mkdir(assets, { recursive: true });
          for (const name of ["index.json", "question_index.json"]) {
            const file = join(from, "_data", name);
            if (await exists(file)) {
              await cp(file, join(assets, name));
            }
          }
        };
      },
      // Both entry points, so `astro dev` serves the same files `astro build` emits.
      "astro:server:setup": async () => {
        await copy();
      },
      "astro:build:start": async () => {
        await copy();
      },
    },
  };
}

async function exists(path) {
  try {
    await stat(path);
    return true;
  } catch {
    return false;
  }
}
