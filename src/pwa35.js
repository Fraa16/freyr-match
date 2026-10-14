/* ===================== web app (GitHub Pages build only): offline, and a hint how to put it on the home screen ===================== */
(() => {
  if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost')) {
    addEventListener('load', () => { navigator.serviceWorker.register('sw.js').catch(() => {}); });
  }
  const standalone = () => !!navigator.standalone || matchMedia('(display-mode: standalone)').matches || matchMedia('(display-mode: fullscreen)').matches;
  const ios = /iPhone|iPad|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  const touch = matchMedia('(pointer: coarse)').matches;
  const OFF = 'wmx-a2hs-off';
  let deferred = null;
  const off = () => { try { return !!localStorage.getItem(OFF); } catch (e) { return false; } };
  const SHARE = '<svg class="a2share" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12M7.5 7.5 12 3l4.5 4.5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/><path d="M8 10.5H6.5A1.5 1.5 0 0 0 5 12v7.5A1.5 1.5 0 0 0 6.5 21h11a1.5 1.5 0 0 0 1.5-1.5V12a1.5 1.5 0 0 0-1.5-1.5H16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>';
  const box = document.createElement('div');
  box.className = 'a2hs'; box.id = 'a2hs'; box.hidden = true; box.setAttribute('role', 'note');
  document.getElementById('mapScreen').appendChild(box);
  const draw = () => {
    if (deferred) {
      box.innerHTML = '<span class="a2t"><b>Freyr Match als App</b>Mit Icon auf dem Homescreen, im Vollbild.</span><button class="a2go" type="button">Installieren</button><button class="a2x" type="button" aria-label="Hinweis schließen">×</button>';
      box.querySelector('.a2go').onclick = async () => { const d = deferred; deferred = null; box.hidden = true; try { d.prompt(); await d.userChoice; } catch (e) {} };
    } else {
      box.innerHTML = '<span class="a2t"><b>Freyr Match als App</b>Tippe auf ' + SHARE + ' Teilen und dann auf „Zum Home-Bildschirm“.</span><button class="a2x" type="button" aria-label="Hinweis schließen">×</button>';
    }
    box.querySelector('.a2x').onclick = () => { box.hidden = true; try { localStorage.setItem(OFF, '1'); } catch (e) {} };
  };
  const show = () => {
    if (standalone() || off()) { box.hidden = true; return; }
    if (!deferred && !(ios && touch)) { box.hidden = true; return; }
    draw(); box.hidden = false;
  };
  addEventListener('beforeinstallprompt', e => { e.preventDefault(); deferred = e; show(); });
  addEventListener('appinstalled', () => { box.hidden = true; try { localStorage.setItem(OFF, '1'); } catch (e) {} });
  // only on the map, and not while the very first start (the wake-up) is still running
  const showMapPlain = showMap;
  showMap = function (...a) { const r = showMapPlain.apply(this, a); setTimeout(show, 1200); return r; };
  if (!document.getElementById('mapScreen').hidden) setTimeout(show, 1600);
})();
