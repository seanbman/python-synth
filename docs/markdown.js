/* A deliberately small Markdown renderer for the manual's authored content. */
(function () {
  "use strict";

  function escapeHtml(value) {
    return value.replace(/[&<>"']/g, function (character) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[character];
    });
  }

  function inline(value) {
    var text = escapeHtml(value);
    text = text.replace(/`([^`]+)`/g, "<code>$1</code>");
    text = text.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    text = text.replace(/__([^_]+)__/g, "<strong>$1</strong>");
    text = text.replace(/\*([^*]+)\*/g, "<em>$1</em>");
    text = text.replace(/_([^_]+)_/g, "<em>$1</em>");
    text = text.replace(/!\[([^\]]*)\]\(([^\s)]+)\)/g, function (_, alt, src) {
      var safeSrc = /^(https?:|\/|\.?\/?[a-z0-9])/i.test(src) ? src : "";
      return '<img class="article-image" src="' + safeSrc + '" alt="' + escapeHtml(alt) + '">';
    });
    text = text.replace(/\[([^\]]+)\]\(([^\s)]+)\)/g, function (_, label, href) {
      var safeHref = /^(https?:|mailto:|#)/i.test(href) ? href : "#";
      return '<a href="' + safeHref + '">' + label + "</a>";
    });
    return text;
  }

  function render(markdown) {
    var lines = markdown.replace(/\r\n?/g, "\n").split("\n");
    var html = [];
    var paragraph = [];
    var listType = null;
    var inCode = false;
    var codeLines = [];

    function flushParagraph() {
      if (paragraph.length) {
        html.push("<p>" + inline(paragraph.join(" ")) + "</p>");
        paragraph = [];
      }
    }

    function closeList() {
      if (listType) {
        html.push("</" + listType + ">");
        listType = null;
      }
    }

    function closeCode() {
      if (inCode) {
        html.push("<pre><code>" + escapeHtml(codeLines.join("\n")) + "</code></pre>");
        codeLines = [];
        inCode = false;
      }
    }

    lines.forEach(function (line) {
      if (/^```/.test(line)) {
        flushParagraph();
        closeList();
        if (inCode) closeCode(); else inCode = true;
        return;
      }
      if (inCode) {
        codeLines.push(line);
        return;
      }
      if (/^\s*$/.test(line)) {
        flushParagraph();
        closeList();
        return;
      }
      var heading = line.match(/^(#{1,3})\s+(.+?)\s*#*$/);
      if (heading) {
        flushParagraph();
        closeList();
        var level = heading[1].length;
        var title = inline(heading[2]);
        var slug = heading[2].toLowerCase().replace(/[^a-z0-9\s-]/g, "").trim().replace(/\s+/g, "-");
        html.push("<h" + level + ' id="' + slug + '">' + title + "</h" + level + ">");
        return;
      }
      if (/^---+$/.test(line.trim())) {
        flushParagraph();
        closeList();
        html.push("<hr>");
        return;
      }
      var quote = line.match(/^>\s?(.*)$/);
      if (quote) {
        flushParagraph();
        closeList();
        html.push("<blockquote><p>" + inline(quote[1]) + "</p></blockquote>");
        return;
      }
      var item = line.match(/^\s*[-*]\s+(.+)$/);
      var ordered = line.match(/^\s*\d+\.\s+(.+)$/);
      if (item || ordered) {
        flushParagraph();
        var desiredList = ordered ? "ol" : "ul";
        if (listType && listType !== desiredList) closeList();
        if (!listType) {
          listType = desiredList;
          html.push("<" + listType + ">");
        }
        html.push("<li>" + inline((item || ordered)[1]) + "</li>");
        return;
      }
      closeList();
      paragraph.push(line.trim());
    });

    flushParagraph();
    closeList();
    closeCode();
    return html.join("\n");
  }

  window.PythonSynthMarkdown = { render: render };
})();
