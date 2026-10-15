/**
 * Port of `normalize_index_part` / `index_anchor_id` in
 * packages/ohm-renderer/src/ohm_renderer/index.py.
 *
 * The MDX carries only the terms of an index entry, so the anchor id has to be derived here.
 * It must match the Python implementation exactly, because the same ids end up in the search
 * index (`_data/index.json`) that the search page links against.
 */

/** Reduces a term to the characters that are safe inside an anchor id. */
function normalizeIndexPart(value: string): string {
  let normalized = value.trim().toLowerCase();
  normalized = normalized.replace(/\s+/gu, "_");
  // Python's `\w` is Unicode-aware, so umlauts survive — JS `\w` is not, hence the classes.
  normalized = normalized.replace(/[^\p{L}\p{N}_]/gu, "_");
  normalized = normalized.replace(/_+/gu, "_").replace(/^_+|_+$/gu, "");
  return normalized || "index";
}

/** The anchor id an index entry gets, shared by the renderers and the builders. */
export function indexAnchorId(first: string, second?: string | null): string {
  const normalized = normalizeIndexPart(first);
  if (second) {
    return `index_${normalized}__${normalizeIndexPart(second)}`;
  }
  return `index_${normalized}`;
}
