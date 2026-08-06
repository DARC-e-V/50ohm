(function () {
  "use strict";

  var STORAGE_KEY = "50ohm-exam-simulator-v1";
  var STORAGE_VERSION = 3;
  var QUESTION_COUNT = 25;
  var ANSWER_LABELS = ["A", "B", "C", "D"];

  var PART_DEFINITIONS = {
    B: { label: "Betriebliche Kenntnisse", minutes: 45 },
    V: { label: "Kenntnisse von Vorschriften", minutes: 45 },
    N: { label: "Technische Kenntnisse Klasse N", minutes: 45 },
    E: { label: "Technische Kenntnisse Klasse E", minutes: 45 },
    A: { label: "Technische Kenntnisse Klasse A", minutes: 60 },
    H: { label: "Hausaufgabe", minutes: null }
  };

  var EXAM_CHOICES = [
    { id: "N", group: "primary", label: "Klasse N", detail: "B + V + N", parts: ["B", "V", "N"], color: "#47ABE8" },
    { id: "E", group: "primary", label: "Klasse E", detail: "B + V + N + E", parts: ["B", "V", "N", "E"], color: "#FE756C" },
    { id: "A", group: "primary", label: "Klasse A", detail: "B + V + N + E + A", parts: ["B", "V", "N", "E", "A"], color: "#3BB583" },
    { id: "N-E", group: "upgrade", label: "N → E", detail: "Technik E", parts: ["E"], color: "#FE756C" },
    { id: "N-A", group: "upgrade", label: "N → A", detail: "Technik E + A", parts: ["E", "A"], color: "#3BB583" },
    { id: "E-A", group: "upgrade", label: "E → A", detail: "Technik A", parts: ["A"], color: "#3BB583" },
    { id: "part-B", group: "single", label: "B", detail: "Betriebliche Kenntnisse", parts: ["B"], color: "#47ABE8" },
    { id: "part-V", group: "single", label: "V", detail: "Kenntnisse von Vorschriften", parts: ["V"], color: "#47ABE8" },
    { id: "part-N", group: "single", label: "N", detail: "Technik Klasse N", parts: ["N"], color: "#47ABE8" },
    { id: "part-E", group: "single", label: "E", detail: "Technik Klasse E", parts: ["E"], color: "#FE756C" },
    { id: "part-A", group: "single", label: "A", detail: "Technik Klasse A", parts: ["A"], color: "#3BB583" }
  ];

  function queryValue(name) {
    return new URLSearchParams(window.location.search).get(name);
  }

  function parseHomeworkQuestionIds() {
    var value = queryValue("homework");
    if (!value) return [];
    var seen = new Set();
    return value.toUpperCase().split(/[\s+,]+/).filter(function (questionId) {
      if (!/^[A-Z]{2}\d{3}$/.test(questionId) || seen.has(questionId)) return false;
      seen.add(questionId);
      return true;
    });
  }

  function parseSharedResult() {
    var fields = (queryValue("result") || "").split(".");
    if (fields[0] !== "1") return null;
    if (fields[1] === "H") {
      var homeworkScore = Number(fields[2]);
      var homeworkTotal = Number(fields[3]);
      if (fields.length !== 4 || !Number.isInteger(homeworkScore) || !Number.isInteger(homeworkTotal) ||
          homeworkTotal < 1 || homeworkScore < 0 || homeworkScore > homeworkTotal) return null;
      return { kind: "homework", score: homeworkScore, total: homeworkTotal };
    }
    var choice = EXAM_CHOICES.find(function (item) { return item.id === fields[1]; });
    if (!choice || fields.length !== choice.parts.length + 2) return null;
    var scores = fields.slice(2).map(Number);
    if (scores.some(function (score) { return !Number.isInteger(score) || score < 0 || score > QUESTION_COUNT; })) return null;
    return { kind: "exam", choice: choice, scores: scores, passed: scores.every(function (score) { return score >= 19; }) };
  }

  function copyText(value) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(value);
    var input = document.createElement("textarea");
    input.value = value;
    input.setAttribute("readonly", "");
    input.style.position = "fixed";
    input.style.opacity = "0";
    document.body.appendChild(input);
    input.select();
    var copied = document.execCommand("copy");
    input.remove();
    return copied ? Promise.resolve() : Promise.reject(new Error("Kopieren nicht möglich"));
  }

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
      var altTexts = Vue.reactive({});
      var requestedAltTexts = new Set();
      var session = ref(null);
      var view = ref("exam");
      var reviewPartIndex = ref(null);
      var sharedResult = ref(null);
      var shareMessage = ref("");
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
      var singlePartChoices = computed(function () {
        return EXAM_CHOICES.filter(function (choice) { return choice.group === "single"; });
      });
      var currentChoice = computed(function () {
        if (!session.value) return null;
        if (session.value.mode === "homework") {
          return { id: "H", label: "Hausaufgabe", parts: ["H"] };
        }
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
      var isHomework = computed(function () {
        return Boolean(session.value && session.value.mode === "homework");
      });
      var currentQuestionCount = computed(function () {
        return currentPart.value ? currentPart.value.questions.length : 0;
      });
      var remainingSeconds = computed(function () {
        if (isHomework.value || !currentPart.value || currentPart.value.status !== "running") return 0;
        if (currentPart.value.paused) return currentPart.value.pausedRemainingSeconds;
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
        if (isHomework.value) return "homework";
        if (session.value.parts.some(function (part) { return part.status !== "evaluated"; })) return "incomplete";
        var failed = session.value.parts.filter(function (part) { return part.score < 19; });
        if (failed.length === 0) return "passed";
        if (failed.length === 1 && failed[0].score >= 17) return "oral";
        return "failed";
      });
      var overallAlertClass = computed(function () {
        return { homework: "alert-primary", passed: "alert-success", oral: "alert-warning", failed: "alert-danger", incomplete: "alert-danger" }[overallState.value];
      });
      var overallIcon = computed(function () {
        return { homework: "task_alt", passed: "verified", oral: "record_voice_over", failed: "cancel", incomplete: "stop_circle" }[overallState.value];
      });
      var overallTitle = computed(function () {
        return { homework: "Hausaufgabe ausgewertet", passed: "Prüfung bestanden", oral: "Mündliche Nachprüfung möglich", failed: "Prüfung nicht bestanden", incomplete: "Prüfung vorzeitig beendet" }[overallState.value];
      });
      var overallText = computed(function () {
        if (overallState.value === "homework") {
          var homeworkPart = session.value.parts[0];
          return homeworkPart.score + " von " + homeworkPart.questions.length + " Fragen wurden richtig beantwortet.";
        }
        if (overallState.value === "passed") return "Gratulation! Du hast jeden Prüfungsteil mit mindestens 19 Punkten bestanden.";
        if (overallState.value === "oral") return "In genau einem Prüfungsteil wurden 17 oder 18 Punkte erreicht; nach den Prüfungsregeln kann eine mündliche Nachprüfung möglich sein.";
        if (overallState.value === "failed") return "Mindestens ein Prüfungsteil wurde nicht bestanden.";
        return evaluatedParts().length + " von " + session.value.parts.length + " Prüfungsteilen wurden abgeschlossen.";
      });

      function questionData(questionState) {
        return catalog.value[questionState.id];
      }

      function padNumber(number) {
        return String(number).padStart(2, "0");
      }

      function displayQuestionNumber(questionState, questionIndex) {
        return isHomework.value ? questionState.id : padNumber(questionIndex + 1);
      }

      function pictureAlt(picture, fallback) {
        return altTexts[picture] || fallback;
      }

      function loadAltText(picture) {
        if (!picture || requestedAltTexts.has(picture)) return;
        requestedAltTexts.add(picture);
        fetch("pictures/" + encodeURIComponent(picture) + ".txt")
          .then(function (response) {
            if (!response.ok) return "";
            return response.text();
          })
          .then(function (description) {
            if (description && description.trim()) altTexts[picture] = description.trim();
          })
          .catch(function () { /* the generic alternative text remains available */ });
      }

      function loadPartAltTexts(part) {
        if (!part) return;
        part.questions.forEach(function (questionState) {
          var question = questionData(questionState);
          if (!question) return;
          loadAltText(question.picture);
          question.answers.forEach(function (answer) { loadAltText(answer.picture); });
        });
      }

      function createPart(code) {
        var picked = balancedSample(Object.values(catalog.value).filter(function (question) {
          return question.part === code;
        }), QUESTION_COUNT);
        return {
          code: code,
          status: "pending",
          deadline: null,
          paused: false,
          pausedRemainingSeconds: null,
          score: null,
          autoSubmitted: false,
          questions: picked.map(function (question) {
            return { id: question.id, order: shuffled([0, 1, 2, 3]), selected: null, history: [] };
          })
        };
      }

      function createHomeworkPart(questionIds) {
        var questions = questionIds.map(function (questionId) { return catalog.value[questionId]; }).filter(Boolean);
        if (questions.length !== questionIds.length) {
          throw new Error("Mindestens eine Frage aus dem Hausaufgabenlink ist nicht im aktuellen Fragenkatalog enthalten.");
        }
        if (questions.length === 0) throw new Error("Der Hausaufgabenlink enthält keine gültigen Fragen.");
        return {
          code: "H",
          status: "pending",
          deadline: null,
          paused: false,
          pausedRemainingSeconds: null,
          score: null,
          autoSubmitted: false,
          questions: questions.map(function (question) {
            return { id: question.id, order: shuffled([0, 1, 2, 3]), selected: null, history: [] };
          })
        };
      }

      function activatePart(part) {
        part.status = "running";
        part.deadline = part.code === "H" ? null : Date.now() + PART_DEFINITIONS[part.code].minutes * 60 * 1000;
        part.paused = false;
        part.pausedRemainingSeconds = null;
        now.value = Date.now();
      }

      function toggleTimer() {
        var part = currentPart.value;
        if (isHomework.value || !part || part.status !== "running") return;
        if (part.paused) {
          part.deadline = Date.now() + part.pausedRemainingSeconds * 1000;
          part.pausedRemainingSeconds = null;
          part.paused = false;
          now.value = Date.now();
          return;
        }

        var seconds = remainingSeconds.value;
        if (seconds <= 0) {
          submitPart(true);
          return;
        }
        part.pausedRemainingSeconds = seconds;
        part.paused = true;
        part.deadline = null;
      }

      function startExam(choice) {
        try {
          var parts = choice.parts.map(createPart);
          activatePart(parts[0]);
          session.value = {
            version: STORAGE_VERSION,
            mode: "exam",
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

      function startHomework(questionIds) {
        try {
          var part = createHomeworkPart(questionIds);
          activatePart(part);
          session.value = {
            version: STORAGE_VERSION,
            mode: "homework",
            choiceId: "H",
            homeworkIds: questionIds.slice(),
            currentPart: 0,
            startedAt: Date.now(),
            parts: [part]
          };
          view.value = "exam";
          reviewPartIndex.value = null;
          renderMathSoon(Vue);
        } catch (error) {
          loadError.value = error.message;
        }
      }

      function selectAnswer(questionIndex, answerIndex) {
        if (currentPart.value.status !== "running" || currentPart.value.paused) return;
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
        if (currentPart.value.status === "running") return "";
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
        currentPart.value.paused = false;
        currentPart.value.pausedRemainingSeconds = null;
        currentPart.value.autoSubmitted = Boolean(autoSubmitted);
        renderMathSoon(Vue);
        window.scrollTo({ top: 0, behavior: "smooth" });
      }

      function requestSubmit() {
        var unanswered = currentQuestionCount.value - answeredCount.value;
        var text = unanswered > 0
          ? "Du hast " + unanswered + " Fragen nicht beantwortet. Möchtest du " + (isHomework.value ? "die Hausaufgabe" : "den Prüfungsteil") + " trotzdem abgeben?"
          : "Möchtest du " + (isHomework.value ? "die Hausaufgabe" : "diesen Prüfungsteil") + " jetzt verbindlich abgeben?";
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
        if (completedResultUrl.value) {
          var target = new URL(completedResultUrl.value);
          if (window.location.pathname !== target.pathname || window.location.search !== target.search) {
            window.location.assign(target.toString());
          }
        }
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

      function resetExam() {
        clearStoredSession();
        session.value = null;
        view.value = "exam";
        reviewPartIndex.value = null;
        sharedResult.value = null;
        shareMessage.value = "";
        window.scrollTo({ top: 0, behavior: "smooth" });
      }

      function abortExam() {
        var noun = isHomework.value ? "Hausaufgabe" : "Simulation";
        if (!window.confirm("Möchtest du diese " + noun + " abbrechen? Der gespeicherte Stand wird gelöscht.")) return;
        resetExam();
        window.history.replaceState(null, "", "simulation.html");
      }

      function newExam() {
        resetExam();
        window.history.replaceState(null, "", "simulation.html");
      }

      function retryHomework() {
        var questionIds = session.value && session.value.homeworkIds;
        if (!questionIds) return;
        clearStoredSession();
        var homeworkUrl = new URL("simulation.html", window.location.href);
        homeworkUrl.search = "?homework=" + questionIds.join("+");
        window.history.replaceState(null, "", homeworkUrl.toString());
        startHomework(questionIds);
        window.scrollTo({ top: 0, behavior: "smooth" });
      }

      function scrollToQuestion(index) {
        var element = document.getElementById("exam-question-" + index);
        if (element) element.scrollIntoView({ behavior: "smooth", block: "start" });
      }

      function resultLabel(part) {
        if (part.code === "H") return "Ausgewertet";
        if (part.score >= 19) return "Bestanden";
        if (part.score >= 17) return "Nachprüfung möglich";
        return "Nicht bestanden";
      }

      function resultAlertClass(part) {
        if (part.code === "H") return "alert-primary";
        if (part.score >= 19) return "alert-success";
        if (part.score >= 17) return "alert-warning";
        return "alert-danger";
      }

      function resultBadgeClass(part) {
        if (part.code === "H") return "text-bg-primary";
        if (part.score >= 19) return "text-bg-success";
        if (part.score >= 17) return "text-bg-warning";
        return "text-bg-danger";
      }

      function resultIcon(part) {
        if (part.code === "H") return "task_alt";
        if (part.score >= 19) return "check_circle";
        if (part.score >= 17) return "record_voice_over";
        return "cancel";
      }

      function resultDescription(part) {
        if (part.code === "H") return part.score + " von " + part.questions.length + " Fragen wurden richtig beantwortet.";
        var prefix = part.autoSubmitted ? "Die Zeit ist abgelaufen und der Prüfungsteil wurde automatisch abgegeben. " : "";
        if (part.score >= 19) return prefix + "Die erforderlichen 19 Punkte wurden erreicht.";
        if (part.score >= 17) return prefix + "Mit 17 oder 18 Punkten kann nach den Prüfungsregeln eine mündliche Nachprüfung möglich sein.";
        return prefix + "Die erforderlichen 19 Punkte wurden nicht erreicht.";
      }

      function encodedResult(result) {
        if (result.kind === "homework") return "1.H." + result.score + "." + result.total;
        return "1." + result.choice.id + "." + result.scores.join(".");
      }

      function resultImageCode(result) {
        if (!result) return "";
        if (result.kind === "homework") return result.score === result.total ? "aenbv" : "";
        if (!result.passed) return "";
        var order = ["A", "E", "N", "B", "V"];
        return order.filter(function (part) {
          return result.choice.parts.indexOf(part) !== -1;
        }).join("").toLowerCase();
      }

      function shareableSessionResult() {
        if (!session.value) return null;
        if (isHomework.value) {
          return { kind: "homework", score: session.value.parts[0].score, total: session.value.parts[0].questions.length };
        }
        if (session.value.parts.some(function (part) { return part.status !== "evaluated"; })) return null;
        return {
          kind: "exam",
          choice: currentChoice.value,
          scores: session.value.parts.map(function (part) { return part.score; }),
          passed: overallState.value === "passed"
        };
      }

      var resultForSharing = computed(function () {
        if (sharedResult.value) return sharedResult.value;
        if (view.value !== "summary") return null;
        return shareableSessionResult();
      });

      function buildResultUrl(result) {
        if (!result) return "";
        var imageCode = resultImageCode(result);
        var url = new URL(imageCode ? "result-" + imageCode + ".html" : "result.html", window.location.href);
        url.search = "?result=" + encodedResult(result);
        return url.toString();
      }

      var completedResultUrl = computed(function () {
        return buildResultUrl(shareableSessionResult());
      });

      var resultShareUrl = computed(function () {
        return buildResultUrl(resultForSharing.value);
      });

      var resultImageUrl = computed(function () {
        var imageCode = resultImageCode(resultForSharing.value);
        return imageCode ? "assets/images/exam-" + imageCode + ".jpeg" : "";
      });

      var shareText = computed(function () {
        var result = resultForSharing.value;
        if (!result) return "";
        if (result.kind === "homework") {
          return "Meine 50ohm.de-Hausaufgabe: " + result.score + " von " + result.total + " Fragen richtig.";
        }
        var scores = result.choice.parts.map(function (part, index) { return part + ": " + result.scores[index] + "/25"; }).join(", ");
        return "Meine 50ohm.de-Prüfungssimulation " + result.choice.label + ": " + scores + " – " + (result.passed ? "bestanden!" : "noch nicht bestanden.");
      });

      var socialShareLinks = computed(function () {
        var textWithUrl = shareText.value + " " + resultShareUrl.value;
        return {
          mastodon: "https://share.joinmastodon.org/#text=" + encodeURIComponent(textWithUrl),
          bluesky: "https://bsky.app/intent/compose?text=" + encodeURIComponent(textWithUrl),
          facebook: "https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(resultShareUrl.value),
          x: "https://x.com/intent/tweet?text=" + encodeURIComponent(textWithUrl)
        };
      });

      function copyResultLink() {
        copyText(resultShareUrl.value)
          .then(function () { shareMessage.value = "Ergebnislink kopiert."; })
          .catch(function () { shareMessage.value = "Der Link konnte nicht automatisch kopiert werden."; });
      }

      function shareNative() {
        if (!navigator.share) {
          copyResultLink();
          return;
        }
        navigator.share({ title: "50ohm.de-Ergebnis", text: shareText.value, url: resultShareUrl.value }).catch(function () {});
      }

      function restoreSession(homeworkQuestionIds, allowHomeworkResult) {
        try {
          var raw = window.localStorage.getItem(STORAGE_KEY);
          if (!raw) return;
          var stored = JSON.parse(raw);
          if (!stored || stored.version !== STORAGE_VERSION || !stored.session) {
            clearStoredSession();
            return;
          }
          var homeworkMode = stored.session.mode === "homework";
          var choice = EXAM_CHOICES.find(function (item) { return item.id === stored.session.choiceId; });
          var homeworkMatches = homeworkMode && (allowHomeworkResult || (homeworkQuestionIds.length > 0 &&
            JSON.stringify(stored.session.homeworkIds) === JSON.stringify(homeworkQuestionIds)));
          var valid = (homeworkMatches || choice) && stored.session.parts.every(function (part) {
            return Array.isArray(part.questions) && (homeworkMode || part.questions.length === QUESTION_COUNT) && part.questions.every(function (question) {
              return Boolean(catalog.value[question.id]);
            });
          });
          if (!valid) {
            clearStoredSession();
            return;
          }
          stored.session.parts.forEach(function (part) {
            part.paused = Boolean(part.paused);
            if (!part.paused) part.pausedRemainingSeconds = null;
          });
          session.value = stored.session;
          if (!session.value.mode) session.value.mode = "exam";
          view.value = stored.view === "summary" ? "summary" : "exam";
          if (session.value.parts[session.value.currentPart].status === "running" &&
              !session.value.parts[session.value.currentPart].paused &&
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

      watch(currentPart, function (part) {
        loadPartAltTexts(part);
      });

      watch(remainingSeconds, function (seconds) {
        if (!isHomework.value && session.value && currentPart.value && currentPart.value.status === "running" &&
            !currentPart.value.paused && seconds <= 0) submitPart(true);
      });

      function loadCatalog() {
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
            catalog.value = window.FiftyOhmQuestions.normalizeCatalog(data[0], data[1] || {}, data[2] || {});
            if (Object.keys(catalog.value).length === 0) throw new Error("Der Fragenkatalog ist leer.");
            var parsedResult = parseSharedResult();
            var homeworkQuestionIds = parseHomeworkQuestionIds();
            if (queryValue("result")) {
              if (!parsedResult) throw new Error("Der Ergebnislink ist ungültig.");
              restoreSession([], true);
              var storedResult = shareableSessionResult();
              if (storedResult && encodedResult(storedResult) === queryValue("result")) {
                sharedResult.value = null;
                view.value = "summary";
              } else {
                session.value = null;
                sharedResult.value = parsedResult;
                view.value = "shared";
              }
            } else {
              restoreSession(homeworkQuestionIds);
              if (homeworkQuestionIds.length > 0 && !session.value) startHomework(homeworkQuestionIds);
            }
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
        sharedResult: sharedResult,
        shareMessage: shareMessage,
        primaryChoices: primaryChoices,
        upgradeChoices: upgradeChoices,
        singlePartChoices: singlePartChoices,
        currentChoice: currentChoice,
        currentPart: currentPart,
        currentPartDefinition: currentPartDefinition,
        isHomework: isHomework,
        currentQuestionCount: currentQuestionCount,
        displayedPartIndex: displayedPartIndex,
        partDefinitions: PART_DEFINITIONS,
        answerLabels: ANSWER_LABELS,
        remainingSeconds: remainingSeconds,
        formattedTime: formattedTime,
        toggleTimer: toggleTimer,
        answeredCount: answeredCount,
        hasNextPart: hasNextPart,
        isReviewing: isReviewing,
        overallAlertClass: overallAlertClass,
        overallState: overallState,
        overallIcon: overallIcon,
        overallTitle: overallTitle,
        overallText: overallText,
        padNumber: padNumber,
        displayQuestionNumber: displayQuestionNumber,
        pictureAlt: pictureAlt,
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
        retryHomework: retryHomework,
        scrollToQuestion: scrollToQuestion,
        resultLabel: resultLabel,
        resultAlertClass: resultAlertClass,
        resultBadgeClass: resultBadgeClass,
        resultIcon: resultIcon,
        resultDescription: resultDescription,
        resultForSharing: resultForSharing,
        completedResultUrl: completedResultUrl,
        resultShareUrl: resultShareUrl,
        resultImageUrl: resultImageUrl,
        shareText: shareText,
        socialShareLinks: socialShareLinks,
        copyResultLink: copyResultLink,
        shareNative: shareNative
      };
    }
  });

  app.mount("#exam-simulator");
})();
