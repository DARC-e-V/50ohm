/**
 * @type {import("prettier").Config}
 */
export default {
  tabWidth: 2,
  experimentalTernaries: true,
  experimentalOperatorPosition: "start",
  objectWrap: "collapse",
  plugins: ["prettier-plugin-astro", "prettier-plugin-bootstrap"],
  overrides: [{ files: "*.astro", options: { parser: "astro" } }],
};
