(function () {
  'use strict';

  const ADSENSE_CLIENT = 'ca-pub-6918638598461716';
  const DEFAULT_GOOGLE_ANALYTICS_ID = 'G-1R5FFVKTF8';
  const DEFAULT_CLARITY_PROJECT_ID = 'qnqi8o9y94';
  const googleAnalyticsId =
    document.querySelector('meta[name="google-analytics-id"]')?.content?.trim() ||
    DEFAULT_GOOGLE_ANALYTICS_ID;
  const clarityProjectId =
    document.querySelector('meta[name="microsoft-clarity-id"]')?.content?.trim() ||
    DEFAULT_CLARITY_PROJECT_ID;
  const path = window.location.pathname;
  const hostname = window.location.hostname;
  const isNoAdPage =
    ['/submit', '/contact'].includes(path);
  const hasManualAds =
    document.querySelector('ins.adsbygoogle') !== null;
  const canLoadVercelInsights =
    hostname !== 'localhost' &&
    hostname !== '127.0.0.1';

  if (canLoadVercelInsights) {
    initVercel();
  }

  if (googleAnalyticsId && canLoadVercelInsights) {
    initGoogleAnalytics(googleAnalyticsId);
  }

  if (clarityProjectId && canLoadVercelInsights) {
    initClarity(clarityProjectId);
  }

  if (isNoAdPage) {
    log('Ads disabled (no-ad page)');
    return;
  }

  deferNonCritical(function () {
    if (hasManualAds) {
      log('Manual ads detected (subject page)');
      loadAdSenseBase(initializeManualAds);
      return;
    }

    log('Loading lightweight analytics and ads');
    loadAdSenseBase();
  });

  function deferNonCritical(callback) {
    function runWhenIdle() {
      if ('requestIdleCallback' in window) {
        window.requestIdleCallback(callback, { timeout: 3000 });
      } else {
        window.setTimeout(callback, 1500);
      }
    }

    if (document.readyState === 'complete') {
      runWhenIdle();
      return;
    }

    window.addEventListener('load', runWhenIdle, { once: true });
  }

  function loadAdSenseBase(onReady) {
    if (window.__ADSENSE_LOADED__) {
      if (typeof onReady === 'function') onReady();
      return;
    }

    window.__ADSENSE_LOADED__ = true;

    const s = document.createElement('script');
    s.async = true;
    s.src =
      'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' +
      ADSENSE_CLIENT;
    s.crossOrigin = 'anonymous';
    if (typeof onReady === 'function') {
      s.addEventListener('load', onReady, { once: true });
    }

    document.head.appendChild(s);
  }

  function initializeManualAds() {
    if (typeof window.__initManualAds === 'function') {
      window.__initManualAds();
    }
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

  function initGoogleAnalytics(measurementId) {
    if (window.__GA_LOADED__) {
      return;
    }

    window.__GA_LOADED__ = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag =
      window.gtag ||
      function () {
        window.dataLayer.push(arguments);
      };

    const s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(measurementId);
    s.addEventListener(
      'load',
      function () {
        window.gtag('js', new Date());
        window.gtag('config', measurementId);
      },
      { once: true }
    );
    document.head.appendChild(s);
  }

  function initClarity(projectId) {
    if (window.__CLARITY_LOADED__) {
      return;
    }

    window.__CLARITY_LOADED__ = true;

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
    })(window, document, 'clarity', 'script', projectId);
  }

  function log(msg) {
    console.log('[analytics.js]', msg);
  }
})();
