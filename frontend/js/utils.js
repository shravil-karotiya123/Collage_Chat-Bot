/**
 * Helper Utility Functions for MRPL Sovereign AI Workbench UI.
 */

const Utils = {
  /**
   * Escape HTML string safely to prevent XSS.
   */
  escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  },

  /**
   * Format ISO date string into readable local timestamp.
   */
  formatDate(isoStr) {
    if (!isoStr) return 'N/A';
    try {
      const d = new Date(isoStr);
      return d.toLocaleString();
    } catch {
      return String(isoStr);
    }
  },

  /**
   * Generate HTML markup for a status badge pill.
   */
  createBadge(status) {
    if (!status) return '<span class="badge badge-info">UNKNOWN</span>';
    const clean = String(status).toLowerCase();
    let badgeClass = 'badge-info';

    if (['healthy', 'pass', 'completed', 'success', 'ready'].includes(clean)) {
      badgeClass = 'badge-healthy';
    } else if (['warning', 'waiting_for_approval', 'running', 'pending', 'degraded'].includes(clean)) {
      badgeClass = 'badge-warning';
    } else if (['error', 'fail', 'failed', 'rejected', 'unhealthy'].includes(clean)) {
      badgeClass = 'badge-error';
    }

    return `<span class="badge ${badgeClass}">${this.escapeHtml(status)}</span>`;
  },

  /**
   * Toast notification display helper.
   */
  showToast(message, isError = false) {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${isError ? 'error' : ''}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.5s';
      setTimeout(() => toast.remove(), 500);
    }, 4000);
  },

  /**
   * Copy code to clipboard from code block widget.
   */
  copyCode(btn) {
    const wrapper = btn.closest('.code-block-wrapper');
    if (!wrapper) return;
    const codeEl = wrapper.querySelector('code');
    if (!codeEl) return;
    const text = codeEl.innerText || codeEl.textContent;
    navigator.clipboard.writeText(text).then(() => {
      btn.textContent = 'Copied!';
      btn.classList.add('copied');
      setTimeout(() => {
        btn.textContent = 'Copy';
        btn.classList.remove('copied');
      }, 2000);
    }).catch(() => {
      Utils.showToast('Failed to copy code to clipboard', true);
    });
  },

  /**
   * Parse and render Markdown string safely into structured, professional HTML.
   */
  renderMarkdown(md) {
    if (md === null || md === undefined || md === '') return '';
    let raw = String(md).replace(/\r\n/g, '\n').replace(/\r/g, '\n');

    // 1. Extract fenced code blocks into placeholders
    const codeBlocks = [];
    raw = raw.replace(/```([a-zA-Z0-9_\-#+.]*)\n?([\s\S]*?)```/g, (match, lang, code) => {
      const placeholder = `@@@CODEBLOCK_${codeBlocks.length}@@@`;
      const cleanLang = (lang || 'code').trim().toLowerCase();
      const escapedCode = Utils.escapeHtml(code.replace(/^\n+|\n+$/g, ''));
      const blockHtml = `
        <div class="code-block-wrapper">
          <div class="code-block-header">
            <span class="code-block-lang">${Utils.escapeHtml(cleanLang)}</span>
            <button type="button" class="code-copy-btn" onclick="Utils.copyCode(this)">Copy</button>
          </div>
          <pre><code class="language-${Utils.escapeHtml(cleanLang)}">${escapedCode}</code></pre>
        </div>
      `.trim();
      codeBlocks.push(blockHtml);
      return '\n\n' + placeholder + '\n\n';
    });

    // 2. Extract inline code into placeholders
    const inlineCodes = [];
    raw = raw.replace(/`([^`\n]+)`/g, (match, code) => {
      const placeholder = `@@@INLINECODE_${inlineCodes.length}@@@`;
      inlineCodes.push(`<code class="inline-code">${Utils.escapeHtml(code)}</code>`);
      return placeholder;
    });

    // 3. Escape HTML on remaining raw text to prevent XSS
    raw = Utils.escapeHtml(raw);

    // 4. Parse Tables
    raw = raw.replace(/(?:^|\n)((?:\|[^\n]+\|\r?\n)(?:\|[\s\-:]+\|\r?\n)(?:\|[^\n]+\|\r?\n?)+)/g, (match, tableBlock) => {
      const lines = tableBlock.trim().split('\n').map(l => l.trim()).filter(Boolean);
      if (lines.length < 2) return match;
      const headerLine = lines[0];
      const dataLines = lines.slice(2);

      const parseRow = (line, isHeader = false) => {
        let cells = line.split('|').map(c => c.trim());
        if (line.startsWith('|')) cells.shift();
        if (line.endsWith('|')) cells.pop();
        const tag = isHeader ? 'th' : 'td';
        return '<tr>' + cells.map(c => `<${tag}>${parseInline(c)}</${tag}>`).join('') + '</tr>';
      };

      let tableHtml = '<div class="table-responsive"><table class="markdown-table"><thead>';
      tableHtml += parseRow(headerLine, true);
      tableHtml += '</thead><tbody>';
      dataLines.forEach(dLine => {
        tableHtml += parseRow(dLine, false);
      });
      tableHtml += '</tbody></table></div>';
      return '\n\n' + tableHtml + '\n\n';
    });

    // Helper for inline spans: bold, italic, strikethrough, links
    function parseInline(text) {
      if (!text) return '';
      let s = text;
      // Bold: **text** or __text__
      s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
      s = s.replace(/__(.+?)__/g, '<strong>$1</strong>');
      // Italic: *text* or _text_ (not inside words)
      s = s.replace(/(^|[^\*])\*([^\*\n]+)\*([^\*]|$)/g, '$1<em>$2</em>$3');
      s = s.replace(/(^|[^_])_([^_\n]+)_([^_]|$)/g, '$1<em>$2</em>$3');
      // Strikethrough: ~~text~~
      s = s.replace(/~~(.+?)~~/g, '<del>$1</del>');
      // Markdown links: [text](url)
      s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (m, linkText, url) => {
        const cleanUrl = url.trim();
        if (cleanUrl.startsWith('http://') || cleanUrl.startsWith('https://') || cleanUrl.startsWith('#') || cleanUrl.startsWith('/')) {
          return `<a href="${cleanUrl}" target="_blank" rel="noopener noreferrer" class="markdown-link">${linkText}</a>`;
        }
        return linkText;
      });
      return s;
    }

    // 5. Line-by-line block parsing
    const rawLines = raw.split('\n');
    const blocks = [];
    let currentList = null; // { type: 'ul'|'ol', items: [ { text, subitems: [] } ] }
    let currentBlockquote = [];
    let currentParagraph = [];

    function flushParagraph() {
      if (currentParagraph.length > 0) {
        const content = currentParagraph.map(l => parseInline(l)).join('<br>');
        blocks.push(`<p class="markdown-p">${content}</p>`);
        currentParagraph = [];
      }
    }

    function flushBlockquote() {
      if (currentBlockquote.length > 0) {
        const content = currentBlockquote.map(l => parseInline(l)).join('<br>');
        blocks.push(`<blockquote class="markdown-blockquote">${content}</blockquote>`);
        currentBlockquote = [];
      }
    }

    function flushList() {
      if (currentList && currentList.items.length > 0) {
        const tag = currentList.type;
        let html = `<${tag} class="markdown-${tag}">`;
        for (const item of currentList.items) {
          html += `<li>${parseInline(item.text)}`;
          if (item.subitems && item.subitems.length > 0) {
            html += `<ul class="markdown-sublist">`;
            for (const sub of item.subitems) {
              html += `<li>${parseInline(sub)}</li>`;
            }
            html += `</ul>`;
          }
          html += `</li>`;
        }
        html += `</${tag}>`;
        blocks.push(html);
        currentList = null;
      }
    }

    for (let i = 0; i < rawLines.length; i++) {
      const line = rawLines[i];
      const trimmed = line.trim();

      // Check placeholder
      if (trimmed.startsWith('@@@CODEBLOCK_') || trimmed.startsWith('<div class="table-responsive">')) {
        flushParagraph();
        flushBlockquote();
        flushList();
        blocks.push(trimmed);
        continue;
      }

      // Empty line -> flush open blocks
      if (!trimmed) {
        flushParagraph();
        flushBlockquote();
        flushList();
        continue;
      }

      // Horizontal Rule: ---, ***, ___
      if (/^(?:---|\*\*\*|___)$/.test(trimmed)) {
        flushParagraph();
        flushBlockquote();
        flushList();
        blocks.push('<hr class="markdown-hr">');
        continue;
      }

      // Headings: # Heading
      const headingMatch = trimmed.match(/^(#{1,6})\s+(.+)$/);
      if (headingMatch) {
        flushParagraph();
        flushBlockquote();
        flushList();
        const level = headingMatch[1].length;
        const text = parseInline(headingMatch[2]);
        blocks.push(`<h${level} class="markdown-h${level}">${text}</h${level}>`);
        continue;
      }

      // Blockquotes: > quote (note: > is escaped as &gt;)
      const bqMatch = trimmed.match(/^&gt;\s?(.*)$/);
      if (bqMatch) {
        flushParagraph();
        flushList();
        currentBlockquote.push(bqMatch[1]);
        continue;
      } else if (currentBlockquote.length > 0) {
        flushBlockquote();
      }

      // List detection (indentation check for nested bullets)
      const indent = line.search(/\S/);
      const isUl = /^[\-\*\+]\s+(.+)$/.test(trimmed);
      const isOl = /^(\d+)\.\s+(.+)$/.test(trimmed);

      if (isUl || isOl) {
        flushParagraph();
        flushBlockquote();

        // Nested sub-item under active list
        if (indent >= 2 && currentList && currentList.items.length > 0) {
          const itemText = trimmed.replace(/^(?:[\-\*\+]|\d+\.)\s+/, '');
          const lastItem = currentList.items[currentList.items.length - 1];
          lastItem.subitems = lastItem.subitems || [];
          lastItem.subitems.push(itemText);
          continue;
        }

        const listType = isUl ? 'ul' : 'ol';
        const itemText = isUl ? trimmed.match(/^[\-\*\+]\s+(.+)$/)[1] : trimmed.match(/^(\d+)\.\s+(.+)$/)[2];

        if (!currentList || currentList.type !== listType) {
          flushList();
          currentList = { type: listType, items: [] };
        }

        currentList.items.push({ text: itemText, subitems: [] });
        continue;
      }

      // If we were in a list, check if this is an indented continuation line
      if (currentList && indent >= 2 && currentList.items.length > 0) {
        const lastItem = currentList.items[currentList.items.length - 1];
        lastItem.text += ' ' + trimmed;
        continue;
      }

      // Regular paragraph text
      flushList();
      flushBlockquote();
      currentParagraph.push(trimmed);
    }

    flushParagraph();
    flushBlockquote();
    flushList();

    let finalHtml = blocks.join('\n');

    // 6. Restore inline code placeholders
    finalHtml = finalHtml.replace(/@@@INLINECODE_(\d+)@@@/g, (m, idx) => {
      return inlineCodes[parseInt(idx, 10)] || m;
    });

    // 7. Restore code block placeholders
    finalHtml = finalHtml.replace(/@@@CODEBLOCK_(\d+)@@@/g, (m, idx) => {
      return codeBlocks[parseInt(idx, 10)] || m;
    });

    return `<div class="markdown-body">${finalHtml}</div>`;
  }
};

