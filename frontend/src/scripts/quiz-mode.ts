/**
 * Port of the quiz mode in ohm_builder/assets/script.js. Hides everything but questions.
 */

const NOTICE_ID = "quiz-mode-notice";
const STORAGE_KEY = "quiz-mode-enabled";
const QUIZ_ATTR = "data-quiz-mode";
const HAS_Q_ATTR = "data-quiz-has-questions";

function pageHasQuestions() {
  return document.querySelector(".course .question") !== null;
}

function showNotice(text: string) {
  let notice = document.getElementById(NOTICE_ID);
  if (!notice) {
    notice = document.createElement("div");
    notice.id = NOTICE_ID;
    notice.className = "alert alert-info";
    notice.setAttribute("role", "alert");
    notice.style.clear = "both";
    const course = document.querySelector(".course");
    if (course) {
      course.insertBefore(notice, course.firstChild);
    } else {
      document.body.appendChild(notice);
    }
  }
  notice.textContent = text;
}

function hideNotice() {
  document.getElementById(NOTICE_ID)?.remove();
}

function updateButton(button: HTMLElement, on: boolean) {
  button.setAttribute("aria-pressed", on ? "true" : "false");
  button.classList.toggle("btn-primary", on);
  button.classList.toggle("btn-secondary", !on);
  button.title = on ? "Alles anzeigen" : "Nur Fragen anzeigen";
}

function setQuizMode(button: HTMLElement, on: boolean) {
  const hasQuestions = pageHasQuestions();
  document.body.toggleAttribute(HAS_Q_ATTR, hasQuestions);
  document.body.toggleAttribute(QUIZ_ATTR, on);
  updateButton(button, on);
  if (on && !hasQuestions) {
    showNotice("Keine Fragen auf dieser Seite gefunden.");
  } else {
    hideNotice();
  }
}

const button = document.getElementById("quiz-mode-toggle");

if (button) {
  button.addEventListener("click", () => {
    const next = !document.body.hasAttribute(QUIZ_ATTR);
    setQuizMode(button, next);
    try {
      localStorage.setItem(STORAGE_KEY, next ? "1" : "0");
    } catch {
      // Without localStorage (e.g. blocked cookies) the choice just isn't remembered.
    }
  });

  let initial = false;
  try {
    initial = localStorage.getItem(STORAGE_KEY) === "1";
  } catch {
    // See above.
  }

  if (initial) {
    setQuizMode(button, true);
  } else {
    updateButton(button, false);
  }
}
