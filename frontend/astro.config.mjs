// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
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
