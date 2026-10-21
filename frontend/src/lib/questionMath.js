const MATH_COMMANDS = new Map([
  ["qtyrange", 3],
  ["qty", 2],
  ["num", 1],
  ["unit", 1],
]);

/**
 * Add math delimiters around supported DARCdown/siunitx commands in question
 * text, while leaving expressions that already have delimiters unchanged.
 *
 * @param {string} text
 * @returns {string}
 */
export function delimitUnwrappedQuestionMath(text) {
  let output = "";
  let position = 0;
  /** @type {string | null} */
  let closingDelimiter = null;

  while (position < text.length) {
    const char = text[position];

    if (
      !isEscaped(text, position)
      && (char === "$"
        || text.startsWith("\\(", position)
        || text.startsWith("\\[", position))
    ) {
      if (char === "$") {
        const delimiter = text.startsWith("$$", position) ? "$$" : "$";
        output += delimiter;
        position += delimiter.length;
        closingDelimiter =
          closingDelimiter === delimiter ? null : (
            (closingDelimiter ?? delimiter)
          );
      } else {
        const delimiter = text.startsWith("\\(", position) ? "\\(" : "\\[";
        output += delimiter;
        position += delimiter.length;
        closingDelimiter =
          closingDelimiter ?? (delimiter === "\\(" ? "\\)" : "\\]");
      }
      continue;
    }

    if (closingDelimiter && text.startsWith(closingDelimiter, position)) {
      output += closingDelimiter;
      position += closingDelimiter.length;
      closingDelimiter = null;
      continue;
    }

    if (!closingDelimiter && text.startsWith("\\\\", position)) {
      output += "\\\\";
      position += 2;
      continue;
    }

    if (!closingDelimiter && char === "\\") {
      const commandMatch = /^\\([A-Za-z]+)(?![A-Za-z])/.exec(
        text.slice(position),
      );
      const arity =
        commandMatch ? MATH_COMMANDS.get(commandMatch[1]) : undefined;
      if (commandMatch && arity) {
        const end = readCommandArguments(
          text,
          position + commandMatch[0].length,
          arity,
        );
        if (end !== undefined) {
          output += `$${text.slice(position, end)}$`;
          position = end;
          continue;
        }
      }
    }

    output += char;
    position += 1;
  }

  return output;
}

/** @param {string} text @param {number} position @param {number} arity */
function readCommandArguments(text, position, arity) {
  let cursor = position;
  for (let argument = 0; argument < arity; argument += 1) {
    while (/\s/.test(text[cursor] ?? "") && cursor < text.length) cursor += 1;
    if (text[cursor] !== "{") return undefined;

    let depth = 0;
    do {
      if (!isEscaped(text, cursor)) {
        if (text[cursor] === "{") depth += 1;
        else if (text[cursor] === "}") depth -= 1;
      }
      cursor += 1;
    } while (cursor < text.length && depth > 0);

    if (depth !== 0) return undefined;
  }
  return cursor;
}

/** @param {string} text @param {number} position */
function isEscaped(text, position) {
  let slashes = 0;
  for (
    let cursor = position - 1;
    cursor >= 0 && text[cursor] === "\\";
    cursor -= 1
  )
    slashes += 1;
  return slashes % 2 === 1;
}
