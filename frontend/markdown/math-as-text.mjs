/**
 * Turns math nodes back into `$…$` / `$$…$$` text.
 *
 * Sätteri's `math` feature has to be on, otherwise MDX reads the `{` in `\qty{1}{\hertz}` as the
 * start of a JSX expression and 56 % of the generated files fail to parse. But with it on, the
 * math would become `<code class="language-math">` (and display math even a syntax-highlighted
 * code block), and the `$` delimiters would be gone — while KaTeX renders in the browser, driven
 * by `/assets/auto-render.min.js` plus the macro table in `/assets/latex.js`, both of which scan
 * the DOM for exactly those delimiters.
 *
 * So the feature is used for its parser only: it tells MDX where the math is, and this plugin
 * hands the text straight back. The rendering stays where the HTML build had it.
 */
export default function mathAsText() {
  return {
    name: "math-as-text",

    /**
     * @param {{ value: string }} node
     * @returns {{ type: "text", value: string }}
     */
    inlineMath(node) {
      return { type: "text", value: `$${node.value}$` };
    },

    /**
     * Block position, so the text needs a block node around it.
     *
     * @param {{ value: string }} node
     * @returns {{ type: "paragraph", children: { type: "text", value: string }[] }}
     */
    math(node) {
      return { type: "paragraph", children: [{ type: "text", value: `$$${node.value}$$` }] };
    },
  };
}
