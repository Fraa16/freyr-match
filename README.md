# Freyr Match

Match-3 mit Freyr, dem weißen Maine Coon. 160 Level, Herz-Truhen, Outfits für Freyr.

**Spielen:** https://fraa16.github.io/freyr-match/

## Als App auf den Homescreen

- **iPhone:** Link in Safari öffnen, auf Teilen tippen, dann auf „Zum Home-Bildschirm“.
- **Android:** Link in Chrome öffnen und im Spiel auf „Installieren“ tippen (oder im Menü „App installieren“).

Danach startet das Spiel im Vollbild mit eigenem Icon und läuft auch ohne Netz.

## Spielstand mitnehmen

Auf der Karte oben rechts auf Freyr tippen, dann „Spielstand sichern oder laden“. Den Code kopieren und auf dem anderen Gerät (oder in der App) einfügen.

## Aufbau

- `docs/` ist die fertige Web-App, die GitHub Pages ausliefert. Nicht von Hand ändern, sie wird gebaut.
- `src/` enthält die Quellen: `game_v17_base.html` plus `patch12.py` (Text-Ersetzungen und die Schichten `game27` bis `game35`), die Level in `levels12.json` und `fix*.json`, die Web-App-Teile `pwa35.*`, `sw35.js`, Schriften und Icons.

## Bauen

```
cd src
python3 patch12.py     # baut src/game.html (die Version fürs Artifact)
python3 mk_site35.py   # baut daraus docs/ (die Web-App)
```

## Tests

Braucht Python 3 und Playwright mit Chromium.

- Alles: `bash src/run12.sh` (etwa 35 Minuten, Ergebnisse in `src/r_*.txt`)
- Einzeln, z. B.: `python3 src/test_save35.py`
- Web-App: `docs/` lokal ausliefern (`python3 -m http.server 8735` im Ordner `docs`), dann `URL=http://localhost:8735/ python3 src/test_site35.py`
- Balancing-Bot: `python3 src/sim30.py 1-160 30 bot.jsonl` (30 Runden pro Level)
