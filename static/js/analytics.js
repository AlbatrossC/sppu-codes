(function () {
  'use strict';

  const ADSENSE_CLIENT = 'ca-pub-6918638598461716';
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

  function log(msg) {
    console.log('[analytics.js]', msg);
  }
})();
