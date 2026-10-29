/**
 * Port of ohm_builder/assets/latex.js. Renders math.
 * TODO: Temporary solution, still needs some work and tidying up.
 */
import renderMathInElement from "katex/contrib/auto-render";

interface MacroExpander {
  future(): { text: string } | undefined;
  consumeArgs(count: number): { text: string }[][];
}

// KaTeX hands the tokens of an argument over in reverse order.
const argText = (tokens: { text: string }[]) =>
  tokens
    .reverse()
    .map((token) => token.text)
    .join("");

function formatThousands(input: string): string {
  let s = input.trim();

  // Extract exponent (e or E) and convert to \cdot 10^{...}
  let exponent = "";
  const expMatch = /([eE])([+-]?\d+)$/.exec(s);
  if (expMatch) {
    let expValue = expMatch[2];

    // Remove leading "+"
    if (expValue.startsWith("+")) {
      expValue = expValue.slice(1);
    }

    // Parse exponent as a numeric value
    const expNum = parseInt(expValue, 10);

    // Suppress exponent if it is 0 (no \cdot 10^0 shown)
    if (expNum !== 0) {
      exponent = "\\cdot 10^{" + expNum.toFixed(0) + "}";
    }

    s = s.slice(0, -expMatch[0].length);
  }

  // Sign (+, -, \pm). Also accept "\\pm" (double-escaped backslash) and optional whitespace.
  let sign = "";
  const pmMatch = /^(?:\\\\pm|\\pm)\s*/.exec(s);
  if (pmMatch) {
    sign = "\\pm";
    s = s.slice(pmMatch[0].length);
  } else if (s.startsWith("+") || s.startsWith("-")) {
    sign = s[0];
    s = s.slice(1);
  }

  // Find decimal point (last . or ,)
  let intPart = s;
  let fracSep = "";
  let fracDigits = "";
  const decMatch = /([.,])(\d+)$/.exec(s);
  if (decMatch) {
    intPart = s.slice(0, decMatch.index);
    fracSep = decMatch[1];
    fracDigits = decMatch[2];
  }

  // Thousand grouping in integer part
  if (intPart.length >= 5) {
    intPart = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, "\\,");
  }

  // Thousand grouping in fractional part (from left in 3-digit blocks)
  if (fracDigits.length >= 4) {
    fracDigits = fracDigits.replace(/(\d{3})(?=\d)/g, "$1\\,");
  }

  // Reassemble
  return sign + intPart + (fracDigits ? fracSep + fracDigits : "") + exponent;
}

const macros: Record<string, string | ((context: MacroExpander) => string)> = {
  ",": (context) =>
    context.future()?.text === " " ? "{\\char`,}" : "\\char`,",
  "\\num": (context) => {
    const [arg] = context.consumeArgs(1);
    return formatThousands(argText(arg));
  },
  "\\qty": (context) => {
    const [numTok, unitTok] = context.consumeArgs(2);
    const formattedNum = formatThousands(argText(numTok));
    const unit = argText(unitTok);
    if (unit.startsWith("\\degree")) {
      return formattedNum + "\\mathrm{" + unit + "}";
    } else {
      return formattedNum + "\\,\\mathrm{" + unit + "}";
    }
  },
  "\\qtyrange": (context) => {
    const [aTok, bTok, unitTok] = context.consumeArgs(3);
    const aFmt = formatThousands(argText(aTok));
    const bFmt = formatThousands(argText(bTok));
    const unit = argText(unitTok);
    if (unit.startsWith("\\degree")) {
      return aFmt + "\\text{--}\\," + bFmt + "\\mathrm{" + unit + "}";
    } else {
      return aFmt + "\\,\\text{--}\\," + bFmt + "\\,\\mathrm{" + unit + "}";
    }
  },
  "\\unit": "{\\mathrm{#1}}",
  "\\squared": "{^{2}}",
  "\\cubed": "{^{3}}",
  "\\per": "/",
  "\\percent": "\\%",
  "\\ppm": "\\text{ppm}",
  "\\tera": "\\text{T}",
  "\\giga": "\\text{G}",
  "\\mega": "\\text{M}",
  "\\kilo": "\\text{k}",
  "\\dezi": "\\text{d}",
  "\\centi": "\\text{c}",
  "\\milli": "\\text{m}",
  "\\micro": "\\text{μ}",
  "\\nano": "\\text{n}",
  "\\pico": "\\text{p}",
  "\\kilogram": "\\text{kg}",
  "\\gram": "\\text{g}",
  "\\meter": "\\text{m}",
  "\\second": "\\text{s}",
  "\\hour": "\\text{h}",
  "\\ampere": "\\text{A}",
  "\\kelvin": "\\text{K}",
  "\\mol": "\\text{mol}",
  "\\bel": "\\text{B}",
  "\\dezibel": "\\text{dB}",
  "\\dB": "\\text{dB}",
  "\\dBm": "\\text{dBm}",
  "\\dBu": "\\text{dBu}",
  "\\dBV": "\\text{dB}\\volt",
  "\\dBuV": "\\text{dB}\\micro\\volt",
  "\\dBW": "\\text{dBW}",
  "\\dBi": "\\text{dBi}",
  "\\dBd": "\\text{dBd}",
  "\\candela": "\\text{cd}",
  "\\newton": "\\text{N}",
  "\\hertz": "\\text{Hz}",
  "\\pascal": "\\text{Pa}",
  "\\volt": "\\text{V}",
  "\\watt": "\\text{W}",
  "\\joule": "\\text{J}",
  "\\henry": "\\text{H}",
  "\\farad": "\\text{F}",
  "\\coulomb": "\\text{C}",
  "\\ohm": "\\Omega",
  "\\Ohm": "\\Omega",
  "\\weber": "\\text{Wb}",
  "\\tesla": "\\text{T}",
  "\\bit": "\\text{Bit}",
  "\\baud": "\\text{Bd}",
  "\\degreeCelsius": "\\,\\degree\\text{C}",
  "\\liter": "\\text{l}",
  "\\oszidiv": "\\text{div}",
  "\\sps": "\\text{sps}",
};

renderMathInElement(document.body, {
  delimiters: [
    { left: "$$", right: "$$", display: true }, // Note: $$ has to come before $
    { left: "$", right: "$", display: false },
    { left: "\\[", right: "\\]", display: true },
    { left: "\\(", right: "\\)", display: false },
  ],
  throwOnError: false,
  macros,
});
