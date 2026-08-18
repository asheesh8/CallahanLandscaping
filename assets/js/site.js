/* Callahan Landscaping — restrained enhancement only.
   Everything here is optional: the page and the quote form both work with JS off. */
(function () {
  'use strict';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* ---- Nav leaves the photo ------------------------------------------- */
  var nav = document.getElementById('nav');
  var hero = document.querySelector('.hero');
  if (nav && hero && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      nav.classList.toggle('stuck', !entries[0].isIntersecting);
    }, { rootMargin: '-72px 0px 0px 0px', threshold: 0 })
      .observe(hero);
  }

  /* ---- Reduced motion: freeze the hero on its poster frame ------------- */
  var heroVideo = document.querySelector('.hero-video');
  function applyMotionPref() {
    if (!heroVideo) return;
    if (reduce.matches) { heroVideo.pause(); heroVideo.removeAttribute('autoplay'); }
    else { var p = heroVideo.play(); if (p && p.catch) p.catch(function () {}); }
  }
  applyMotionPref();
  if (reduce.addEventListener) reduce.addEventListener('change', applyMotionPref);

  /* ---- Entrance reveals ------------------------------------------------ */
  if ('IntersectionObserver' in window && !reduce.matches) {
    var targets = document.querySelectorAll('.band .label, .h2, .lede, .reel-item, .grid li, .season li, .form, .note');
    Array.prototype.forEach.call(targets, function (el) { el.classList.add('reveal'); });
    var revealer = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        // Reveal on entry, but also reveal anything already scrolled past — otherwise
        // jumping to an anchor leaves everything above it invisible on the way back up.
        if (!e.isIntersecting && e.boundingClientRect.top > 0) return;
        e.target.classList.add('in');
        revealer.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
    Array.prototype.forEach.call(targets, function (el) { revealer.observe(el); });

    // Failsafe: never let the page sit invisible if the observer misbehaves.
    setTimeout(function () {
      Array.prototype.forEach.call(targets, function (el) { el.classList.add('in'); });
    }, 3000);
  }

  /* ---- Reel clips only play while visible ------------------------------ */
  var clips = document.querySelectorAll('video[data-autoplay]');
  if (clips.length && 'IntersectionObserver' in window) {
    var clipObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var v = e.target;
        if (e.isIntersecting && !reduce.matches) {
          if (v.preload === 'none') v.preload = 'auto';
          var p = v.play(); if (p && p.catch) p.catch(function () {});
        } else { v.pause(); }
      });
    }, { threshold: 0.35 });
    Array.prototype.forEach.call(clips, function (v) { clipObs.observe(v); });
  }

  /* ---- Quote form: enhance, never require ----------------------------- */
  var form = document.getElementById('quote-form');
  var status = document.getElementById('form-status');
  if (form && window.fetch) {
    form.addEventListener('submit', function (ev) {
      var name = form.elements.name.value.trim();
      var contact = form.elements.contact.value.trim();
      if (!name || !contact) return; /* let the browser handle it natively */

      ev.preventDefault();
      var btn = form.querySelector('button[type="submit"]');
      btn.disabled = true;
      status.removeAttribute('data-state');
      status.textContent = 'Sending…';

      fetch(form.action, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify({
          name: name,
          contact: contact,
          address: form.elements.address.value.trim(),
          message: form.elements.message.value.trim(),
          website: form.elements.website.value
        })
      })
        .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, body: j }; }); })
        .then(function (res) {
          if (!res.ok) throw new Error(res.body && res.body.error || 'Something went wrong.');
          form.reset();
          status.setAttribute('data-state', 'ok');
          status.textContent = 'Got it — we will be in touch.';
        })
        .catch(function (err) {
          status.setAttribute('data-state', 'err');
          status.innerHTML = (err.message || 'Could not send.') +
            ' Text or call <a href="tel:+18025039275">(802) 503-9275</a> instead.';
        })
        .finally(function () { btn.disabled = false; });
    });
  }

  /* ---- Theme toggle: page room only. The hero and footer keep their own
     media palette regardless, so a photographic scrim never goes pale. ---- */
  var themeBtn = document.getElementById('theme-btn');
  if (themeBtn) {
    var root = document.documentElement;
    var sysDark = window.matchMedia('(prefers-color-scheme: dark)');
    themeBtn.addEventListener('click', function () {
      var current = root.getAttribute('data-theme') || (sysDark.matches ? 'dark' : 'light');
      var next = current === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (e) {}
      themeBtn.setAttribute('aria-label', 'Switch to ' + (next === 'dark' ? 'light' : 'dark') + ' theme');
    });
  }
})();
