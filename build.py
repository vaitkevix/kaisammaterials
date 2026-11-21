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
      var t = ''; try { t = localStorage.getItem('sh_t') || ''; } catch (e) {}   // portāla sesija — mainīt var tikai ielogojies
      fetch(API + '?fn=' + encodeURIComponent(fn) + (t ? '&t=' + encodeURIComponent(t) : ''), { method: 'POST', headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: JSON.stringify(args) })
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
shx = '''<style>@media(max-width:420px){.t-long{display:none}}@media(min-width:421px){.t-short{display:none}}</style><script>
window.SHX = {
  app: 'kais', title: 'Jauns pieteikums', api: 'https://aizvietosana-api.vaitkevix.workers.dev', icon: 'icon.png',
  sub: 'Lai pieteiktu, ievadiet savu PIN kodu', hint: 'Tas pats PIN, kas Aizvietošanā.',
  gateIn: '#new-task', ownMenu: '.actions', a2hs: true,
  homeTab: function (k) { return k === 'kurjers' ? 'carrier' : 'new-task'; },
  tourKind: function (u) { return state.tab === 'carrier' && state.unlocked ? 'kurjers' : (u && u.kind === 'admin' ? 'admin' : 'pieteicejs'); },
  loggedIn: function () { return !!state.unlocked; },
  switchTab: function (t) { switchTab(t); },
  onUser: function (u) { shxReq(u); },
  onOut: function () { shxCourierOut(); },
  tours: {
    pieteicejs: [
      { title: 'Sveiki!', text: 'Īsa pamācība, kā pieteikt kaisāmmateriālu. Aizņems pusminūti.' },
      { sel: '#tabs', title: 'Cilnes', text: 'Jauns — pieteikt piegādi. Saraksts — visi pieteikumi un statuss. Kurjers — kurjeriem. Statistika — kopsavilkums.' },
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
      { sel: '.shx-help', tab: 'carrier', title: 'Izvēlne', text: 'Pamācība, pievienošana sākuma ekrānam un iziešana.' },
      { title: 'Viss gatavs!', text: 'Veiksmīgu darbu!' }
    ]
  }
};
window.SHX.tours.admin = window.SHX.tours.pieteicejs;
function shxReq(u) {
  var sel = document.getElementById('requester'); if (!sel || !u) return;
  var n = String(u.name || '').toLowerCase(), opts = [].slice.call(sel.options);
  var o = opts.find(function (x) { return x.value.toLowerCase() === n; }) || opts.find(function (x) { return x.value && x.value.toLowerCase().indexOf(n) === 0; });
  if (!o && sel.options.length > 1) { o = new Option(u.name, u.name); sel.add(o); }
  if (o) sel.value = o.value;
  sel.disabled = u.kind !== 'admin' && !!o;
}
/* Kurjers: tikai sava uzņēmuma (SIA) parole; uzņēmums katrā pieteikumā jau izvēlēts */
function shxCourier() { try { return localStorage.getItem('shx_kais_courier') || ''; } catch (e) { return ''; } }
function shxSia() {
  var c = shxCourier(); if (!c || !state.unlocked) return;
  document.querySelectorAll('#carrierContainer select[id^="sia_"]').forEach(function (s) {
    if (![].some.call(s.options, function (o) { return o.value === c; })) s.add(new Option(c, c));
    if (s.value !== c) s.value = c; s.disabled = true;
  });
}
function shxCourierOut() { try { localStorage.removeItem('shx_kais_courier'); sessionStorage.removeItem('carrierOk'); } catch (e) {} state.unlocked = false; try { renderCarrierList(); } catch (e) {} }
var shxOldPin = window.checkCarrierPin;
window.checkCarrierPin = function () {
  var inp = document.getElementById('carrierPinInput'), pw = inp.value.trim(); if (!pw) return inp.focus();
  SHXR.who(pw).then(function (u) {
    if (u.kind !== 'kurjers') throw new Error('Ievadiet sava uzņēmuma (SIA) paroli');
    try { localStorage.setItem('shx_kais_courier', u.name); sessionStorage.setItem('carrierOk', '1'); } catch (e) {}
    state.unlocked = true; renderCarrierList(); SHXR.maybeTourKind('kurjers');
  }).catch(function (err) {
    if (err.message === 'Nepareizs PIN') return shxOldPin();   // pagaidām der arī vecā kopējā parole
    var card = document.getElementById('lockCard'); if (card) { card.classList.remove('shake'); void card.offsetWidth; card.classList.add('shake'); }
    inp.value = ''; toast(/fetch|network/i.test(err.message) ? 'Nav interneta' : err.message, 'err');
  });
};
(function () {
  if (location.hash === '#carrier') { var st = document.createElement('style'); st.textContent = '#tabs .tab[data-tab="new-task"],#tabs .tab[data-tab="analytics"]{display:none!important}'; document.head.appendChild(st);
    setTimeout(function () { switchTab('carrier'); if (typeof moveTabInd === 'function') moveTabInd(); }, 60); }
  try { if (shxCourier()) { state.unlocked = true; } } catch (e) {}
  var cc = document.getElementById('carrierContainer'); if (cc) new MutationObserver(shxSia).observe(cc, { childList: true, subtree: true });
  var sd = window.setupDropdowns; if (sd) window.setupDropdowns = function () { var r = sd.apply(this, arguments); shxReq(SHXR.user()); return r; };
  var f = document.getElementById('taskForm'); if (f) f.addEventListener('reset', function () { setTimeout(function () { shxReq(SHXR.user()); }, 0); });
})();
</script>
<script src="sh-addon.js?v=%s"></script>
''' % ver
app = open('index.html', encoding='utf-8').read().replace('</body>', shx + '</body>', 1)
open('index.html', 'w', encoding='utf-8').write(app)
print('SHX', ver)

# SH kopīgā tēma (sh-theme.css) — vienots izskats ar SH portālu
import re as _re
_s = open('index.html', encoding='utf-8').read()
_s = _re.sub(r'\n?<!--SH-THEME-->.*?<!--/SH-THEME-->', '', _s, flags=_re.S)
_s = _s.replace('</head>', '\n<!--SH-THEME--><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&display=swap"><link rel="stylesheet" href="sh-theme.css?v=2"><script>/*SH tēma: kopīga ar portālu (sh_theme), mainās uzreiz*/(function(d){d.setAttribute("data-sh","kais");function a(t){d.setAttribute("data-theme",t==="dark"?"dark":"light")}try{a(localStorage.getItem("sh_theme"))}catch(e){}addEventListener("storage",function(e){if(e.key==="sh_theme")a(e.newValue)});addEventListener("message",function(e){var m=e.data;if(e.origin===location.origin&&m&&m.sh==="theme")a(m.t)})})(document.documentElement)</script><!--/SH-THEME-->\n</head>', 1)
open('index.html', 'w', encoding='utf-8').write(_s)
