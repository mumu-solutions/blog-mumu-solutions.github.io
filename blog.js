// Theme + language toggle. No inline <script> anywhere in the generated
// pages (see .specify/adr/0003-external-css-js-bare-csp.md), so this file
// is the only script the CSP has to name, once, for the whole site.
(function () {
  "use strict";

  var root = document.documentElement;

  function apply(key, value, attr) {
    root.setAttribute(attr, value);
    try { localStorage.setItem(key, value); } catch (e) {}
  }

  function stored(key) {
    try { return localStorage.getItem(key); } catch (e) { return null; }
  }

  // theme -------------------------------------------------------------
  var savedTheme = stored("mumu-blog-theme");
  if (savedTheme) root.setAttribute("data-theme", savedTheme);

  var themeBtn = document.getElementById("themeBtn");
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "light" ? "dark" : "light";
      apply("mumu-blog-theme", next, "data-theme");
    });
  }

  // language ------------------------------------------------------------
  // Server renders PT as .on already, so no-JS visitors get PT. This only
  // ever moves .on between the pt/en siblings that already exist in the
  // markup — it never injects content.
  function setLang(lang) {
    document.querySelectorAll("[data-lang]").forEach(function (el) {
      el.classList.toggle("on", el.getAttribute("data-lang") === lang);
    });
    root.setAttribute("data-language", lang);
    try { localStorage.setItem("mumu-blog-lang", lang); } catch (e) {}
  }

  var savedLang = stored("mumu-blog-lang");
  if (savedLang && savedLang !== root.getAttribute("data-language")) {
    setLang(savedLang);
  }

  var langBtn = document.getElementById("langBtn");
  if (langBtn) {
    langBtn.addEventListener("click", function () {
      var next = root.getAttribute("data-language") === "pt" ? "en" : "pt";
      setLang(next);
    });
  }
})();
