/**
 * Shuffles the answers of every question and evaluates the clicks on them.
 *
 * Port of `shuffleChildren()` and `answer()` from ohm_builder/assets/script.js. The HTML build
 * passed the result to `answer()` through an `onclick` per button; `Question.astro` marks the
 * correct answer with `data-correct` instead, and one listener per question handles all four.
 */

const RESULT_TEXT = { correct: "richtig", wrong: "falsch" };

/** Appends the children in random order; appending a child moves it to the end. */
function shuffle(container: Element) {
  const remaining = [...container.children];
  while (remaining.length > 0) {
    container.append(...remaining.splice(Math.floor(Math.random() * remaining.length), 1));
  }
}

function evaluate(event: Event) {
  if (!(event.target instanceof Element)) return;

  const button = event.target.closest("button");
  if (!button) return;

  const result = button.dataset.correct === undefined ? "wrong" : "correct";
  button.classList.add(result);

  const text = button.querySelector(".result-text");
  if (text) text.textContent = RESULT_TEXT[result];
}

for (const answers of document.querySelectorAll(".question .answers")) {
  shuffle(answers);

  // Only now: as a live region from the start, the shuffle would read out every answer.
  answers.setAttribute("aria-live", "polite");
  answers.addEventListener("click", evaluate);
}
