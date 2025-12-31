/**
 * Central Analytics & Ad Loader (AdSense-safe)
 * - Loads Clarity & Vercel everywhere
 * - Loads AdSense only when allowed
 * - NEVER controls ad frequency, timing, or formats
 */

(function () {
  'use strict';

  /* ==============================
     CONFIG
  ============================== */
  const ADSENSE_CLIENT = 'ca-pub-6918638598461716';
  const CLARITY_ID = 'qnqi8o9y94';

  /* ==============================
     PAGE DETECTION (READ-ONLY)
  ============================== */
  const path = window.location.pathname;

  const isViewerPage =
    path.startsWith('/question-papers/') &&
    path !== '/question-papers';

  const isSubjectPage =
    /^\/[^\/]+\/?$/.test(path) &&
    !['/', '/submit', '/contact', '/question-papers', '/sitemap'].includes(path);

  const isNoAdPage =
    ['/submit', '/contact'].includes(path);

  /* Subject pages have manual <ins> ads */
  const hasManualAds =
    document.querySelector('ins.adsbygoogle') !== null;

  /* ==============================
     ANALYTICS (ALWAYS SAFE)
  ============================== */
  initClarity();
  initVercel();

  /* ==============================
     ADSENSE (SAFE GATE)
  ============================== */
  if (isNoAdPage) {
    log('Ads disabled (no-ad page)');
    return;
  }

  if (hasManualAds) {
    log('Manual ads detected (subject page)');
    loadAdSenseBase();
    return;
  }

  if (isViewerPage) {
    log('Viewer page → allow vignette/anchor via AdSense UI');
    loadAdSenseBase();
    return;
  }

  // Normal pages
  log('Normal page → auto ads allowed');
  loadAdSenseBase();

  /* ==============================
     FUNCTIONS
  ============================== */

  function loadAdSenseBase() {
    if (window.__ADSENSE_LOADED__) return;

    window.__ADSENSE_LOADED__ = true;

    const s = document.createElement('script');
    s.async = true;
    s.src =
      'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' +
      ADSENSE_CLIENT;
    s.crossOrigin = 'anonymous';

    document.head.appendChild(s);
  }

  function initClarity() {
    (function (c, l, a, r, i, t, y) {
      c[a] =
        c[a] ||
        function () {
          (c[a].q = c[a].q || []).push(arguments);
        };
      t = l.createElement(r);
      t.async = 1;
      t.src = 'https://www.clarity.ms/tag/' + i;
      y = l.getElementsByTagName(r)[0];
      y.parentNode.insertBefore(t, y);
    })(window, document, 'clarity', 'script', CLARITY_ID);
  }

  function initVercel() {
    window.va =
      window.va ||
      function () {
        (window.vaq = window.vaq || []).push(arguments);
      };

    const s = document.createElement('script');
    s.defer = true;
    s.src = '/_vercel/insights/script.js';
    document.head.appendChild(s);
  }

  function log(msg) {
    console.log('[analytics.js]', msg);
  }
})();
