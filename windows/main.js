// CURIOUS XXL — Windows-versie (Electron) rond dezelfde catalogus als de Mac-app
const { app, BrowserWindow, ipcMain, dialog, shell, protocol, net, Menu } = require('electron');
const path = require('path');
const fs = require('fs');
const fsp = fs.promises;
const os = require('os');
const { spawn } = require('child_process');
const { pathToFileURL } = require('url');

app.setName('CURIOUS XXL');
app.setAppUserModelId('nl.hankoopman.playlistxxl');
// gegevens van de vorige naam meenemen
try {
  const oldDir = path.join(app.getPath('appData'), 'Playlist XXL', 'data');
  const newDir = path.join(app.getPath('appData'), 'CURIOUS XXL', 'data');
  app.setPath('userData', path.join(app.getPath('appData'), 'CURIOUS XXL'));
  if (!fs.existsSync(newDir) && fs.existsSync(oldDir)) fs.cpSync(oldDir, newDir, { recursive: true });
} catch {}
// links uit de handleiding: curiousxxl://
const LINK = 'curiousxxl';
const exePath = process.env.PORTABLE_EXECUTABLE_FILE || process.execPath;
if (process.defaultApp) app.setAsDefaultProtocolClient(LINK, process.execPath, [path.resolve(process.argv[1] || '.')]);
else app.setAsDefaultProtocolClient(LINK, exePath, []);
const linkIn = argv => (argv || []).find(a => typeof a === 'string' && a.toLowerCase().startsWith(LINK + '://'));
let pageReady = false; const pending = [];
let lastLink = '', lastAt = 0;
function openLink(url) {
  if (!url) return;
  const now = Date.now(); if (url === lastLink && now - lastAt < 1500) return; lastLink = url; lastAt = now;
  if (!pageReady || !win) { pending.push(url); return; }
  win.webContents.executeJavaScript(`window.__pxxlLink && window.__pxxlLink(${JSON.stringify(url)})`).catch(() => {});
}
if (!app.requestSingleInstanceLock()) { app.quit(); }
const startLink = linkIn(process.argv);
if (startLink) pending.push(startLink);

protocol.registerSchemesAsPrivileged([
  { scheme: 'pxxl-media', privileges: { standard: true, secure: true, stream: true, supportFetchAPI: true, bypassCSP: true } }
]);

const AUDIO = new Set(['.mp3', '.m4a', '.aac', '.wav', '.flac', '.aif', '.aiff', '.ogg']);
let mm = null; // music-metadata, pas laden bij gebruik
let win;

const dataDir = () => { const d = path.join(app.getPath('userData'), 'data'); fs.mkdirSync(d, { recursive: true }); return d; };
const storeFile = () => path.join(dataDir(), 'catalogus.json');
const expand = p => (p || '').replace(/^~(?=$|[\\/])/, os.homedir()).replace(/\//g, path.sep);

function defaultMusic() {
  const cands = [path.join(app.getPath('music'), 'MP3'), app.getPath('music'), os.homedir()];
  return cands.find(c => { try { return fs.statSync(c).isDirectory(); } catch { return false; } });
}

async function walk(root) {
  const out = [];
  const stack = [root];
  while (stack.length) {
    const dir = stack.pop();
    let entries;
    try { entries = await fsp.readdir(dir, { withFileTypes: true }); } catch { continue; }
    for (const e of entries) {
      if (e.name.startsWith('.') || e.name.startsWith('$')) continue;
      const full = path.join(dir, e.name);
      if (e.isDirectory()) stack.push(full);
      else if (e.isFile() && AUDIO.has(path.extname(e.name).toLowerCase())) {
        out.push({ rel: path.relative(root, full).split(path.sep).join('/'), path: full });
      }
    }
  }
  return out;
}

async function readTags(p) {
  if (!mm) mm = require('music-metadata');
  const d = {};
  try {
    const r = await mm.parseFile(p, { skipCovers: true, duration: false });
    const c = r.common || {}, f = r.format || {};
    if (c.title) d.title = String(c.title);
    if (c.artist) d.artist = String(c.artist);
    if (c.year && c.year > 1000 && c.year < 2100) d.year = c.year;
    if (Array.isArray(c.genre) && c.genre.length) d.genre = String(c.genre[0]);
    if (c.bpm && isFinite(+c.bpm) && +c.bpm > 20 && +c.bpm < 400) d.bpm = Math.round(+c.bpm);
    if (c.key && String(c.key).length <= 8) d.key = String(c.key).trim();
    let dur = f.duration;
    if (!(dur > 0) && f.bitrate > 0) { try { dur = (fs.statSync(p).size * 8) / f.bitrate; } catch {} }
    if (dur > 0 && dur < 86400) d.dur = dur;
  } catch { /* onleesbaar bestand: lege tags, de app loopt door */ }
  return d;
}

async function mapLimit(items, n, fn) {
  const res = new Array(items.length); let i = 0;
  await Promise.all(Array.from({ length: n }, async () => { while (i < items.length) { const k = i++; res[k] = await fn(items[k]); } }));
  return res;
}

function runClaude(prompt) {
  return new Promise((resolve, reject) => {
    const child = spawn('claude', ['-p', '--output-format', 'text'], { shell: true, windowsHide: true, env: process.env });
    let out = '', err = '';
    child.stdout.on('data', b => out += b);
    child.stderr.on('data', b => err += b);
    child.on('error', () => reject({ code: 'missing' }));
    child.on('close', code => {
      if (code === 0) resolve(out);
      else if (/not recognized|not found|niet herkend|ENOENT/i.test(err)) reject({ code: 'missing' });
      else reject({ code: 'failed', message: err.slice(0, 300) });
    });
    child.stdin.end(prompt);
  });
}

const handlers = {
  async storeLoad() { try { return await fsp.readFile(storeFile(), 'utf8'); } catch { return null; } },
  async storeSave({ data }) {
    const tmp = storeFile() + '.tmp';
    await fsp.writeFile(tmp, data || '', 'utf8');
    await fsp.rename(tmp, storeFile());
    const day = new Date().toLocaleDateString('sv-SE');
    const backup = path.join(dataDir(), `reserve-${day}.json`);
    if (!fs.existsSync(backup)) await fsp.writeFile(backup, data || '', 'utf8');
    return true;
  },
  async chooseFolder({ start }) {
    let def = start ? expand(start) : null;
    if (!def || !fs.existsSync(def)) def = defaultMusic();
    const r = await dialog.showOpenDialog(win, { title: 'Kies je muziekmap', buttonLabel: 'Koppel', defaultPath: def, properties: ['openDirectory'] });
    return r.canceled || !r.filePaths.length ? null : r.filePaths[0];
  },
  async scan({ root }) {
    const r = expand(root);
    await fsp.access(r);
    return walk(r);
  },
  async tags({ paths }) { return mapLimit(paths || [], 8, readTags); },
  async copyToDesktop({ folder, files, extra }) {
    const desk = app.getPath('desktop');
    const base = String(folder || 'CURIOUS XXL').replace(/[\\/:*?"<>|]+/g, '-');
    let dest = path.join(desk, base), k = 2;
    while (fs.existsSync(dest)) dest = path.join(desk, `${base} (${k++})`);
    await fsp.mkdir(dest, { recursive: true });
    for (const f of files || []) await fsp.copyFile(f.src, path.join(dest, f.name));
    for (const e of extra || []) await fsp.writeFile(path.join(dest, e.name), e.text, 'utf8');
    shell.openPath(dest);
    return path.basename(dest);
  },
  async saveFile({ name, text }) {
    const r = await dialog.showSaveDialog(win, { defaultPath: path.join(app.getPath('desktop'), name || 'curious-xxl.txt') });
    if (r.canceled || !r.filePath) return false;
    await fsp.writeFile(r.filePath, text || '', 'utf8');
    return true;
  },
  async claude({ prompt }) { return runClaude(prompt || ''); },
  async manual() { openManual(); return true; }
};

ipcMain.handle('pxxl', async (_e, msg) => {
  const fn = handlers[msg && msg.cmd];
  if (!fn) throw new Error('onbekende opdracht');
  try { return { ok: true, value: await fn(msg.args || {}) }; }
  catch (e) { return { ok: false, value: e && e.code ? e : String((e && e.message) || e) }; }
});

const manualPath = () => app.isPackaged ? path.join(process.resourcesPath, 'CURIOUS XXL - Handleiding.pdf') : path.join(__dirname, 'CURIOUS XXL - Handleiding.pdf');
let manualWin = null;
function openManual() {
  if (manualWin && !manualWin.isDestroyed()) { manualWin.show(); manualWin.focus(); return; }
  const b = win ? win.getBounds() : { x: 80, y: 60, height: 920 };
  manualWin = new BrowserWindow({
    width: 780, height: Math.max(700, b.height), x: Math.max(0, b.x - 380), y: b.y,
    title: 'CURIOUS XXL · Handleiding', backgroundColor: '#10151D', autoHideMenuBar: true,
    icon: path.join(__dirname, 'build', 'icon.png'),
    webPreferences: { plugins: true, contextIsolation: true, nodeIntegration: false }
  });
  const wc = manualWin.webContents;
  const catchLink = (e, url) => {
    if (typeof url !== 'string') return;
    if (url.toLowerCase().startsWith(LINK + '://')) { if (e && e.preventDefault) e.preventDefault(); if (win) win.showInactive && win.show(); openLink(url); }
    else if (/^https?:/i.test(url)) { if (e && e.preventDefault) e.preventDefault(); shell.openExternal(url); }
  };
  wc.on('will-navigate', catchLink);
  wc.on('will-frame-navigate', d => catchLink(d, d.url));
  wc.setWindowOpenHandler(({ url }) => { catchLink(null, url); return { action: 'deny' }; });
  manualWin.loadURL(pathToFileURL(manualPath()).toString());
}

function createWindow() {
  win = new BrowserWindow({
    width: 1440, height: 920, minWidth: 900, minHeight: 600,
    title: 'CURIOUS XXL', backgroundColor: '#10151D',
    icon: path.join(__dirname, 'build', 'icon.png'),
    autoHideMenuBar: true,
    webPreferences: { preload: path.join(__dirname, 'preload.js'), contextIsolation: false, nodeIntegration: false, sandbox: false }
  });
  win.webContents.setWindowOpenHandler(({ url }) => { if (/^https?:/.test(url)) shell.openExternal(url); return { action: 'deny' }; });
  win.webContents.on('will-navigate', (e, url) => { if (/^https?:/.test(url)) { e.preventDefault(); shell.openExternal(url); } });
  win.webContents.on('did-finish-load', () => setTimeout(() => { pageReady = true; pending.splice(0).forEach(openLink); }, 800));
  win.webContents.on('did-start-loading', () => { pageReady = false; });
  win.loadFile(path.join(__dirname, 'index.html'));
}

app.on('second-instance', (_e, argv) => { if (win) { if (win.isMinimized()) win.restore(); win.focus(); } openLink(linkIn(argv)); });

app.whenReady().then(() => {
  protocol.handle(LINK, req => { openLink(req.url); return new Response(null, { status: 204 }); });
  protocol.handle('pxxl-media', req => {
    const p = decodeURIComponent(new URL(req.url).searchParams.get('p') || '');
    return net.fetch(pathToFileURL(p).toString(), { headers: req.headers });
  });
  Menu.setApplicationMenu(Menu.buildFromTemplate([
    { label: 'Bestand', submenu: [
      { label: 'Toon catalogusmap', click: () => shell.openPath(dataDir()) },
      { type: 'separator' },
      { label: 'Stoppen', role: 'quit' }
    ] },
    { label: 'Wijzig', submenu: [
      { label: 'Herstel', role: 'undo' }, { label: 'Opnieuw', role: 'redo' }, { type: 'separator' },
      { label: 'Knip', role: 'cut' }, { label: 'Kopieer', role: 'copy' }, { label: 'Plak', role: 'paste' },
      { label: 'Selecteer alles', role: 'selectAll' }
    ] },
    { label: 'Weergave', submenu: [
      { label: 'Ververs', role: 'reload' }, { type: 'separator' },
      { label: 'Groter', role: 'zoomIn' }, { label: 'Kleiner', role: 'zoomOut' }, { label: 'Ware grootte', role: 'resetZoom' },
      { type: 'separator' }, { label: 'Volledig scherm', role: 'togglefullscreen' }
    ] },
    { label: 'Help', submenu: [
      { label: 'Handleiding CURIOUS XXL', accelerator: 'F1', click: () => {
        openManual();
      } }
    ] }
  ]));
  createWindow();
});
app.on('window-all-closed', () => app.quit());
