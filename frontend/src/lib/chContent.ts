import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import type { Locale } from "./i18n";
import i18nConfig from "../../i18n.config.json";

export const swissProfile = import.meta.env.PUBLIC_SITE_PROFILE === "ch";
export const releaseId = import.meta.env.PUBLIC_CH_RELEASE_ID || "";
export const isBeta = import.meta.env.PUBLIC_CH_BETA === "true";
export const feedbackUrl = import.meta.env.PUBLIC_CH_FEEDBACK_URL || "";

function inputFile(locale: Locale, relativePath: string): string {
  const input = process.env.OHM_CH_INPUT_ROOT;
  if (!input) throw new Error("OHM_CH_INPUT_ROOT is required for the Swiss site profile");
  return readFileSync(resolve(input, locale, relativePath), "utf8");
}

const labelCache = new Map<Locale, Record<string, string>>();
function labelsFor(locale: Locale): Record<string, string> {
  const cached = labelCache.get(locale);
  if (cached) return cached;
  const labels: Record<string, string> = JSON.parse(inputFile(locale, `generator_extra_content/${locale}/labels.json`));
  labelCache.set(locale, labels);
  return labels;
}

export function siteLabel(locale: Locale, key: string, upstreamValue: string): string {
  if (!swissProfile) return upstreamValue;
  const label = labelsFor(locale)[key];
  if (typeof label === "string") return label;
  const messages = i18nConfig.messages as Record<Locale, Record<string, string>>;
  const message = messages[locale][key];
  if (typeof message === "string") return message;
  if (upstreamValue) return upstreamValue;
  throw new Error(`Missing Swiss UI label for ${locale}: ${key}`);
}

export function extractedHtml(locale: Locale, name: string): string {
  if (!swissProfile) throw new Error("Extracted HTML is only used by the Swiss site profile");
  if (!["index", "kurse-karte", "kurse-liste", "patenkarte", "todo"].includes(name)) {
    throw new Error(`Unknown extracted HTML page: ${name}`);
  }
  // Extracted pages use paths relative to the classic site root. Under Astro's
  // locale-prefixed routes those would resolve below /de/, /fr/, or /it/.
  return inputFile(locale, `rendered_extra_content/html/${name}.html`)
    .replace(/\b(src|href)=(['"])assets\//g, "$1=$2/assets/");
}

export function canonicalStaticHtml(locale: Locale, name: string): string {
  if (!swissProfile) throw new Error("Canonical static HTML is only used by the Swiss site profile");
  if (!["infos", "pruefung", "infos_sidebar", "pruefung_sidebar", "suche"].includes(name)) {
    throw new Error(`Unknown static HTML page: ${name}`);
  }
  return inputFile(locale, `contents/static/${name}.html`);
}
