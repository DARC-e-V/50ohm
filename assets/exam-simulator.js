(function () {
  "use strict";

  var STORAGE_KEY = "50ohm-exam-simulator-v1";
  var STORAGE_VERSION = 3;
  var QUESTION_COUNT = 25;
  var ANSWER_LABELS = ["A", "B", "C", "D"];

  var PART_DEFINITIONS = {
    B: { label: "Betriebliche Kenntnisse", formLabel: "Betriebliche Kenntnisse", minutes: 45 },
    V: { label: "Kenntnisse von Vorschriften", formLabel: "Kenntnisse von Vorschriften", minutes: 45 },
    N: { label: "Technische Kenntnisse Klasse N", formLabel: "Technische Kenntnisse Klasse N", minutes: 45 },
    E: { label: "Technische Kenntnisse Klasse E", formLabel: "Technische Kenntnisse Klasse E", minutes: 45 },
    A: { label: "Technische Kenntnisse Klasse A", formLabel: "Technische Kenntnisse Klasse A", minutes: 60 }
  };

  var EXAM_CHOICES = [
    { id: "N", group: "primary", shortLabel: "N", label: "Prüfung Klasse N", parts: ["B", "V", "N"], color: "#47ABE8" },
    { id: "E", group: "primary", shortLabel: "N + E", label: "Prüfung Klasse E", parts: ["B", "V", "N", "E"], color: "#FE756C" },
    { id: "A", group: "primary", shortLabel: "N + E + A", label: "Prüfung Klasse A", parts: ["B", "V", "N", "E", "A"], color: "#3BB583" },
    { id: "N-E", group: "upgrade", shortLabel: "N → E", label: "Aufstockung von N auf E", parts: ["E"], color: "#FE756C" },
    { id: "E-A", group: "upgrade", shortLabel: "E → A", label: "Aufstockung von E auf A", parts: ["A"], color: "#3BB583" },
    { id: "N-A", group: "upgrade", shortLabel: "N → A", label: "Aufstockung von N auf A", parts: ["E", "A"], color: "#3BB583" }
  ];

  function shuffled(values) {
    var result = values.slice();
    for (var i = result.length - 1; i > 0; i -= 1) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = result[i];
      result[i] = result[j];
      result[j] = tmp;
    }
    return result;
  }

  function buildCategoryTree(pool) {
    var root = { children: new Map(), items: [], size: 0 };
    pool.forEach(function (item) {
      var node = root;
      node.size += 1;
      (item.category || []).forEach(function (categoryPart) {
        if (!node.children.has(categoryPart)) {
          node.children.set(categoryPart, { children: new Map(), items: [], size: 0 });
        }
        node = node.children.get(categoryPart);
        node.size += 1;
      });
      node.items.push(item);
    });
    return root;
  }

  function allocateQuotas(children, quota, totalSize) {
    var allocations = children.map(function (child) {
      var target = quota * child.size / totalSize;
      return { child: child, quota: Math.floor(target), fraction: target - Math.floor(target) };
    });
    var assigned = allocations.reduce(function (sum, allocation) { return sum + allocation.quota; }, 0);

    while (assigned < quota) {
      var candidates = allocations.filter(function (allocation) {
        return allocation.quota < allocation.child.size;
      });
      var weight = candidates.reduce(function (sum, allocation) { return sum + allocation.fraction; }, 0);
      var selected;
      if (weight <= 0) {
        selected = candidates[Math.floor(Math.random() * candidates.length)];
      } else {
        var draw = Math.random() * weight;
        selected = candidates[candidates.length - 1];
        for (var i = 0; i < candidates.length; i += 1) {
          draw -= candidates[i].fraction;
          if (draw <= 0) {
            selected = candidates[i];
            break;
          }
        }
      }
      selected.quota += 1;
      selected.fraction = 0;
      assigned += 1;
    }
    return allocations;
  }

  function pickFromTree(node, quota) {
    if (quota <= 0) return [];
    if (node.children.size === 0) return shuffled(node.items).slice(0, quota);
    var allocations = allocateQuotas(Array.from(node.children.values()), quota, node.size);
    var result = [];
    allocations.forEach(function (allocation) {
      result = result.concat(pickFromTree(allocation.child, allocation.quota));
    });
    return shuffled(result);
  }

  function balancedSample(pool, count) {
    if (!Array.isArray(pool) || pool.length < count) {
      throw new Error("Für diesen Prüfungsteil stehen nicht genügend Fragen zur Verfügung.");
    }
    return pickFromTree(buildCategoryTree(pool), count);
  }

  function renderMathSoon(VueApi) {
    VueApi.nextTick(function () {
      if (typeof window.renderFiftyOhmMath !== "function") return;
      window.renderFiftyOhmMath(document.getElementById("exam-simulator"));
    });
  }

  var app = Vue.createApp({
    setup: function () {
      var ref = Vue.ref;
      var computed = Vue.computed;
      var watch = Vue.watch;
      var onMounted = Vue.onMounted;
      var onBeforeUnmount = Vue.onBeforeUnmount;

      var loading = ref(true);
      var loadError = ref("");
      var catalog = ref({});
      var session = ref(null);
      var view = ref("exam");
      var reviewPartIndex = ref(null);
      var now = ref(Date.now());
      var timerId = null;
      var catalogLoadHandler = null;
      var headerObserver = null;

      var primaryChoices = computed(function () {
        return EXAM_CHOICES.filter(function (choice) { return choice.group === "primary"; });
      });
      var upgradeChoices = computed(function () {
        return EXAM_CHOICES.filter(function (choice) { return choice.group === "upgrade"; });
      });
      var currentChoice = computed(function () {
        if (!session.value) return null;
        return EXAM_CHOICES.find(function (choice) { return choice.id === session.value.choiceId; });
      });
      var displayedPartIndex = computed(function () {
        return reviewPartIndex.value === null ? session.value.currentPart : reviewPartIndex.value;
      });
      var currentPart = computed(function () {
        if (!session.value) return null;
        return session.value.parts[displayedPartIndex.value];
      });
      var currentPartDefinition = computed(function () {
        if (!currentPart.value) return null;
        return PART_DEFINITIONS[currentPart.value.code];
      });
      var remainingSeconds = computed(function () {
        if (!currentPart.value || currentPart.value.status !== "running") return 0;
        return Math.max(0, Math.ceil((currentPart.value.deadline - now.value) / 1000));
      });
      var formattedTime = computed(function () {
        var minutes = Math.floor(remainingSeconds.value / 60);
        var seconds = remainingSeconds.value % 60;
        return String(minutes).padStart(2, "0") + ":" + String(seconds).padStart(2, "0");
      });
      var answeredCount = computed(function () {
        if (!currentPart.value) return 0;
        return currentPart.value.questions.filter(function (question) { return question.selected !== null; }).length;
      });
      var hasNextPart = computed(function () {
        if (!session.value) return false;
        return session.value.currentPart < session.value.parts.length - 1;
      });
      var isReviewing = computed(function () { return reviewPartIndex.value !== null; });

      function evaluatedParts() {
        return session.value.parts.filter(function (part) { return part.status === "evaluated"; });
      }

      var overallState = computed(function () {
        if (session.value.parts.some(function (part) { return part.status !== "evaluated"; })) return "incomplete";
        var failed = session.value.parts.filter(function (part) { return part.score < 19; });
        if (failed.length === 0) return "passed";
        if (failed.length === 1 && failed[0].score >= 17) return "oral";
        return "failed";
      });
      var overallAlertClass = computed(function () {
        return { passed: "alert-success", oral: "alert-warning", failed: "alert-danger", incomplete: "alert-danger" }[overallState.value];
      });
      var overallIcon = computed(function () {
        return { passed: "verified", oral: "record_voice_over", failed: "cancel", incomplete: "stop_circle" }[overallState.value];
      });
      var overallTitle = computed(function () {
        return { passed: "Prüfung bestanden", oral: "Mündliche Nachprüfung möglich", failed: "Prüfung nicht bestanden", incomplete: "Prüfung vorzeitig beendet" }[overallState.value];
      });
      var overallText = computed(function () {
        if (overallState.value === "passed") return "Du hast jeden Prüfungsteil mit mindestens 19 Punkten bestanden.";
        if (overallState.value === "oral") return "In genau einem Prüfungsteil wurden 17 oder 18 Punkte erreicht; nach den Prüfungsregeln kann eine mündliche Nachprüfung möglich sein.";
        if (overallState.value === "failed") return "Mindestens ein Prüfungsteil wurde nicht bestanden.";
        return evaluatedParts().length + " von " + session.value.parts.length + " Prüfungsteilen wurden abgeschlossen.";
      });

      function questionData(questionState) {
        return catalog.value[questionState.id];
      }

      function partSummary(parts) {
        return parts.join(" + ");
      }

      function padNumber(number) {
        return String(number).padStart(2, "0");
      }

      function createPart(code) {
        var picked = balancedSample(Object.values(catalog.value).filter(function (question) {
          return question.part === code;
        }), QUESTION_COUNT);
        return {
          code: code,
          status: "pending",
          deadline: null,
          score: null,
          autoSubmitted: false,
          questions: picked.map(function (question) {
            return { id: question.id, order: shuffled([0, 1, 2, 3]), selected: null, history: [] };
          })
        };
      }

      function activatePart(part) {
        part.status = "running";
        part.deadline = Date.now() + PART_DEFINITIONS[part.code].minutes * 60 * 1000;
        now.value = Date.now();
      }

      function startExam(choice) {
        try {
          var parts = choice.parts.map(createPart);
          activatePart(parts[0]);
          session.value = {
            version: STORAGE_VERSION,
            choiceId: choice.id,
            currentPart: 0,
            startedAt: Date.now(),
            parts: parts
          };
          view.value = "exam";
          reviewPartIndex.value = null;
          renderMathSoon(Vue);
        } catch (error) {
          loadError.value = error.message;
        }
      }

      function selectAnswer(questionIndex, answerIndex) {
        if (currentPart.value.status !== "running") return;
        var question = currentPart.value.questions[questionIndex];
        if (question.selected === answerIndex) return;
        var firstAnswer = question.selected === null;
        question.selected = answerIndex;
        question.history.push(answerIndex);
        if (firstAnswer && questionIndex < currentPart.value.questions.length - 1) {
          window.setTimeout(function () { scrollToQuestion(questionIndex + 1); }, 150);
        }
      }

      function answerMark(questionIndex, answerIndex) {
        var question = currentPart.value.questions[questionIndex];
        if (question.selected === answerIndex) {
          var restored = question.history.slice(0, -1).indexOf(answerIndex) !== -1;
          return '<span class="answer-mark-symbol' + (restored ? " answer-mark-restored" : "") + '">×</span>';
        }
        if (question.history.indexOf(answerIndex) !== -1) {
          return '<span class="answer-mark-symbol">=</span>';
        }
        return "";
      }

      function answerCellClass(questionIndex, answerIndex) {
        if (currentPart.value.status !== "evaluated") return "";
        var question = currentPart.value.questions[questionIndex];
        var sourceIndex = question.order[answerIndex];
        if (question.selected === answerIndex && sourceIndex === 0) return "answer-cell-correct";
        if (question.selected === answerIndex) return "answer-cell-wrong";
        if (sourceIndex === 0) return "answer-cell-solution";
        return "";
      }

      function questionAnswerClass(questionIndex, answerIndex) {
        var question = currentPart.value.questions[questionIndex];
        if (currentPart.value.status === "running") {
          return question.selected === answerIndex ? "exam-answer-selected" : "";
        }
        var sourceIndex = question.order[answerIndex];
        if (sourceIndex === 0) return "correct";
        if (question.selected === answerIndex) return "wrong";
        return "";
      }

      function submitPart(autoSubmitted) {
        if (!session.value || currentPart.value.status !== "running") return;
        var score = currentPart.value.questions.reduce(function (sum, question) {
          return sum + (question.selected !== null && question.order[question.selected] === 0 ? 1 : 0);
        }, 0);
        currentPart.value.score = score;
        currentPart.value.status = "evaluated";
        currentPart.value.deadline = null;
        currentPart.value.autoSubmitted = Boolean(autoSubmitted);
        renderMathSoon(Vue);
        window.scrollTo({ top: 0, behavior: "smooth" });
      }

      function requestSubmit() {
        var unanswered = QUESTION_COUNT - answeredCount.value;
        var text = unanswered > 0
          ? "Du hast " + unanswered + " Fragen nicht beantwortet. Möchtest du den Prüfungsteil trotzdem abgeben?"
          : "Möchtest du diesen Prüfungsteil jetzt verbindlich abgeben?";
        if (window.confirm(text)) submitPart(false);
      }

      function startNextPart() {
        var nextIndex = session.value.currentPart + 1;
        var nextPart = session.value.parts[nextIndex];
        if (!nextPart) {
          showSummary();
          return;
        }
        session.value.currentPart = nextIndex;
        reviewPartIndex.value = null;
        view.value = "exam";
        activatePart(nextPart);
        renderMathSoon(Vue);
        window.scrollTo({ top: 0, behavior: "smooth" });
      }

      function finishExamEarly() {
        if (!window.confirm("Möchtest du die Prüfung wirklich hier beenden? Nicht bearbeitete Teile gelten dann als nicht abgeschlossen.")) return;
        showSummary();
      }

      function showSummary() {
        reviewPartIndex.value = null;
        view.value = "summary";
        window.scrollTo({ top: 0, behavior: "smooth" });
      }

      function reviewPart(index) {
        reviewPartIndex.value = index;
        view.value = "exam";
        renderMathSoon(Vue);
        window.scrollTo({ top: 0, behavior: "smooth" });
      }

      function clearStoredSession() {
        try { window.localStorage.removeItem(STORAGE_KEY); } catch (error) { /* storage can be unavailable */ }
      }

      function abortExam() {
        if (!window.confirm("Möchtest du diese Simulation abbrechen? Der gespeicherte Prüfungsstand wird gelöscht.")) return;
        clearStoredSession();
        session.value = null;
        view.value = "exam";
        reviewPartIndex.value = null;
        window.scrollTo({ top: 0, behavior: "smooth" });
      }

      function newExam() {
        clearStoredSession();
        session.value = null;
        view.value = "exam";
        reviewPartIndex.value = null;
        window.scrollTo({ top: 0, behavior: "smooth" });
      }

      function scrollToQuestion(index) {
        var element = document.getElementById("exam-question-" + index);
        if (element) element.scrollIntoView({ behavior: "smooth", block: "start" });
      }

      function resultLabel(part) {
        if (part.score >= 19) return "Bestanden";
        if (part.score >= 17) return "Nachprüfung möglich";
        return "Nicht bestanden";
      }

      function resultAlertClass(part) {
        if (part.score >= 19) return "alert-success";
        if (part.score >= 17) return "alert-warning";
        return "alert-danger";
      }

      function resultBadgeClass(part) {
        if (part.score >= 19) return "text-bg-success";
        if (part.score >= 17) return "text-bg-warning";
        return "text-bg-danger";
      }

      function resultIcon(part) {
        if (part.score >= 19) return "check_circle";
        if (part.score >= 17) return "record_voice_over";
        return "cancel";
      }

      function resultDescription(part) {
        var prefix = part.autoSubmitted ? "Die Zeit ist abgelaufen und der Prüfungsteil wurde automatisch abgegeben. " : "";
        if (part.score >= 19) return prefix + "Die erforderlichen 19 Punkte wurden erreicht.";
        if (part.score >= 17) return prefix + "Mit 17 oder 18 Punkten kann nach den Prüfungsregeln eine mündliche Nachprüfung möglich sein.";
        return prefix + "Die erforderlichen 19 Punkte wurden nicht erreicht.";
      }

      function restoreSession() {
        try {
          var raw = window.localStorage.getItem(STORAGE_KEY);
          if (!raw) return;
          var stored = JSON.parse(raw);
          if (!stored || stored.version !== STORAGE_VERSION || !stored.session) {
            clearStoredSession();
            return;
          }
          var choice = EXAM_CHOICES.find(function (item) { return item.id === stored.session.choiceId; });
          var valid = choice && stored.session.parts.every(function (part) {
            return Array.isArray(part.questions) && part.questions.length === QUESTION_COUNT && part.questions.every(function (question) {
              return Boolean(catalog.value[question.id]);
            });
          });
          if (!valid) {
            clearStoredSession();
            return;
          }
          session.value = stored.session;
          view.value = stored.view === "summary" ? "summary" : "exam";
          if (session.value.parts[session.value.currentPart].status === "running" &&
              session.value.parts[session.value.currentPart].deadline <= Date.now()) {
            submitPart(true);
          }
        } catch (error) {
          clearStoredSession();
        }
      }

      watch([session, view], function () {
        if (!session.value) return;
        try {
          window.localStorage.setItem(STORAGE_KEY, JSON.stringify({
            version: STORAGE_VERSION,
            session: session.value,
            view: view.value
          }));
        } catch (error) { /* simulator remains usable without persistence */ }
      }, { deep: true });

      watch(remainingSeconds, function (seconds) {
        if (session.value && currentPart.value && currentPart.value.status === "running" && seconds <= 0) submitPart(true);
      });

      function loadCatalog() {
        fetch("assets/exam-questions.json")
          .then(function (response) {
            if (!response.ok) throw new Error("Fragenkatalog nicht gefunden (HTTP " + response.status + ").");
            return response.json();
          })
          .then(function (data) {
            catalog.value = data.questions || {};
            if (Object.keys(catalog.value).length === 0) throw new Error("Der Fragenkatalog ist leer.");
            restoreSession();
            loading.value = false;
            renderMathSoon(Vue);
          })
          .catch(function (error) {
            loadError.value = error.message || "Unbekannter Ladefehler";
            loading.value = false;
          });
      }

      function updateHeaderHeight() {
        var header = document.querySelector(".fiftyohm-layout-outer-head");
        if (!header) return;
        document.documentElement.style.setProperty("--exam-header-height", header.offsetHeight + "px");
      }

      onMounted(function () {
        document.body.classList.add("exam-simulator-page");
        updateHeaderHeight();
        if (typeof window.ResizeObserver === "function") {
          headerObserver = new window.ResizeObserver(updateHeaderHeight);
          headerObserver.observe(document.querySelector(".fiftyohm-layout-outer-head"));
        }
        if (document.readyState === "loading") {
          catalogLoadHandler = function () { window.setTimeout(loadCatalog, 0); };
          document.addEventListener("DOMContentLoaded", catalogLoadHandler, { once: true });
        } else {
          loadCatalog();
        }
        timerId = window.setInterval(function () { now.value = Date.now(); }, 1000);
      });

      onBeforeUnmount(function () {
        if (timerId !== null) window.clearInterval(timerId);
        if (catalogLoadHandler !== null) document.removeEventListener("DOMContentLoaded", catalogLoadHandler);
        if (headerObserver !== null) headerObserver.disconnect();
        document.documentElement.style.removeProperty("--exam-header-height");
        document.body.classList.remove("exam-simulator-page");
      });

      return {
        loading: loading,
        loadError: loadError,
        session: session,
        view: view,
        primaryChoices: primaryChoices,
        upgradeChoices: upgradeChoices,
        currentChoice: currentChoice,
        currentPart: currentPart,
        currentPartDefinition: currentPartDefinition,
        displayedPartIndex: displayedPartIndex,
        partDefinitions: PART_DEFINITIONS,
        answerLabels: ANSWER_LABELS,
        remainingSeconds: remainingSeconds,
        formattedTime: formattedTime,
        answeredCount: answeredCount,
        hasNextPart: hasNextPart,
        isReviewing: isReviewing,
        overallAlertClass: overallAlertClass,
        overallIcon: overallIcon,
        overallTitle: overallTitle,
        overallText: overallText,
        partSummary: partSummary,
        padNumber: padNumber,
        questionData: questionData,
        startExam: startExam,
        selectAnswer: selectAnswer,
        answerMark: answerMark,
        answerCellClass: answerCellClass,
        questionAnswerClass: questionAnswerClass,
        requestSubmit: requestSubmit,
        startNextPart: startNextPart,
        finishExamEarly: finishExamEarly,
        showSummary: showSummary,
        reviewPart: reviewPart,
        abortExam: abortExam,
        newExam: newExam,
        scrollToQuestion: scrollToQuestion,
        resultLabel: resultLabel,
        resultAlertClass: resultAlertClass,
        resultBadgeClass: resultBadgeClass,
        resultIcon: resultIcon,
        resultDescription: resultDescription
      };
    }
  });

  app.mount("#exam-simulator");
})();
