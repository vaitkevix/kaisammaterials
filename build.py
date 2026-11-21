# Saliek index.html no Apps Script Index.html (lietotne) + ātrā savienojuma (Cloudflare) + sākuma ekrāna piedāvājuma.
# Palaid: python3 build.py   © VAITKEVIX, SIA
import re
app = open('apps-script/Index.html', encoding='utf-8').read()
old = open('apps-script/wrapper-old.html', encoding='utf-8').read()
API = 'https://aizvietosana-api.vaitkevix.workers.dev/kais'

head = '''
  <title>SH | Kaisāmmateriāls</title>
  <meta name="theme-color" content="#0f6b5c">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="Kaisāmmateriāls">
  <meta name="author" content="VAITKEVIX, SIA">
  <link rel="apple-touch-icon" sizes="180x180" href="icon.png?v=2">
  <link rel="icon" type="image/png" sizes="64x64" href="favicon.png?v=2">
  <link rel="mask-icon" href="safari-pinned-tab.svg" color="#e07a1f">
  <link rel="manifest" href="manifest.json">
  <link rel="preconnect" href="https://aizvietosana-api.vaitkevix.workers.dev">
  <script>
  /* Ātrā versija: google.script.run → Cloudflare (Google tabula paliek galvenā). © VAITKEVIX, SIA */
  (function () {
    var API = '%s';
    function call(fn, args, ok, fail, uo) {
      fetch(API + '?fn=' + encodeURIComponent(fn), { method: 'POST', headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: JSON.stringify(args) })
        .then(function (r) { return r.json(); })
        .then(function (j) { if (j.notices) notices(j.notices); if (!j.ok) throw new Error(j.error || 'Kļūda'); if (ok) ok(j.result, uo); })
        .catch(function (e) { if (fail) fail(e, uo); else console.error(e); });
    }
    // Ja Google noraidīja fonā saglabātu darbību — parāda vienreiz
    function notices(list) {
      var seen = {}; try { seen = JSON.parse(localStorage.getItem('izv_seen') || '{}'); } catch (e) {}
      list.forEach(function (n) { if (seen[n.id]) return; seen[n.id] = 1; setTimeout(function () { if (window.toast) toast(n.text, 'err'); else alert(n.text); }, 800); });
      try { localStorage.setItem('izv_seen', JSON.stringify(seen)); } catch (e) {}
    }
    function runner(ok, fail, uo) {
      return new Proxy({}, { get: function (_, name) {
        if (name === 'withSuccessHandler') return function (h) { return runner(h, fail, uo); };
        if (name === 'withFailureHandler') return function (h) { return runner(ok, h, uo); };
        if (name === 'withUserObject') return function (o) { return runner(ok, fail, o); };
        if (typeof name !== 'string' || name === 'then') return undefined;
        return function () { call(name, Array.prototype.slice.call(arguments), ok, fail, uo); };
      } });
    }
    var q = {}; new URLSearchParams(location.search).forEach(function (v, k) { q[k] = v; });
    window.google = window.google || {};
    google.script = { run: runner(), url: { getLocation: function (cb) { cb({ parameter: q, parameters: {}, hash: location.hash.slice(1) }); } }, host: { close: function () {}, setHeight: function () {} } };
  })();
  </script>''' % API

app = re.sub(r'\s*<title>[^<]*</title>', '', app, count=1)
app = app.replace('<meta charset="utf-8">', '<meta charset="utf-8">' + head, 1)

open('index.html', 'w', encoding='utf-8').write(app)
print('index.html', len(app))

# ===== Kopējās funkcijas (kā Aizvietošanā): ieeja ar PIN, izvēlne, pamācība soli pa solim =====
import hashlib
addon = open('sh-addon.js', encoding='utf-8').read()
ver = hashlib.sha1(addon.encode()).hexdigest()[:8]
shx = '''<script>
window.SHX = {
  app: 'kais', title: 'Kaisāmmateriāla piegāde', api: 'https://aizvietosana-api.vaitkevix.workers.dev', icon: 'icon.png',
  sub: 'Ievadiet savu PIN kodu vai kurjera paroli',
  hint: 'Pieteicēji — tas pats PIN, kas Aizvietošanā. Kurjeri — sava parole.',
  tabSel: '#tabs .tab', ownMenu: '.actions', a2hs: true,
  tabsFor: function (u) { return u.kind === 'admin' ? ['new-task', 'task-list', 'carrier', 'analytics'] : u.kind === 'kurjers' ? ['carrier', 'task-list'] : ['new-task', 'task-list', 'analytics']; },
  homeTab: function (u) { return u.kind === 'kurjers' ? 'carrier' : 'new-task'; },
  switchTab: function (t) { switchTab(t); },
  onOut: function () { try { sessionStorage.removeItem('carrierOk'); } catch (e) {} },
  onUser: function (u) {
    if ((u.kind === 'kurjers' || u.kind === 'admin') && !state.unlocked) { state.unlocked = true; try { sessionStorage.setItem('carrierOk', '1'); renderCarrierList(); } catch (e) {} }
    if (u.kind === 'kurjers') { if (state.tab !== 'carrier') switchTab('carrier'); shxSia(); }
    else shxReq(u);
    if (typeof moveTabInd === 'function') setTimeout(moveTabInd, 50);
  },
  tours: {
    pieteicejs: [
      { title: 'Sveiki!', text: 'Īsa pamācība, kā pieteikt kaisāmmateriālu. Aizņems pusminūti.' },
      { sel: '#tabs', title: 'Cilnes', text: 'Jauns — pieteikt piegādi. Saraksts — visi pieteikumi un statuss. Statistika — kopsavilkums.' },
      { sel: '#ac', tab: 'new-task', title: 'Adrese', text: 'Sāciet rakstīt adresi un izvēlieties no saraksta.' },
      { sel: '#requester', tab: 'new-task', title: 'Pasūtītājs', text: 'Jūsu vārds ir aizpildīts automātiski.' },
      { sel: '#matPick', tab: 'new-task', title: 'Materiāls', text: 'Sāls, smilts vai mix.' },
      { sel: '#qtyOrder', tab: 'new-task', title: 'Daudzums', text: 'Norādiet maisu skaitu ar − un +.' },
      { sel: '#dz-new', tab: 'new-task', title: 'Bilde', text: 'Ja vajag, pievienojiet bildi.' },
      { sel: '#submitBtn', tab: 'new-task', title: 'Nosūtīt', text: 'Pieteikums saglabājas uzreiz, arī ar vāju internetu.' },
      { sel: '#searchInput', tab: 'task-list', title: 'Saraksts', text: 'Meklējiet pēc adreses, pasūtītāja vai materiāla un sekojiet statusam.' },
      { sel: '.shx-help', tab: 'new-task', title: 'Izvēlne', text: 'Šeit ir pamācība, pievienošana sākuma ekrānam un iziešana.' },
      { title: 'Viss gatavs!', text: 'Veiksmīgu darbu!' }
    ],
    kurjers: [
      { title: 'Sveiki!', text: 'Īsa pamācība kurjeram. Aizņems pusminūti.' },
      { sel: '#carrierContainer', tab: 'carrier', title: 'Jūsu piegādes', text: 'Šeit ir visi gaidošie pieteikumi.' },
      { sel: '#carrierContainer .task, #carrierContainer', tab: 'carrier', title: 'Atzīmēt piegādātu', text: 'Jūsu uzņēmums jau ir izvēlēts. Norādiet daudzumu, pievienojiet bildi un spiediet Piegādāts.' },
      { sel: '[data-tab="task-list"]', title: 'Saraksts', text: 'Visi pieteikumi un to vēsture.' },
      { sel: '.shx-help', tab: 'carrier', title: 'Izvēlne', text: 'Pamācība, pievienošana sākuma ekrānam un iziešana.' },
      { title: 'Viss gatavs!', text: 'Veiksmīgu darbu!' }
    ]
  }
};
window.SHX.tours.admin = window.SHX.tours.pieteicejs.slice(0, -2).concat([
  { sel: '[data-tab="carrier"]', title: 'Kurjers', text: 'Kurjeru skats — atzīmē piegādātos pieteikumus.' },
  { sel: '[data-tab="analytics"]', title: 'Statistika', text: 'Kopsavilkums pa mēnešiem un materiāliem.' }
]).concat(window.SHX.tours.pieteicejs.slice(-2));
function shxReq(u) {
  var sel = document.getElementById('requester'); if (!sel) return;
  var n = String(u.name || '').toLowerCase(), opts = [].slice.call(sel.options);
  var o = opts.find(function (x) { return x.value.toLowerCase() === n; }) || opts.find(function (x) { return x.value && x.value.toLowerCase().indexOf(n) === 0; });
  if (!o && sel.options.length > 1) { o = new Option(u.name, u.name); sel.add(o); }
  if (o) sel.value = o.value;
  sel.disabled = u.kind !== 'admin' && !!o;
}
/* Kurjeram uzņēmums katrā pieteikumā jau izvēlēts */
function shxSia() {
  var u = window.SHXR && SHXR.user(); if (!u || u.kind !== 'kurjers') return;
  document.querySelectorAll('#carrierContainer select[id^="sia_"]').forEach(function (s) {
    if (![].some.call(s.options, function (o) { return o.value === u.name; })) s.add(new Option(u.name, u.name));
    if (s.value !== u.name) s.value = u.name; s.disabled = true;
  });
}
(function () {
  var cc = document.getElementById('carrierContainer'); if (cc) new MutationObserver(shxSia).observe(cc, { childList: true, subtree: true });
  var sd = window.setupDropdowns; if (sd) window.setupDropdowns = function () { var r = sd.apply(this, arguments); var u = window.SHXR && SHXR.user(); if (u && u.kind !== 'kurjers') shxReq(u); return r; };
  var f = document.getElementById('taskForm'); if (f) f.addEventListener('reset', function () { setTimeout(function () { var u = window.SHXR && SHXR.user(); if (u && u.kind !== 'kurjers') shxReq(u); }, 0); });
})();
</script>
<script src="sh-addon.js?v=%s"></script>
''' % ver
app = open('index.html', encoding='utf-8').read().replace('</body>', shx + '</body>', 1)
open('index.html', 'w', encoding='utf-8').write(app)
print('SHX', ver)
