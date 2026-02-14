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
});

function answer(el, correct) {
  if (correct)
    el.classList.add("correct")
  else
    el.classList.add("wrong")
}

/*
var els = document.querySelectorAll(".question .question-text");

for (i = 0; i < els.length; i++) {
  let el = els[i];
  katex.render(el.innerHTML, el, { throwOnError: false });
}
*/
