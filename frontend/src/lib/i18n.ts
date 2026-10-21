import localeConfig from "../../i18n.config.json";

export const DEFAULT_LOCALE = localeConfig.defaultLocale;
export const LOCALES = localeConfig.locales as [string, ...string[]];
export type Locale = (typeof LOCALES)[number];

export function isLocale(value: string): value is Locale {
  return (LOCALES as readonly string[]).includes(value);
}

export const localePaths = () => LOCALES.map((locale) => ({ params: { lang: locale } }));
