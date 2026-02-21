document.addEventListener("DOMContentLoaded", function() {

    function formatThousands(input) {
        
        let s = String(input).trim();

        // Extract exponent (e or E) and convert to \cdot 10^{...}
        let exponent = "";
        const expMatch = s.match(/([eE])([+-]?\d+)$/);
        if (expMatch) {
            let expValue = expMatch[2];

            // Remove leading "+"
            if (expValue[0] === "+") {
                expValue = expValue.slice(1);
            }

            // Parse exponent as a numeric value
            const expNum = parseInt(expValue, 10);

            // Suppress exponent if it is 0 (no \cdot 10^0 shown)
            if (expNum !== 0) {
                exponent = "\\cdot 10^{" + expNum + "}";
            }

            s = s.slice(0, -expMatch[0].length);
        }

        // Sign (+, -, \pm). Also accept "\\pm" (double-escaped backslash) and optional whitespace.
        let sign = "";
        const pmMatch = s.match(/^(?:\\\\pm|\\pm)\s*/);
        if (pmMatch) {
            sign = "\\pm";
            s = s.slice(pmMatch[0].length);
        } else if (s[0] === "+" || s[0] === "-") {
            sign = s[0];
            s = s.slice(1);
        }

        // Find decimal point (last . or ,)
        let intPart = s;
        let fracSep = "";
        let fracDigits = "";
        const decMatch = s.match(/([.,])(\d+)$/);
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
        return sign + intPart + (fracDigits ? (fracSep + fracDigits) : "") + exponent;
    }


    var macros = {
        ",": (context) => context.future()?.text === " " ? "{\\char`,}" : "\\char`,",
        "\\num": (context) => {
            const [arg] = context.consumeArgs(1);
            const raw = arg.reverse().map(t => t.text).join("");
            return formatThousands(raw);
        },
        "\\qty": (context) => {
            const [numTok, unitTok] = context.consumeArgs(2);
            const rawNum = numTok.reverse().map(t => t.text).join("");
            const unit = unitTok.reverse().map(t => t.text).join("");
            const formattedNum = formatThousands(rawNum);
            if (unit.startsWith("\\degree")) {
                return formattedNum + "\\mathrm{" + unit + "}";
            } else {
                return formattedNum + "\\,\\mathrm{" + unit + "}";
            }
        },
        "\\qtyrange": (context) => {
            const [aTok, bTok, unitTok] = context.consumeArgs(3);
            const aRaw = aTok.reverse().map(t => t.text).join("");
            const bRaw = bTok.reverse().map(t => t.text).join("");
            const unit = unitTok.reverse().map(t => t.text).join("");
            const aFmt = formatThousands(aRaw);
            const bFmt = formatThousands(bRaw);
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
        "\\bit": "\\text{b}",
        "\\baud": "\\text{Bd}",
        "\\degreeCelsius": "\\,\\degree\\text{C}",
        "\\liter": "\\text{l}",
        "\\oszidiv": "\\text{div}",
        "\\sps": "\\text{sps}",
    };

    renderMathInElement(document.body, {
        delimiters: [
            { left: '$$', right: '$$', display: true }, // Note: $$ has to come before $
            { left: '$', right: '$', display: false },
            { left: '\\[', right: '\\]', display: true },
            { left: "\\(", right: "\\)", display: false },
        ],
        throwOnError: false,
        macros: macros
    });

});
