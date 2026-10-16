import { readFileSync } from "node:fs";
import { resolve } from "node:path";

export const swissProfile = import.meta.env.PUBLIC_SITE_PROFILE === "ch";
export const releaseId = import.meta.env.PUBLIC_CH_RELEASE_ID || "";
export const isBeta = import.meta.env.PUBLIC_CH_BETA === "true";
export const feedbackUrl = import.meta.env.PUBLIC_CH_FEEDBACK_URL || "";
export const frenchSiteUrl = import.meta.env.PUBLIC_CH_FR_URL || "";
export const italianSiteUrl = import.meta.env.PUBLIC_CH_IT_URL || "";

function inputFile(relativePath: string): string {
  const input = process.env.OHM_CH_INPUT_DIR;
  if (!input) throw new Error("OHM_CH_INPUT_DIR is required for the Swiss site profile");
  return readFileSync(resolve(input, relativePath), "utf8");
}

const labels: Record<string, string> = swissProfile
  ? JSON.parse(inputFile("generator_extra_content/de/labels.json"))
  : {};

export function siteLabel(key: string, upstreamValue: string): string {
  if (!swissProfile) return upstreamValue;
  const value = labels[key];
  if (typeof value !== "string") throw new Error(`Missing Swiss UI label: ${key}`);
  return value;
}

export function extractedHtml(name: string): string {
  if (!swissProfile) throw new Error("Extracted HTML is only used by the Swiss site profile");
  if (!["index", "kurse-karte", "kurse-liste", "patenkarte", "todo"].includes(name)) {
    throw new Error(`Unknown extracted HTML page: ${name}`);
  }
  return inputFile(`rendered_extra_content/html/${name}.html`);
}

export function canonicalStaticHtml(name: string): string {
  if (!swissProfile) throw new Error("Canonical static HTML is only used by the Swiss site profile");
  if (!["infos", "pruefung", "infos_sidebar", "pruefung_sidebar"].includes(name)) {
    throw new Error(`Unknown static HTML page: ${name}`);
  }
  return inputFile(`contents/static/${name}.html`);
}
