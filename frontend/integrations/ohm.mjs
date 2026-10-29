import { fileURLToPath } from "node:url";

/** @param {string} path Relative to `src/`. */
const src = (path) => new URL(`../src/${path}`, import.meta.url);

/** The building blocks of any page of the site, imported as `virtual:ohm/site/<Name>`. */
const SITE = {
  Head: src("site/Head.astro"),
  BaseLayout: src("site/BaseLayout.astro"),
  PageLayout: src("site/PageLayout.astro"),
  SiteHeader: src("site/SiteHeader.astro"),
  SiteFooter: src("site/SiteFooter.astro"),
  Breadcrumbs: src("site/Breadcrumbs.astro"),
};

/** The building blocks only the course pages use, imported as `virtual:ohm/course/<Name>`. */
const COURSE = {
  CourseToolbar: src("course/CourseToolbar.astro"),
  CourseContent: src("course/CourseContent.astro"),
  TableOfContents: src("course/TableOfContents.astro"),
  NextSection: src("course/NextSection.astro"),
  NextChapter: src("course/NextChapter.astro"),
  QuestionSearch: src("course/QuestionSearch.astro"),
};

/** Course pages, imported as `virtual:ohm/page-components/<Name>`. */
const PAGE_COMPONENTS = {
  EditionPage: src("page-components/EditionPage.astro"),
  ChapterPage: src("page-components/ChapterPage.astro"),
  SectionPage: src("page-components/SectionPage.astro"),
};

/**
 * The components `FiftyOhmMdxRenderer` emits, imported as `virtual:ohm/mdx-components/<Name>`.
 * `virtual:ohm/mdx-components` bundles them into the map passed to `<Content components={…} />`.
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
  "virtual:ohm/site": SITE,
  "virtual:ohm/course": COURSE,
  "virtual:ohm/page-components": PAGE_COMPONENTS,
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
      modules.set(
        `${namespace}/${name}`,
        `export { default } from ${JSON.stringify(fileURLToPath(url))};`,
      );
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
