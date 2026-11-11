(function () {
  "use strict";

  var pages = [
    { id: "overview", title: "Overview", section: "Start here", file: "overview.md", description: "Meet Synthepyzer and learn the shape of the instrument." },
    { id: "getting-started", title: "Getting Started", section: "Start here", file: "getting-started.md", description: "Connect a controller and make your first sound." },
    { id: "midi-controllers", title: "MIDI Controllers", section: "Play", file: "midi-controllers.md", description: "Use a keyboard and common performance controls." },
    { id: "playing", title: "Playing", section: "Play", file: "playing.md", description: "Shape a patch while you perform." },
    { id: "features", title: "Features", section: "Explore", file: "features.md", description: "See what you can do with the instrument." },
    { id: "layers-presets", title: "Layers & Presets", section: "Explore", file: "layers-and-presets.md", description: "Stack two layers and save sounds in the .spyzr format." }
  ];

  var state = { current: "overview", pages: pages, searchOpen: false };
  var article = document.getElementById("article");
  var breadcrumbs = document.getElementById("breadcrumbs");
  var outline = document.getElementById("page-outline");
  var nav = document.getElementById("sidebar-nav");
  var input = document.getElementById("search-input");
  var results = document.getElementById("search-results");
  var sidebar = document.getElementById("sidebar");
  var overlay = document.getElementById("mobile-overlay");
  var menuButton = document.getElementById("mobile-menu");

  function pageFor(id) { return pages.find(function (page) { return page.id === id; }) || pages[0]; }

  function routeFromHash() {
    var raw = window.location.hash.replace(/^#\/?/, "") || "overview";
    var parts = raw.split("?");
    var params = new URLSearchParams(parts[1] || "");
    return { pageId: parts[0] || "overview", section: params.get("section") || "" };
  }

  function scrollToSection(section, behavior) {
    if (!section) return;
    var heading = document.getElementById(section);
    if (!heading || !article.contains(heading)) return;
    heading.scrollIntoView({ behavior: behavior || "smooth", block: "start" });
    heading.setAttribute("tabindex", "-1");
    heading.focus({ preventScroll: true });
  }

  function renderNav() {
    var groups = pages.reduce(function (accumulator, page) {
      (accumulator[page.section] = accumulator[page.section] || []).push(page);
      return accumulator;
    }, {});
    nav.innerHTML = Object.keys(groups).map(function (section) {
      return '<section class="nav-group"><h2 class="nav-group__label">' + section + '</h2>' +
        groups[section].map(function (page) {
          return '<a class="nav-link" href="#/' + page.id + '" data-page="' + page.id + '"' + (page.id === state.current ? ' aria-current="page"' : '') + '>' + page.title + '</a>';
        }).join("") + '</section>';
    }).join("");
  }

  function renderBreadcrumbs(page) {
    breadcrumbs.innerHTML = '<a href="#/overview">Manual</a><span class="breadcrumbs__separator" aria-hidden="true">/</span><a href="#/' + page.id + '">' + page.section + '</a><span class="breadcrumbs__separator" aria-hidden="true">/</span><span class="breadcrumbs__current" aria-current="page">' + page.title + '</span>';
  }

  function renderOutline() {
    var headings = Array.prototype.slice.call(article.querySelectorAll("h2, h3"));
    if (!headings.length) {
      outline.innerHTML = "";
      return;
    }
    outline.innerHTML = '<p class="page-outline__label">On this page</p>' + headings.map(function (heading) {
      return '<a href="#/' + state.current + '?section=' + encodeURIComponent(heading.id) + '" data-section-link="' + heading.id + '">' + heading.textContent + '</a>';
    }).join("");
  }

  function renderFooter(page) {
    var index = pages.findIndex(function (candidate) { return candidate.id === page.id; });
    var previous = index > 0 ? pages[index - 1] : null;
    var next = index < pages.length - 1 ? pages[index + 1] : null;
    var links = [];
    if (previous) links.push('<a href="#/' + previous.id + '">← ' + previous.title + '</a>'); else links.push("<span></span>");
    if (next) links.push('<a href="#/' + next.id + '">' + next.title + ' →</a>'); else links.push("<span></span>");
    article.insertAdjacentHTML("beforeend", '<footer class="article__footer">' + links.join("") + "</footer>");
  }

  function loadPage(id, section) {
    var page = pageFor(id);
    state.current = page.id;
    renderNav();
    renderBreadcrumbs(page);
    article.innerHTML = '<p class="loading">Loading the manual…</p>';
    outline.innerHTML = "";
    fetch("content/" + page.file)
      .then(function (response) {
        if (!response.ok) throw new Error("Page not found");
        return response.text();
      })
      .then(function (markdown) {
        article.innerHTML = '<p class="article__eyebrow">' + page.section + '</p>' + PythonSynthMarkdown.render(markdown);
        renderOutline();
        renderFooter(page);
        document.title = page.title + " · Synthepyzer Manual";
        document.getElementById("main-content").focus({ preventScroll: true });
        if (section) window.requestAnimationFrame(function () { scrollToSection(section, "auto"); });
      })
      .catch(function () {
        article.innerHTML = '<div class="error-card"><strong>We couldn’t load this page.</strong><p>Try refreshing the manual or return to the <a href="#/overview">overview</a>.</p></div>';
        document.title = "Page unavailable · Synthepyzer Manual";
      });
  }

  function searchIndex() {
    return Promise.all(pages.map(function (page) {
      return fetch("content/" + page.file).then(function (response) { return response.text(); }).then(function (text) {
        return Object.assign({}, page, { body: text.replace(/[#*_>`-]/g, " ").replace(/\s+/g, " ").trim() });
      });
    }));
  }

  function showSearchResults(matches) {
    results.hidden = false;
    if (!matches.length) {
      results.innerHTML = '<div class="search-empty">No pages match that search.</div>';
      return;
    }
    results.innerHTML = matches.map(function (page) {
      var query = input.value.trim().toLowerCase();
      var position = page.body.toLowerCase().indexOf(query);
      var snippet = position >= 0 ? page.body.slice(Math.max(0, position - 42), position + 100) : page.description;
      return '<button class="search-result" type="button" role="option" data-result="' + page.id + '"><span class="search-result__title">' + page.title + '</span><span class="search-result__section">' + page.section + '</span><span class="search-result__snippet">' + snippet + '</span></button>';
    }).join("");
    results.querySelectorAll("[data-result]").forEach(function (button) {
      button.addEventListener("click", function () {
        window.location.hash = "/" + button.dataset.result;
        closeSearch();
      });
    });
  }

  var indexPromise = searchIndex();
  function search(value) {
    var query = value.trim().toLowerCase();
    if (!query) { results.hidden = true; return; }
    indexPromise.then(function (index) {
      var matches = index.filter(function (page) { return (page.title + " " + page.section + " " + page.body).toLowerCase().includes(query); });
      showSearchResults(matches);
    });
  }

  function closeSearch() { results.hidden = true; }

  function handleRoute() {
    var route = routeFromHash();
    if (route.pageId === state.current && article.querySelector("h1")) {
      if (route.section) scrollToSection(route.section);
      else window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }
    loadPage(route.pageId, route.section);
  }

  function closeMobileNav() {
    sidebar.classList.remove("is-open");
    overlay.classList.remove("is-visible");
    overlay.hidden = true;
    menuButton.setAttribute("aria-expanded", "false");
  }

  function toggleMobileNav() {
    var open = sidebar.classList.toggle("is-open");
    overlay.hidden = !open;
    overlay.classList.toggle("is-visible", open);
    menuButton.setAttribute("aria-expanded", String(open));
  }

  window.addEventListener("hashchange", function () {
    handleRoute();
    closeMobileNav();
  });
  window.addEventListener("popstate", handleRoute);
  nav.addEventListener("click", function (event) {
    if (event.target.matches(".nav-link")) closeMobileNav();
  });
  outline.addEventListener("click", function (event) {
    var link = event.target.closest("[data-section-link]");
    if (!link) return;
    event.preventDefault();
    var route = "#/" + state.current + "?section=" + encodeURIComponent(link.dataset.sectionLink);
    window.history.pushState({ page: state.current, section: link.dataset.sectionLink }, "", route);
    scrollToSection(link.dataset.sectionLink);
  });
  menuButton.addEventListener("click", toggleMobileNav);
  overlay.addEventListener("click", closeMobileNav);
  input.addEventListener("input", function () { search(input.value); });
  input.addEventListener("focus", function () { if (input.value.trim()) search(input.value); });
  document.addEventListener("click", function (event) {
    if (!document.getElementById("search-wrap").contains(event.target)) closeSearch();
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "/" && document.activeElement !== input && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) {
      event.preventDefault();
      input.focus();
    }
    if (event.key === "Escape") { closeSearch(); closeMobileNav(); }
  });

  renderNav();
  var initialRoute = routeFromHash();
  loadPage(initialRoute.pageId, initialRoute.section);
})();
