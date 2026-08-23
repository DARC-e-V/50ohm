(function () {
  "use strict";

  function normalizeCatalog(rawCatalog, metadata, questionIndex) {
    var questions = {};
    var partForSection = { 1: "B", 2: "V" };
    var partForClass = { "1": "N", "2": "E", "3": "A" };

    function pictureId(value) {
      return value ? String(value) : "";
    }

    function walk(section, sectionIndex, category) {
      (section.questions || []).forEach(function (question) {
        var part = String(question.class) === "SWL"
          ? "SWL"
          : (sectionIndex === 0 ? partForClass[String(question.class)] : partForSection[sectionIndex]);
        if (!part) return;

        var questionMetadata = metadata[question.number] || {};
        questions[question.number] = {
          id: question.number,
          part: part,
          category: category.slice(),
          question: question.question,
          layout: questionMetadata.layout || "default",
          picture: pictureId(questionMetadata.picture_question),
          answers: ["a", "b", "c", "d"].map(function (letter) {
            return {
              text: question["answer_" + letter] || "",
              picture: pictureId(questionMetadata["picture_" + letter])
            };
          }),
          hasSolution: Boolean(questionIndex[question.number] && questionIndex[question.number].has_solution)
        };
      });

      (section.sections || []).forEach(function (child, childIndex) {
        walk(child, sectionIndex, category.concat(childIndex));
      });
    }

    (rawCatalog.sections || []).forEach(function (section, sectionIndex) {
      walk(section, sectionIndex, []);
    });
    return questions;
  }

  window.FiftyOhmQuestions = {
    normalizeCatalog: normalizeCatalog
  };
})();
