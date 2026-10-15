/**
 * Port of `Morse.convert_to_morse_code` in packages/ohm-renderer/src/ohm_renderer/morse.py.
 *
 * The MDX carries the plain text (`<Morse text="…" />`), so the conversion happens here.
 */

const DIT = 1;
const DAH = 2;
const SPACE = 3;

export type MorseSymbol = typeof DIT | typeof DAH | typeof SPACE;

const MORSE_CODE: Record<string, MorseSymbol[]> = {
  a: [DIT, DAH],
  b: [DAH, DIT, DIT, DIT],
  c: [DAH, DIT, DAH, DIT],
  d: [DAH, DIT, DIT],
  e: [DIT],
  f: [DIT, DIT, DAH, DIT],
  g: [DAH, DAH, DIT],
  h: [DIT, DIT, DIT, DIT],
  i: [DIT, DIT],
  j: [DIT, DAH, DAH, DAH],
  k: [DAH, DIT, DAH],
  l: [DIT, DAH, DIT, DIT],
  m: [DAH, DAH],
  n: [DAH, DIT],
  o: [DAH, DAH, DAH],
  p: [DIT, DAH, DAH, DIT],
  q: [DAH, DAH, DIT, DAH],
  r: [DIT, DAH, DIT],
  s: [DIT, DIT, DIT],
  t: [DAH],
  u: [DIT, DIT, DAH],
  v: [DIT, DIT, DIT, DAH],
  w: [DIT, DAH, DAH],
  x: [DAH, DIT, DIT, DAH],
  y: [DAH, DIT, DAH, DAH],
  z: [DAH, DAH, DIT, DIT],
  ä: [DIT, DAH, DIT, DAH],
  ö: [DAH, DAH, DAH, DIT],
  ü: [DIT, DIT, DAH, DAH],
  ß: [DIT, DIT, DIT, DAH, DAH, DIT, DIT],
  "0": [DAH, DAH, DAH, DAH, DAH],
  "1": [DIT, DAH, DAH, DAH, DAH],
  "2": [DIT, DIT, DAH, DAH, DAH],
  "3": [DIT, DIT, DIT, DAH, DAH],
  "4": [DIT, DIT, DIT, DIT, DAH],
  "5": [DIT, DIT, DIT, DIT, DIT],
  "6": [DAH, DIT, DIT, DIT, DIT],
  "7": [DAH, DAH, DIT, DIT, DIT],
  "8": [DAH, DAH, DAH, DIT, DIT],
  "9": [DAH, DAH, DAH, DAH, DIT],
  ".": [DIT, DAH, DIT, DAH, DIT, DAH],
  ",": [DAH, DAH, DIT, DIT, DAH, DAH],
  ":": [DAH, DAH, DAH, DIT, DIT, DIT],
  ";": [DAH, DIT, DAH, DIT, DAH, DIT],
  "?": [DIT, DIT, DAH, DAH, DIT, DIT],
  "!": [DAH, DIT, DAH, DIT, DAH, DAH],
  "-": [DAH, DIT, DIT, DIT, DIT, DAH],
  _: [DIT, DIT, DAH, DAH, DIT, DAH],
  "(": [DAH, DIT, DAH, DAH, DIT],
  ")": [DAH, DIT, DAH, DAH, DIT, DAH],
  "'": [DIT, DAH, DAH, DAH, DAH, DIT],
  "=": [DAH, DIT, DIT, DIT, DAH],
  "+": [DIT, DAH, DIT, DAH, DIT],
  "/": [DAH, DIT, DIT, DAH, DIT],
  "@": [DIT, DAH, DAH, DIT, DAH, DIT],
  ar: [DIT, DAH, DIT, DAH, DIT],
  bk: [DAH, DIT, DIT, DIT, DAH, DIT, DAH],
  sk: [DIT, DIT, DIT, DAH, DIT, DAH],
  correction: [DIT, DIT, DIT, DIT, DIT, DIT, DIT, DIT],
  " ": [SPACE],
};

/** Turns a text into one symbol list per character, skipping unknown characters. */
export function convertToMorseCode(text: string): MorseSymbol[][] {
  const result: MorseSymbol[][] = [];

  for (const char of text) {
    result.push(MORSE_CODE[char.toLowerCase()]);
  }

  return result;
}
