/**
 * The editions the builder produces, in the order the landing page lists them.
 *
 * Port of `Edition` in packages/ohm-builder/src/ohm_builder/edition.py.
 */
export const EDITIONS = ["N", "E", "A", "NE", "EA", "NEA"] as const;

export type Edition = (typeof EDITIONS)[number];
