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
  var QUIZ_ATTR = "data-quiz-mode";
  var HAS_Q_ATTR = "data-quiz-has-questions";

  function pageHasQuestions() {
    return document.querySelector(".course .question") !== null;
  }

  function showNotice(text) {
    var n = document.getElementById(NOTICE_ID);
    if (!n) {
      n = document.createElement("div");
      n.id = NOTICE_ID;
      n.className = "alert alert-info";
      n.setAttribute("role", "alert");
      n.style.clear = "both";
      var course = document.querySelector(".course");
      if (course) {
        course.insertBefore(n, course.firstChild);
      } else {
        document.body.appendChild(n);
      }
    }
    n.textContent = text;
  }

  function hideNotice() {
    var n = document.getElementById(NOTICE_ID);
    if (n) n.parentNode.removeChild(n);
  }

  function updateButton(btn, on) {
    btn.setAttribute("aria-pressed", on ? "true" : "false");
    btn.classList.toggle("btn-primary", on);
    btn.classList.toggle("btn-secondary", !on);
    btn.title = on ? "Alles anzeigen" : "Nur Fragen anzeigen";
  }

  function setQuizMode(on) {
    var hasQ = pageHasQuestions();
    if (hasQ) document.body.setAttribute(HAS_Q_ATTR, "");
    else document.body.removeAttribute(HAS_Q_ATTR);
    if (on) document.body.setAttribute(QUIZ_ATTR, "");
    else document.body.removeAttribute(QUIZ_ATTR);
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
      var next = !document.body.hasAttribute(QUIZ_ATTR);
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
