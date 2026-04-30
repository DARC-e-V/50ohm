function shuffleChildren(el) {
  for (var i = el.children.length; i >= 0; i--) {
      el.appendChild(el.children[Math.random() * i | 0]);
  }
}

document.addEventListener("DOMContentLoaded", function() {
  var els = document.querySelectorAll(".answers");
  for (var i = 0; i < els.length; i++) {
    shuffleChildren(els[i]);
  }
  initQuizMode();
});

function answer(el, correct) {
  if (correct)
    el.classList.add("correct")
  else
    el.classList.add("wrong")
}

(function () {
  var NOTICE_ID = "quiz-mode-notice";
  var STORAGE_KEY = "quiz-mode-enabled";
  var QUIZ_CLASS = "quiz-mode-active";
  var HAS_Q_CLASS = "quiz-has-questions";

  function pageHasQuestions() {
    return document.querySelector(".course .question") !== null;
  }

  function tagSectionTail() {
    var course = document.querySelector(".course");
    if (!course) return false;
    var tagged = course.querySelectorAll("[data-quiz-tail]");
    for (var i = 0; i < tagged.length; i++) {
      tagged[i].removeAttribute("data-quiz-tail");
    }
    var children = course.children;
    for (var j = 0; j < children.length; j++) {
      var child = children[j];
      if (child.tagName !== "DIV") continue;
      var text = (child.textContent || "").toLowerCase();
      if (text.indexOf("weiter zum nächsten abschnitt") !== -1 ||
          text.indexOf("weiter zum nächsten kapitel") !== -1) {
        child.setAttribute("data-quiz-tail", "");
        return true;
      }
    }
    return false;
  }

  function showNotice(text) {
    var n = document.getElementById(NOTICE_ID);
    if (!n) {
      n = document.createElement("div");
      n.id = NOTICE_ID;
      document.body.appendChild(n);
    }
    n.textContent = text;
  }

  function hideNotice() {
    var n = document.getElementById(NOTICE_ID);
    if (n) n.parentNode.removeChild(n);
  }

  function updateButton(btn, on) {
    btn.setAttribute("aria-pressed", on ? "true" : "false");
    btn.classList.toggle("active", on);
    btn.title = on ? "Alles anzeigen" : "Nur Fragen anzeigen";
  }

  function setQuizMode(on) {
    var hasQ = pageHasQuestions();
    document.body.classList.toggle(HAS_Q_CLASS, hasQ);
    if (on && hasQ) tagSectionTail();
    document.body.classList.toggle(QUIZ_CLASS, on);
    var btn = document.getElementById("quiz-mode-toggle");
    if (btn) updateButton(btn, on);
    if (on && !hasQ) {
      showNotice("Keine Fragen auf dieser Seite gefunden.");
    } else {
      hideNotice();
    }
  }

  window.initQuizMode = function () {
    var btn = document.getElementById("quiz-mode-toggle");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var next = !document.body.classList.contains(QUIZ_CLASS);
      setQuizMode(next);
      try { localStorage.setItem(STORAGE_KEY, next ? "1" : "0"); } catch (e) {}
    });
    var initial = false;
    try { initial = localStorage.getItem(STORAGE_KEY) === "1"; } catch (e) {}
    if (initial) setQuizMode(true);
    else updateButton(btn, false);
  };
})();

/*
var els = document.querySelectorAll(".question .question-text");

for (i = 0; i < els.length; i++) {
  let el = els[i];
  katex.render(el.innerHTML, el, { throwOnError: false });
}
*/
