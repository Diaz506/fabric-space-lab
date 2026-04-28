/* ============================================================
   ZOSA Mission Control — Storyboard Interactions
   IntersectionObserver animations, progress bar, starfield
   ============================================================ */

(function () {
  'use strict';

  /* --- Reading Progress Bar --- */
  function initProgressBar() {
    const bar = document.querySelector('.progress-bar');
    if (!bar) return;

    window.addEventListener('scroll', function () {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      bar.style.width = Math.min(progress, 100) + '%';
    }, { passive: true });
  }

  /* --- Chapter Reveal on Scroll --- */
  function initChapterReveal() {
    const chapters = document.querySelectorAll('.chapter');
    if (!chapters.length) return;

    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

    chapters.forEach(function (ch) { observer.observe(ch); });
  }

  /* --- Scroll Spy for Mini-TOC --- */
  function initScrollSpy() {
    const tocLinks = document.querySelectorAll('.mini-toc a');
    if (!tocLinks.length) return;

    const sections = [];
    tocLinks.forEach(function (link) {
      const id = link.getAttribute('href');
      if (id && id.startsWith('#')) {
        const el = document.querySelector(id);
        if (el) sections.push({ el: el, link: link });
      }
    });

    function update() {
      const scrollPos = window.scrollY + 120;
      let active = null;
      sections.forEach(function (s) {
        if (s.el.offsetTop <= scrollPos) active = s;
      });
      tocLinks.forEach(function (l) { l.classList.remove('active'); });
      if (active) active.link.classList.add('active');
    }

    window.addEventListener('scroll', update, { passive: true });
    update();
  }

  /* --- Starfield Generator --- */
  function initStarfield() {
    const container = document.querySelector('.starfield');
    if (!container) return;

    const count = Math.min(Math.floor(window.innerWidth * 0.15), 200);
    for (var i = 0; i < count; i++) {
      var star = document.createElement('div');
      star.className = 'star';
      var size = Math.random() * 2.5 + 0.5;
      star.style.width = size + 'px';
      star.style.height = size + 'px';
      star.style.left = Math.random() * 100 + '%';
      star.style.top = Math.random() * 100 + '%';
      star.style.setProperty('--duration', (Math.random() * 4 + 2) + 's');
      star.style.setProperty('--max-opacity', (Math.random() * 0.5 + 0.3).toString());
      star.style.animationDelay = (Math.random() * 5) + 's';
      container.appendChild(star);
    }
  }

  /* --- Smooth Scroll for Anchor Links --- */
  function initSmoothScroll() {
    document.addEventListener('click', function (e) {
      var link = e.target.closest('a[href^="#"]');
      if (!link) return;
      var target = document.querySelector(link.getAttribute('href'));
      if (!target) return;
      e.preventDefault();
      var offset = 80;
      var top = target.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top: top, behavior: 'smooth' });
      history.pushState(null, '', link.getAttribute('href'));
    });
  }

  /* --- Init All --- */
  function init() {
    initProgressBar();
    initChapterReveal();
    initScrollSpy();
    initStarfield();
    initSmoothScroll();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
