// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import { satteri } from '@astrojs/markdown-satteri';

import copyCourseAssets from './integrations/copy-course-assets.mjs';
import mathAsText from './markdown/math-as-text.mjs';

// https://astro.build/config
export default defineConfig({
    integrations: [mdx(), copyCourseAssets()],
    markdown: {
        // `math` is off by default, and without it MDX reads the `{` in `\qty{1}{\hertz}` as a
        // JSX expression — 56 % of the generated files fail to parse. It is enabled for the
        // parser only; math-as-text hands the `$…$` back for the client-side KaTeX to render.
        processor: satteri({
            features: { math: true },
            mdastPlugins: [mathAsText()],
        }),
    },
    vite: {
        css: {
            preprocessorOptions: {
                scss: {
                    // Bootstrap 5.3 still uses these, silence the warnings.
                    // Configured as recommended in https://getbootstrap.com/docs/5.3/getting-started/vite/#configure-vite
                    silenceDeprecations: ['import', 'mixed-decls', 'color-functions', 'global-builtin']
                }
            }
        }
    }
});
