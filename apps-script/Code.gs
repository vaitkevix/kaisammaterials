/*******************************************************
 * Kaisāmmateriāla piegāde — sāls / smilts / mix
 * Google Apps Script backend
 *
 * PIRMO REIZI: izvēlieties funkciju "setupSheets" un nospiediet ▶ Run.
 * Tā izveidos visas vajadzīgās lapas ar virsrakstiem.
 *******************************************************/

// ---------- IESTATĪJUMI ----------
const UNIT = 'maisi';                               // daudzumu skaita maisos
const BAG_KG = 25;                                  // viena maisa svars (jāsakrīt ar Index.html)
const PHOTO_FOLDER = 'Kaisāmmateriāla bildes';      // Drive mape bildēm
const STATUS_PENDING = 'Gaida piegādi';
const STATUS_DONE = 'Piegādāts';

const SHEETS = {
  tasks:      'Pieteikumi',
  addresses:  'Adreses',
  requesters: 'Pasutitaji',
  couriers:   'Kurjeri',
  materials:  'Materiali'
};

// Kolonnas lapā "Pieteikumi" (1 = A)
const COL = {
  id: 1, date: 2, address: 3, requester: 4, material: 5, qtyOrdered: 6,
  comment: 7, photoBefore: 8, status: 9, courier: 10, photoAfter: 11,
  qtyDelivered: 12, courierComment: 13, deliveredAt: 14,
  kgOrdered: 15, kgDelivered: 16           // aprēķina automātiski: maisi × BAG_KG
};
const NUM_COLS = 14;          // nolasa A–N; O un P ir tikai tabulai
const ALL_COLS = 16;
const TASK_HEADERS = [
  'ID', 'Datums', 'Adrese', 'Pasūtītājs', 'Materiāls', 'Pasūtīti maisi',
  'Komentārs', 'Bilde (pieteikums)', 'Statuss', 'Kurjers',
  'Bilde (pēc piegādes)', 'Piegādāti maisi', 'Kurjera komentārs', 'Piegādes laiks',
  'Pasūtīts (kg)', 'Piegādāts (kg)'
];

// ---------- Web lietotne ----------
function doGet() {
  return HtmlService.createHtmlOutputFromFile('Index')
    .setTitle('Kaisāmmateriāla piegāde')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1, viewport-fit=cover')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

// Izpilda formatēšanu, bet neaptur skriptu, ja lapa ir Google Sheets "tabula"
// ar kolonnu tipiem (tur formātu nosaka pati tabula)
// SVARĪGI: SpreadsheetApp.flush() ir iekšā — Google izmaiņas izpilda tikai pie
// nākamās nolasīšanas, tāpēc bez flush kļūda "uzsprāgtu" vēlāk citā vietā.
function safe_(fn) {
  try { fn(); SpreadsheetApp.flush(); }
  catch (e) { Logger.log('Izlaists: ' + e.message); }
}

// ---------- Vienreizēja uzstādīšana ----------
function setupSheets() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  const make = (name, headers, examples) => {
    let sh = ss.getSheetByName(name);
    if (!sh) sh = ss.insertSheet(name);
    if (sh.getLastRow() === 0) {
      sh.getRange(1, 1, 1, headers.length).setValues([headers]);
      safe_(() => sh.getRange(1, 1, 1, headers.length).setFontWeight('bold').setBackground('#dbe8f3'));
      sh.setFrozenRows(1);
      if (examples && examples.length) {
        sh.getRange(2, 1, examples.length, 1).setValues(examples.map(v => [v]));
      }
      safe_(() => sh.autoResizeColumns(1, headers.length));
    }
    return sh;
  };

  make(SHEETS.tasks, TASK_HEADERS);
  make(SHEETS.addresses,  ['Adrese']);
  make(SHEETS.requesters, ['Pasūtītājs', 'Tālrunis']);
  const rq = ss.getSheetByName(SHEETS.requesters);
  if (!rq.getRange(1, 2).getValue()) safe_(() => rq.getRange(1, 2).setValue('Tālrunis'));
  safe_(() => rq.getRange(2, 2, rq.getMaxRows() - 1, 1).setNumberFormat('@'));   // tālruņi kā teksts (saglabā +371)
  make(SHEETS.couriers,   ['Kurjera uzņēmums']);
  make(SHEETS.materials,  ['Materiāls'], ['Sāls', 'Smiltis', 'Sāls/smilts mix']);

  const t = ss.getSheetByName(SHEETS.tasks);
  safe_(() => t.getRange(2, COL.date, t.getMaxRows() - 1, 1).setNumberFormat('dd.MM.yyyy HH:mm'));
  safe_(() => t.getRange(2, COL.deliveredAt, t.getMaxRows() - 1, 1).setNumberFormat('dd.MM.yyyy HH:mm'));
  safe_(() => t.getRange(2, COL.qtyOrdered, t.getMaxRows() - 1, 1).setNumberFormat('0'));
  safe_(() => t.getRange(2, COL.qtyDelivered, t.getMaxRows() - 1, 1).setNumberFormat('0'));
  // Atjauno virsrakstus arī jau esošā tabulā
  safe_(() => t.getRange(1, 1, 1, TASK_HEADERS.length).setValues([TASK_HEADERS]));
  safe_(() => t.getRange(1, 1, 1, TASK_HEADERS.length).setFontWeight('bold').setBackground('#dbe8f3'));

  const cnt = name => Math.max(0, ss.getSheetByName(name).getLastRow() - 1);
  const phones = Object.keys(getPhones_()).length;
  const lines = [
    'Adreses: ' + cnt(SHEETS.addresses),
    'Pasūtītāji: ' + cnt(SHEETS.requesters) + ' (ar tālruni: ' + phones + ')',
    'Kurjeri: ' + cnt(SHEETS.couriers),
    'Materiāli: ' + cnt(SHEETS.materials),
    'Pieteikumi: ' + cnt(SHEETS.tasks)
  ];
  const empty = [SHEETS.addresses, SHEETS.requesters, SHEETS.couriers].filter(n => cnt(n) === 0);
  SpreadsheetApp.getUi().alert(
    (empty.length ? 'Vēl jāaizpilda: ' + empty.join(', ') : '✓ Viss gatavs!') +
    '\n\n' + lines.join('\n') + '\n\n1 maiss = ' + BAG_KG + ' kg');
}

// ---------- Saraksti formām ----------
function getList_(name) {
  const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(name);
  if (!sh || sh.getLastRow() < 2) return [];
  return sh.getRange(2, 1, sh.getLastRow() - 1, 1).getValues()
    .map(r => String(r[0]).trim())
    .filter(Boolean);
}

/** Pieslēgšanās tikai ar paroli: lapa "Kurjeri", kolonna "Parole" (izveido, ja nav). Atgriež kurjera nosaukumu */
function courierByPassword(pw) {
  const p = String(pw == null ? '' : pw).trim().toUpperCase(); if (!p) return '';
  const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEETS.couriers); if (!sh) return '';
  const lc = Math.max(1, sh.getLastColumn());
  const head = sh.getRange(1, 1, 1, lc).getValues()[0].map(h => String(h).trim());
  let c = head.findIndex(h => /^parole/i.test(h));
  if (c < 0) { sh.getRange(1, lc + 1).setValue('Parole').setFontWeight('bold'); Utilities.sleep(800); return ''; }
  const rows = sh.getLastRow() < 2 ? [] : sh.getRange(2, 1, sh.getLastRow() - 1, lc).getValues();
  const m = rows.filter(r => String(r[0]).trim() && String(r[c]).trim().toUpperCase() === p);
  if (m.length === 1) return String(m[0][0]).trim();
  Utilities.sleep(800); return '';
}

// Pasūtītāju tālruņi: lapa "Pasutitaji", A = vārds, B = tālrunis
function getPhones_() {
  const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEETS.requesters);
  const out = {};
  if (!sh || sh.getLastRow() < 2) return out;
  let rows = [];
  try { rows = sh.getRange(2, 1, sh.getLastRow() - 1, 2).getDisplayValues(); }
  catch (e) { Logger.log('Tālruņus neizdevās nolasīt: ' + e.message); return out; }
  rows.forEach(r => {
    const name = String(r[0]).trim();
    let tel = String(r[1]).trim().replace(/\.0$/, '');
    if (/^\d{8}$/.test(tel)) tel = '+371 ' + tel;   // 8 cipari bez +371 (piem., ja kolonna ir 'Skaitlis')
    if (name && tel) out[name] = tel;
  });
  return out;
}

function getInitialData() {
  return {
    addresses: getList_(SHEETS.addresses),
    people:    getList_(SHEETS.requesters),
    siaList:   getList_(SHEETS.couriers),
    materials: getList_(SHEETS.materials),
    phones:    getPhones_()
  };
}

// ---------- Bildes ----------
function getPhotoFolder_() {
  const it = DriveApp.getFoldersByName(PHOTO_FOLDER);
  return it.hasNext() ? it.next() : DriveApp.createFolder(PHOTO_FOLDER);
}

function saveFileToDrive(base64Data, filename) {
  if (!base64Data || !base64Data.includes('base64,')) return base64Data || '';
  try {
    const parts = base64Data.split('base64,');
    const contentType = parts[0].split(':')[1].split(';')[0];
    const blob = Utilities.newBlob(Utilities.base64Decode(parts[1]), contentType, filename);
    const file = getPhotoFolder_().createFile(blob);
    file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
    return file.getUrl();
  } catch (err) {
    Logger.log('Drive kļūda: ' + err);
    return '';
  }
}

function getTaskSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(SHEETS.tasks);
  if (!sh) {
    sh = ss.insertSheet(SHEETS.tasks);
    sh.appendRow(TASK_HEADERS);
    safe_(() => sh.getRange(1, 1, 1, ALL_COLS).setFontWeight('bold').setBackground('#dbe8f3'));
    sh.setFrozenRows(1);
  }
  return sh;
}

function toNum_(v) {
  const n = parseFloat(String(v || '').replace(',', '.'));
  return isNaN(n) ? '' : n;
}

// ---------- Jauns pieteikums ----------
function saveTask(taskData) {
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
    const sheet = getTaskSheet_();

    // ID var atnākt no ātrās versijas (Cloudflare), lai atkārtota sūtīšana neveidotu dublikātu
    const newId = /^KM-\d{10,}$/.test(String(taskData.id || '')) ? String(taskData.id) : 'KM-' + new Date().getTime();
    if (taskData.id) {
      const ids = sheet.getLastRow() > 1 ? sheet.getRange(2, COL.id, sheet.getLastRow() - 1, 1).getValues().map(r => String(r[0])) : [];
      if (ids.indexOf(newId) !== -1) return { status: 'success', id: newId };
    }
    const photoUrl = taskData.photo ? saveFileToDrive(taskData.photo, newId + '_Pieteikums.jpg') : '';

    const row = new Array(NUM_COLS).fill('');
    row[COL.id - 1]          = newId;
    row[COL.date - 1]        = new Date();
    row[COL.address - 1]     = taskData.address || '';
    row[COL.requester - 1]   = taskData.requester || '';
    row[COL.material - 1]    = taskData.material || '';
    row[COL.qtyOrdered - 1]  = toNum_(taskData.bagsEst);
    row[COL.comment - 1]     = taskData.comment || '';
    row[COL.photoBefore - 1] = photoUrl;
    row[COL.status - 1]      = STATUS_PENDING;

    row.push('', '');
    sheet.appendRow(row);
    const nr = sheet.getLastRow();
    safe_(() => sheet.getRange(nr, COL.kgOrdered).setFormula('=IF(F' + nr + '="";"";F' + nr + '*' + BAG_KG + ')'));
    safe_(() => sheet.getRange(nr, COL.kgDelivered).setFormula('=IF(L' + nr + '="";"";L' + nr + '*' + BAG_KG + ')'));
    SpreadsheetApp.flush();
    return { status: 'success', id: newId };
  } catch (e) {
    return { status: 'error', message: e.toString() };
  } finally {
    lock.releaseLock();
  }
}

// ---------- Visi pieteikumi ----------
function getTasks() {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEETS.tasks);
    if (!sheet || sheet.getLastRow() < 2) return [];

    const data = sheet.getRange(2, 1, sheet.getLastRow() - 1, NUM_COLS).getValues();
    const tz = Session.getScriptTimeZone();
    const fmtDate = v => v instanceof Date ? Utilities.formatDate(v, tz, 'dd.MM.yyyy HH:mm') : String(v || '');
    const s = v => (v === null || v === undefined) ? '' : String(v);

    return data
      .map((r, i) => ({
        rowIndex:       i + 2,
        id:             s(r[COL.id - 1]),
        date:           fmtDate(r[COL.date - 1]),
        address:        s(r[COL.address - 1]),
        requester:      s(r[COL.requester - 1]),
        material:       s(r[COL.material - 1]),
        bagsEst:        s(r[COL.qtyOrdered - 1]),     // pasūtītais daudzums
        comment:        s(r[COL.comment - 1]),
        photoBefore:    s(r[COL.photoBefore - 1]),
        status:         s(r[COL.status - 1]) || STATUS_PENDING,
        sia:            s(r[COL.courier - 1]),
        photoAfter:     s(r[COL.photoAfter - 1]),
        m3Hauled:       s(r[COL.qtyDelivered - 1]),   // piegādātais daudzums
        carrierComment: s(r[COL.courierComment - 1]),
        deliveredAt:    fmtDate(r[COL.deliveredAt - 1])
      }))
      .filter(t => t.id);   // izlaiž tukšas rindas
  } catch (e) {
    Logger.log('Kļūda ielādējot pieteikumus: ' + e);
    return [];
  }
}

// ---------- Kurjers atzīmē piegādi ----------
function completeTask(data) {
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEETS.tasks);
    if (!sheet) return { status: 'error', message: 'Lapa "' + SHEETS.tasks + '" netika atrasta' };

    const r = parseInt(data.rowIndex, 10);
    if (!r || r < 2 || r > sheet.getLastRow()) return { status: 'error', message: 'Pieteikums netika atrasts' };

    const current = sheet.getRange(r, 1, 1, NUM_COLS).getValues()[0];
    if (current[COL.status - 1] === STATUS_DONE) {
      return { status: 'error', message: 'Šis pieteikums jau ir atzīmēts kā piegādāts' };
    }

    let photoAfterUrl = data.photoAfter || '';
    if (photoAfterUrl.startsWith('data:image')) {
      photoAfterUrl = saveFileToDrive(photoAfterUrl, current[COL.id - 1] + '_Piegadats.jpg');
    }

    sheet.getRange(r, COL.status).setValue(STATUS_DONE);
    sheet.getRange(r, COL.courier).setValue(data.sia || '');
    if (photoAfterUrl) sheet.getRange(r, COL.photoAfter).setValue(photoAfterUrl);
    sheet.getRange(r, COL.qtyDelivered).setValue(toNum_(data.m3Hauled));
    sheet.getRange(r, COL.courierComment).setValue(data.carrierComment || '');
    sheet.getRange(r, COL.deliveredAt).setValue(new Date());

    SpreadsheetApp.flush();
    return { status: 'success' };
  } catch (e) {
    return { status: 'error', message: e.toString() };
  } finally {
    lock.releaseLock();
  }
}

// ================================================================
//  ĀTRĀ VERSIJA (Cloudflare) — tilts. © VAITKEVIX, SIA
//  Lietotne (GitHub) → Cloudflare Worker → šeit. Google tabula paliek galvenā.
//  Script properties: BRIDGE_KEY (tā pati atslēga, kas Cloudflare).
// ================================================================
const BRIDGE_MAP_ = { getTasks: getTasks, getInitialData: getInitialData, saveTask: saveTask, completeTask: completeTask, saveFileToDrive: saveFileToDrive, courierByPassword: courierByPassword };

function doPost(e) {
  const out = (o) => ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
  try {
    const p = (e && e.parameter) || {};
    const key = PropertiesService.getScriptProperties().getProperty('BRIDGE_KEY');
    if (!key || p.key !== key) return out({ ok: false, error: 'Nav atļauts' });
    const fn = Object.prototype.hasOwnProperty.call(BRIDGE_MAP_, p.fn) ? BRIDGE_MAP_[p.fn] : null;
    if (!fn) return out({ ok: false, error: 'Nezināma darbība' });
    const args = e.postData && e.postData.contents ? JSON.parse(e.postData.contents) : [];
    return out({ ok: true, result: fn.apply(null, Array.isArray(args) ? args : []) });
  } catch (err) {
    return out({ ok: false, error: String(err && err.message || err) });
  }
}
