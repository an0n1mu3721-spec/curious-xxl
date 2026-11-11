// Dezelfde brug als in de Mac-app: de pagina praat via window.webkit.messageHandlers.pxxl
const { ipcRenderer } = require('electron');

window.webkit = {
  messageHandlers: {
    pxxl: {
      postMessage(m) {
        ipcRenderer.invoke('pxxl', m).then(
          r => window.__pxxlReply(m.id, r.ok, r.value),
          e => window.__pxxlReply(m.id, false, String(e))
        );
      }
    }
  }
};
window.PXXL_MEDIA = p => 'pxxl-media://f/?p=' + encodeURIComponent(p);
