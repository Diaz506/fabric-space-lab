/* ============================================================
   ZOSA Mission Control — Navigation
   Module list, theme toggle, mobile menu
   ============================================================ */

(function () {
  'use strict';

  /* --- Module Registry --- */
  var modules = [
    { id: '00', title: 'Prerequisites & Mission Briefing', file: '00-prerequisites.html', icon: '🚀', tags: ['setup'] },
    { id: '01', title: 'Capacity & Workspace Setup', file: '01-capacity.html', icon: '🏗️', tags: ['admin'] },
    { id: '02', title: 'Governance & Security', file: '02-governance.html', icon: '🔒', tags: ['security'] },
    { id: '03', title: 'Data Ingestion', file: '03-ingestion.html', icon: '📡', tags: ['data'] },
    { id: '04', title: 'Medallion Lakehouse', file: '04-medallion.html', icon: '💎', tags: ['lakehouse', 'spark'] },
    { id: '05', title: 'Semantic Model & Direct Lake', file: '05-semantic-model.html', icon: '🧊', tags: ['modeling'] },
    { id: '06', title: 'Power BI Reports', file: '06-power-bi.html', icon: '📊', tags: ['visualization'] },
    { id: '07', title: 'Real-Time Intelligence', file: '07-real-time.html', icon: '⚡', tags: ['streaming', 'kql'] },
    { id: '08', title: 'Data Science & ML', file: '08-data-science.html', icon: '🧬', tags: ['ml', 'mlflow'] },
    { id: '09', title: 'Ontology & Knowledge Graph', file: '09-ontology.html', icon: '🕸️', tags: ['preview', 'ai'] },
    { id: '10', title: 'AI Agents', file: '10-ai-agents.html', icon: '🤖', tags: ['agents', 'ai'] },
    { id: '11', title: 'CI/CD & Deployment', file: '11-ci-cd.html', icon: '🔄', tags: ['devops'] },
    { id: '12', title: 'Monitoring & Optimization', file: '12-monitoring.html', icon: '📈', tags: ['operations'] }
  ];

  /* Expose for other scripts */
  window.ZOSA_MODULES = modules;

  /* --- Theme Toggle --- */
  function initTheme() {
    var stored = localStorage.getItem('zosa-theme');
    if (stored) {
      document.documentElement.setAttribute('data-theme', stored);
    }

    var btn = document.querySelector('.theme-toggle');
    if (!btn) return;

    function updateIcon() {
      var isDark = document.documentElement.getAttribute('data-theme') !== 'light';
      btn.textContent = isDark ? '☀️' : '🌙';
      btn.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
    }

    btn.addEventListener('click', function () {
      var isDark = document.documentElement.getAttribute('data-theme') !== 'light';
      var next = isDark ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('zosa-theme', next);
      updateIcon();
    });

    updateIcon();
  }

  /* --- Mobile Menu Toggle --- */
  function initMobileMenu() {
    var toggle = document.querySelector('.mobile-menu-toggle');
    var toc = document.querySelector('.mini-toc');
    if (!toggle || !toc) return;

    toggle.addEventListener('click', function () {
      toc.classList.toggle('open');
      var isOpen = toc.classList.contains('open');
      toggle.setAttribute('aria-expanded', isOpen);
    });

    // Close on link click
    toc.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        toc.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* --- Get Module Neighbors --- */
  function getModuleNav(currentId) {
    var idx = modules.findIndex(function (m) { return m.id === currentId; });
    return {
      prev: idx > 0 ? modules[idx - 1] : null,
      next: idx < modules.length - 1 ? modules[idx + 1] : null
    };
  }

  window.ZOSA_getModuleNav = getModuleNav;

  /* --- Init --- */
  function init() {
    initTheme();
    initMobileMenu();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
