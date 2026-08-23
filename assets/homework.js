(function () {
  "use strict";

  var COURSE_CHOICES = [
    { edition: "SWL", label: "SWL-Kurs", detail: "Kurzwellenhören", color: "#FFFFFF" },
    { edition: "N", label: "N-Kurs", detail: "N", color: "#47ABE8" },
    { edition: "NE", label: "E-Kurs", detail: "N + E", color: "#FE756C" },
    { edition: "NEA", label: "A-Kurs", detail: "N + E + A", color: "#3BB583" },
    { edition: "E", label: "Aufstockung N → E", detail: "E", color: "#FE756C" },
    { edition: "EA", label: "Aufstockung N → A", detail: "E + A", color: "#3BB583" },
    { edition: "A", label: "Aufstockung E → A", detail: "A", color: "#3BB583" }
  ];

  function renderMathSoon() {
    Vue.nextTick(function () {
      if (typeof window.renderFiftyOhmMath !== "function") return;
      window.renderFiftyOhmMath(document.getElementById("homework-generator"));
    });
  }

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    var input = document.createElement("textarea");
    input.value = text;
    input.setAttribute("readonly", "");
    input.style.position = "fixed";
    input.style.opacity = "0";
    document.body.appendChild(input);
    input.select();
    var copied = document.execCommand("copy");
    input.remove();
    return copied ? Promise.resolve() : Promise.reject(new Error("Kopieren nicht möglich"));
  }

  var app = Vue.createApp({
    setup: function () {
      var ref = Vue.ref;
      var computed = Vue.computed;
      var reactive = Vue.reactive;

      var loading = ref(true);
      var loadError = ref("");
      var step = ref(1);
      var catalog = ref({});
      var questionIndex = ref({});
      var questionsBySection = ref({});
      var selectedCourse = ref(null);
      var toc = ref(null);
      var selectedChapterIds = ref([]);
      var selectedSectionIds = ref([]);
      var questionSelection = reactive({});
      var generatedUrl = ref("");
      var copyMessage = ref("");
      var tocCache = {};

      var stepLabels = [
        { number: 1, label: "Kurs" },
        { number: 2, label: "Kapitel" },
        { number: 3, label: "Sektionen" },
        { number: 4, label: "Fragen" },
        { number: 5, label: "Link" }
      ];

      function sectionQuestionIds(section) {
        if (!selectedCourse.value) return [];
        return questionsBySection.value[selectedCourse.value.edition + ":" + section.ident] || [];
      }

      function chapterQuestionCount(chapter) {
        return chapter.sections.reduce(function (sum, section) {
          return sum + sectionQuestionIds(section).length;
        }, 0);
      }

      var selectedChapters = computed(function () {
        if (!toc.value) return [];
        return toc.value.chapters.filter(function (chapter) {
          return selectedChapterIds.value.indexOf(chapter.ident) !== -1;
        });
      });

      var selectedSectionGroups = computed(function () {
        var groups = [];
        selectedChapters.value.forEach(function (chapter) {
          chapter.sections.forEach(function (section) {
            if (selectedSectionIds.value.indexOf(section.ident) === -1) return;
            groups.push({ chapter: chapter, section: section, questionIds: sectionQuestionIds(section) });
          });
        });
        return groups;
      });

      var orderedQuestions = computed(function () {
        return selectedSectionGroups.value.reduce(function (result, group) {
          return result.concat(group.questionIds);
        }, []);
      });

      var selectedQuestionIds = computed(function () {
        return orderedQuestions.value.filter(function (questionId) { return questionSelection[questionId]; });
      });

      function buildSectionIndex() {
        var result = {};
        Object.keys(questionIndex.value).forEach(function (questionId) {
          var entry = questionIndex.value[questionId];
          (entry.editions || []).forEach(function (edition) {
            var key = edition + ":" + entry.section;
            if (!result[key]) result[key] = [];
            result[key].push(questionId);
          });
        });
        Object.keys(result).forEach(function (key) {
          result[key].sort(function (left, right) {
            return left.localeCompare(right, "de", { numeric: true });
          });
        });
        questionsBySection.value = result;
      }

      function goToStep(number) {
        step.value = number;
        copyMessage.value = "";
        if (number === 4) renderMathSoon();
        window.scrollTo({ top: 0, behavior: "smooth" });
      }

      function selectCourse(course) {
        selectedCourse.value = course;
        selectedChapterIds.value = [];
        selectedSectionIds.value = [];
        generatedUrl.value = "";
        if (tocCache[course.edition]) {
          toc.value = tocCache[course.edition];
          goToStep(2);
          return;
        }
        loading.value = true;
        fetch("assets/toc/" + course.edition + ".json")
          .then(function (response) {
            if (!response.ok) throw new Error("Inhaltsverzeichnis nicht gefunden (HTTP " + response.status + ").");
            return response.json();
          })
          .then(function (data) {
            tocCache[course.edition] = data;
            toc.value = data;
            loading.value = false;
            goToStep(2);
          })
          .catch(function (error) {
            loadError.value = error.message || "Unbekannter Ladefehler";
            loading.value = false;
          });
      }

      function openSectionSelection() {
        var preselectedSections = [];
        selectedChapters.value.forEach(function (chapter) {
          chapter.sections.forEach(function (section) {
            if (sectionQuestionIds(section).length > 0) preselectedSections.push(section.ident);
          });
        });
        selectedSectionIds.value = preselectedSections;
        goToStep(3);
      }

      function openQuestionSelection() {
        orderedQuestions.value.forEach(function (questionId) { questionSelection[questionId] = true; });
        goToStep(4);
      }

      function setAllQuestions(selected) {
        orderedQuestions.value.forEach(function (questionId) { questionSelection[questionId] = selected; });
      }

      function generateLink() {
        var url = new URL("simulation.html", window.location.href);
        url.search = "?homework=" + selectedQuestionIds.value.join("+");
        generatedUrl.value = url.toString();
        goToStep(5);
      }

      function copyLink() {
        copyText(generatedUrl.value)
          .then(function () { copyMessage.value = "Der Hausaufgabenlink wurde kopiert."; })
          .catch(function () { copyMessage.value = "Der Link konnte nicht automatisch kopiert werden. Bitte kopiere ihn aus dem Feld."; });
      }

      Promise.all([
        fetch("assets/fragenkatalog.json"),
        fetch("assets/metadata.json"),
        fetch("assets/question_index.json")
      ])
        .then(function (responses) {
          var names = ["Fragenkatalog", "Metadaten", "Fragenindex"];
          responses.forEach(function (response, index) {
            if (!response.ok) throw new Error(names[index] + " nicht gefunden (HTTP " + response.status + ").");
          });
          return Promise.all(responses.map(function (response) { return response.json(); }));
        })
        .then(function (data) {
          questionIndex.value = data[2] || {};
          catalog.value = window.FiftyOhmQuestions.normalizeCatalog(data[0], data[1] || {}, questionIndex.value);
          buildSectionIndex();
          loading.value = false;
        })
        .catch(function (error) {
          loadError.value = error.message || "Unbekannter Ladefehler";
          loading.value = false;
        });

      return {
        loading: loading,
        loadError: loadError,
        step: step,
        stepLabels: stepLabels,
        courseChoices: COURSE_CHOICES,
        catalog: catalog,
        selectedCourse: selectedCourse,
        toc: toc,
        selectedChapterIds: selectedChapterIds,
        selectedSectionIds: selectedSectionIds,
        questionSelection: questionSelection,
        selectedChapters: selectedChapters,
        selectedSectionGroups: selectedSectionGroups,
        orderedQuestions: orderedQuestions,
        selectedQuestionIds: selectedQuestionIds,
        generatedUrl: generatedUrl,
        copyMessage: copyMessage,
        sectionQuestionIds: sectionQuestionIds,
        chapterQuestionCount: chapterQuestionCount,
        goToStep: goToStep,
        selectCourse: selectCourse,
        openSectionSelection: openSectionSelection,
        openQuestionSelection: openQuestionSelection,
        setAllQuestions: setAllQuestions,
        generateLink: generateLink,
        copyLink: copyLink
      };
    }
  });

  app.mount("#homework-generator");
})();
