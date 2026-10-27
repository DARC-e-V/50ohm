import { fileURLToPath } from "node:url";

/** @param {string} path Relative to `src/`. */
const src = (path) => new URL(`../src/${path}`, import.meta.url);

/**
 * The layouts, imported as `virtual:ohm/layouts/<Name>`.
 *
 * Each module, here and in the tables below, only re-exports the file listed. Nothing can
 * replace them yet: the indirection exists so that overriding one later changes where its module
 * resolves to, not the files that import it.
 */
const LAYOUTS = {
  BaseLayout: src("layouts/BaseLayout.astro"),
  PageLayout: src("layouts/PageLayout.astro"),
};

/** The site components, imported as `virtual:ohm/components/<Name>`. */
const COMPONENTS = {
  SiteHeader: src("components/SiteHeader.astro"),
  SiteFooter: src("components/SiteFooter.astro"),
  NextChapter: src("components/NextChapter.astro"),
  NextSection: src("components/NextSection.astro"),
};

/**
 * The components `FiftyOhmMdxRenderer` emits, imported as `virtual:ohm/mdx-components/<Name>`.
 * `virtual:ohm/mdx-components` bundles them into the map passed to `<Content components={…} />`.
 *
 * The generated MDX imports nothing, so this map is the whole contract. Everything else the
 * renderer produces — `<figure>`, `<figcaption>`, `<u>`, GFM tables, `![…](/pictures/…)` and
 * `$$ … $$` — is plain HTML or Markdown and needs no component.
 */
const MDX_COMPONENTS = {
  Anchor: src("mdx-components/Anchor.astro"),
  Include: src("mdx-components/Include.astro"),
  Index: src("mdx-components/Index.astro"),
  Morse: src("mdx-components/Morse.astro"),
  Qso: src("mdx-components/Qso.astro"),
  QsoLine: src("mdx-components/QsoLine.astro"),
  Question: src("mdx-components/Question.astro"),
  Reference: src("mdx-components/Reference.astro"),
  Tag: src("mdx-components/Tag.astro"),
};

const NAMESPACES = {
  "virtual:ohm/layouts": LAYOUTS,
  "virtual:ohm/components": COMPONENTS,
  "virtual:ohm/mdx-components": MDX_COMPONENTS,
};

const MDX_MAP = "virtual:ohm/mdx-components";

/** Provides the `virtual:ohm/…` modules and their type declarations. */
export default function ohm() {
  return {
    name: "ohm",
    hooks: {
      "astro:config:setup": ({ updateConfig }) => {
        updateConfig({ vite: { plugins: [vitePluginOhm()] } });
      },
      "astro:config:done": ({ injectTypes }) => {
        injectTypes({ filename: "virtual.d.ts", content: virtualTypes() });
      },
    },
  };
}

function vitePluginOhm() {
  const modules = virtualModules();

  return {
    name: "vite-plugin-ohm",
    /** @param {string} id */
    resolveId(id) {
      if (modules.has(id)) {
        return `\0${id}`;
      }
    },
    /** @param {string} id */
    load(id) {
      if (id.startsWith("\0")) {
        return modules.get(id.slice(1));
      }
    },
  };
}

/** The source of every virtual module, by id. */
function virtualModules() {
  /** @type {Map<string, string>} */
  const modules = new Map();

  for (const [namespace, components] of Object.entries(NAMESPACES)) {
    for (const [name, url] of Object.entries(components)) {
      modules.set(`${namespace}/${name}`, `export { default } from ${JSON.stringify(fileURLToPath(url))};`);
    }
  }

  const names = Object.keys(MDX_COMPONENTS);
  modules.set(
    MDX_MAP,
    [
      ...names.map((name) => `import ${name} from "${MDX_MAP}/${name}";`),
      `export default { ${names.join(", ")} };`,
    ].join("\n"),
  );

  return modules;
}

/**
 * Declarations for `virtualModules()`. Each component module gets the type of its file, so
 * `astro check` sees the real props.
 */
function virtualTypes() {
  const declarations = [];

  for (const [namespace, components] of Object.entries(NAMESPACES)) {
    for (const [name, url] of Object.entries(components)) {
      declarations.push(
        `declare module "${namespace}/${name}" {`,
        `  const ${name}: typeof import(${JSON.stringify(fileURLToPath(url))}).default;`,
        `  export default ${name};`,
        `}`,
      );
    }
  }

  declarations.push(
    `declare module "${MDX_MAP}" {`,
    `  const mdxComponents: {`,
    ...Object.keys(MDX_COMPONENTS).map(
      (name) => `    ${name}: typeof import("${MDX_MAP}/${name}").default;`,
    ),
    `  };`,
    `  export default mdxComponents;`,
    `}`,
  );

  return declarations.join("\n") + "\n";
}
