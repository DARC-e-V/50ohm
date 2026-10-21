document.querySelectorAll("[data-feedback-link]").forEach((link) => {
  const url = new URL(link.dataset.feedbackBase, window.location.href);
  url.searchParams.set("release_id", link.dataset.releaseId);
  url.searchParams.set("lang", link.dataset.lang);
  url.searchParams.set("page", window.location.pathname + window.location.search + window.location.hash);
  link.href = url.toString();
});
