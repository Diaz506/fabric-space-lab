/* ============================================================
   ZOSA Mission Control — Code Blocks
   Prism.js integration, copy buttons, language badges
   ============================================================ */

(function () {
  'use strict';

  /* --- Enhance Code Blocks --- */
  function enhanceCodeBlocks() {
    var terminals = document.querySelectorAll('.code-terminal');
    terminals.forEach(function (terminal) {
      var copyBtn = terminal.querySelector('.copy-btn');
      var codeEl = terminal.querySelector('pre code');
      if (!copyBtn || !codeEl) return;

      copyBtn.addEventListener('click', function () {
        var text = codeEl.textContent;
        navigator.clipboard.writeText(text).then(function () {
          copyBtn.textContent = 'Copied!';
          copyBtn.classList.add('copied');
          setTimeout(function () {
            copyBtn.textContent = 'Copy';
            copyBtn.classList.remove('copied');
          }, 2000);
        }).catch(function () {
          // Fallback for older browsers
          var ta = document.createElement('textarea');
          ta.value = text;
          ta.style.position = 'fixed';
          ta.style.left = '-9999px';
          document.body.appendChild(ta);
          ta.select();
          document.execCommand('copy');
          document.body.removeChild(ta);
          copyBtn.textContent = 'Copied!';
          copyBtn.classList.add('copied');
          setTimeout(function () {
            copyBtn.textContent = 'Copy';
            copyBtn.classList.remove('copied');
          }, 2000);
        });
      });
    });
  }

  /* --- Run Prism Highlighting --- */
  function highlightCode() {
    if (typeof Prism !== 'undefined') {
      Prism.highlightAll();
    }
  }

  /* --- Init --- */
  function init() {
    highlightCode();
    enhanceCodeBlocks();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
