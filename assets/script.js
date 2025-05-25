document.addEventListener("DOMContentLoaded", function() {
  var macros = {
    ",": (context) => context.future()?.text === " " ? "{\\char`,}" : "\\char`,",
    "\\qty": "{#1\\,\\mathrm{#2}}",
    "\\squared": "{^{2}}",
    "\\cubed": "{^{3}}",
    "\\per": "/",
    "\\tera": "T",
    "\\giga": "G",
    "\\mega": "M",
    "\\kilo": "k",
    "\\milli": "m",
    "\\micro": "\\text{μ}",
    "\\nano": "n",
    "\\kilogram": "\\text{kg}",
    "\\meter": "\\text{m}",
    "\\second": "\\text{s}",
    "\\ampere": "\\text{A}",
    "\\kelvin": "\\text{K}",
    "\\mol": "\\text{mol}",
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
    "\\weber": "\\text{Wb}",
    "\\tesla": "\\text{T}",
  };
  renderMathInElement(document.body, {
    delimiters: [{left: '$', right: '$', display: false}],
    throwOnError : false,
    macros: macros
  });
  renderMathInElement(document.body, {
    delimiters: [{left: '\\[', right: '\\]', display: false}],
    throwOnError : false
  });
});

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
