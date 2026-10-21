import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import vm from "node:vm";
import { delimitUnwrappedQuestionMath } from "../src/lib/questionMath.js";

const assetRoot = new URL("../public/assets/", import.meta.url);

function loadMathConfiguration() {
  const katexContext = { exports: {}, module: { exports: {} } };
  vm.runInNewContext(
    readFileSync(new URL("katex/katex.min.js", assetRoot), "utf8"),
    katexContext,
  );

  let onReady;
  let renderOptions;
  vm.runInNewContext(readFileSync(new URL("latex.js", assetRoot), "utf8"), {
    document: {
      body: {},
      addEventListener: (_event, callback) => {
        onReady = callback;
      },
    },
    renderMathInElement: (_root, options) => {
      renderOptions = options;
    },
  });
  onReady();

  return { katex: katexContext.module.exports, macros: renderOptions.macros };
}

test("wraps un-delimited quantities without changing existing math", () => {
  assert.equal(
    delimitUnwrappedQuestionMath(
      "Ein \\qty{20}{\\m} langer Draht; Antwort: \\qty{13,33}{\\m} und \\qty{6,67}{\\m}.",
    ),
    "Ein $\\qty{20}{\\m}$ langer Draht; Antwort: $\\qty{13,33}{\\m}$ und $\\qty{6,67}{\\m}$.",
  );
  assert.equal(
    delimitUnwrappedQuestionMath(
      "Bereits gesetzt: $f = \\qty{2,7}{\\kHz}$; \\qtyrange{1}{2}{\\kHz}.",
    ),
    "Bereits gesetzt: $f = \\qty{2,7}{\\kHz}$; $\\qtyrange{1}{2}{\\kHz}$.",
  );
  assert.equal(
    delimitUnwrappedQuestionMath("Wert \\num{1000}; Einheit \\unit{\\V}."),
    "Wert $\\num{1000}$; Einheit $\\unit{\\V}$.",
  );
});

test("the site KaTeX macros render pool unit aliases and upright symbols", () => {
  const { katex, macros } = loadMathConfiguration();
  const expressions = [
    ["\\qty{2,7}{\\kHz}", "kHz"],
    ["\\qty{9}{\\V}", "V"],
    ["\\qty{1}{\\kohm}", "Ω"],
    ["\\qty{10}{\\nF}", "nF"],
    ["\\qty{2}{\\g}", "g"],
    ["R_{\\symup{L}} = R_{\\symup{i}}", "L"],
  ];

  for (const [expression, expectedText] of expressions) {
    const html = katex.renderToString(expression, {
      macros,
      throwOnError: true,
    });
    assert.match(html, new RegExp(expectedText));
    assert.doesNotMatch(html, /katex-error/);
  }
});
