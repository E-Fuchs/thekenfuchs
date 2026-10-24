#!/usr/bin/env python3
"""Baut den Thekenfuchs.

  dist/site/            – Inhalt für GitHub Pages unter /thekenfuchs/
      app/              – installierbare Web-App (Manifest, Service Worker, offline)
      demo/             – Demo zum Ausprobieren (Speicher nur im RAM, kein Service Worker)
      install/thekenfuchs.mobileconfig – Installationsprofil (Web Clip) auf die App-Adresse
      + alles aus ./site (Startseite, Installationsseite, Bilder)
  dist/release/         – thekenfuchs.zip (App zum Download/lokal unter Windows) + Profil
  dist/artifact/        – einzelne Testseite (ohne Kamera, ohne Offline)

  python3 build.py [--url https://…/app/] [--version 1.0.0] [--removable]
"""
import base64, json, hashlib, shutil, zipfile, datetime, argparse, plistlib, uuid, io
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).parent
SRC, DIST, SITE = ROOT / "src", ROOT / "dist", ROOT / "site"
VEN = ROOT / "node_modules" if (ROOT / "node_modules").exists() else ROOT / "vendor" / "node_modules"
VERSION = datetime.datetime.now().strftime("%Y.%m.%d-%H%M") + "-dev"
DEFAULT_URL = "https://e-fuchs.github.io/thekenfuchs/app/"
NAME = "Thekenfuchs"
TAGLINE = "Antippen statt Kopfrechnen – Thekenrechner für Vereinsfeste"
FEATURES = "Produkte mit Preisen auf Tasten · Pfandautomatik · Rückgeld auf einen Blick · Preisliste per QR auf alle Geräte verteilbar"
DISCLAIMER = "Rechenhilfe, keine Kasse: Der Thekenfuchs speichert keine Verkäufe."
DESCRIPTION = ("Antippen statt Kopfrechnen – Thekenrechner für Vereinsfeste. Offline-Web-App für Tablet und "
               "Smartphone (iPad, Android, Windows): Produkte mit Preisen auf Tasten, Pfandautomatik, Rückgeld "
               "auf einen Blick, Preisliste per QR auf alle Geräte verteilbar. Rechenhilfe, keine Kasse – "
               "speichert keine Verkäufe.")

FONTS = [
    ("Barlow Condensed", 600, "@fontsource/barlow-condensed/files/barlow-condensed-latin-600-normal.woff2"),
    ("Barlow Condensed", 700, "@fontsource/barlow-condensed/files/barlow-condensed-latin-700-normal.woff2"),
    ("Barlow", 400, "@fontsource/barlow/files/barlow-latin-400-normal.woff2"),
    ("Barlow", 500, "@fontsource/barlow/files/barlow-latin-500-normal.woff2"),
    ("Barlow", 600, "@fontsource/barlow/files/barlow-latin-600-normal.woff2"),
]

def font_css():
    out = []
    for fam, w, rel in FONTS:
        b64 = base64.b64encode((VEN / rel).read_bytes()).decode()
        out.append(f'@font-face{{font-family:"{fam}";font-weight:{w};font-style:normal;font-display:swap;'
                   f'src:url(data:font/woff2;base64,{b64}) format("woff2")}}')
    return "\n".join(out)

def lib(rel):
    code = (VEN / rel).read_text()
    return "<script>\n" + code.replace("</script", "<\\/script") + "\n</script>"

def build(variant: str, icon_b64: str = "") -> str:
    """variant: 'artifact' | 'app' | 'demo'"""
    pwa = variant in ("app", "demo")
    head = (SRC / "head.html").read_text().replace("/*@FONTS@*/", font_css())
    body = (SRC / "body.html").read_text()
    libs = [lib("qrcode-generator/qrcode.js")]
    if pwa:
        libs.append(lib("jsqr/dist/jsQR.js"))
    body = body.replace("<!--@LIBS@-->", "\n".join(libs))
    meta = {'pwa': pwa, 'demo': variant == "demo", 'version': VERSION}
    if variant == "app" and icon_b64:
        meta['icon'] = icon_b64
    body = body.replace("/*@BUILD@*/", f"window.__BUILD__={json.dumps(meta)};")
    if not pwa:
        return head + "\n" + body
    csp = ("default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
           "img-src 'self' data: blob:; font-src 'self' data:; media-src 'self' blob: mediastream:; "
           "connect-src 'none'; worker-src 'self'; manifest-src 'self'; base-uri 'none'; form-action 'none'; object-src 'none'")
    if variant == "app":
        links = """<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Thekenfuchs">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-180.png">
<link rel="icon" href="icon-192.png">"""
    else:
        links = """<meta name="robots" content="noindex">
<link rel="icon" href="../app/icon-192.png">"""
    pwa_head = f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="{csp}">
<meta name="theme-color" content="#0E6A4C">
{links}
<style>:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}</style>"""
    if variant == "demo":
        head = head.replace("<title>Thekenfuchs</title>", "<title>Thekenfuchs – Demo</title>")
    return f'<!doctype html>\n<html lang="de">\n<head>\n{pwa_head}\n{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n'

def icon(size, maskable=False):
    s = 1024
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    green = (14, 106, 76, 255)
    if maskable:
        d.rectangle([0, 0, s, s], fill=green)
    else:
        d.rounded_rectangle([0, 0, s - 1, s - 1], radius=220, fill=green)
    # Wertmarke mit seitlichen Kerben
    inset = 250 if maskable else 190
    x0, y0, x1, y1 = inset, int(s * 0.30), s - inset, int(s * 0.70)
    d.rounded_rectangle([x0, y0, x1, y1], radius=40, fill=(255, 255, 255, 255))
    r, cy = 46, (y0 + y1) // 2 + 40
    d.ellipse([x0 - r, cy - r, x0 + r, cy + r], fill=green)
    d.ellipse([x1 - r, cy - r, x1 + r, cy + r], fill=green)
    # Kopfband + Perforation
    d.rounded_rectangle([x0, y0, x1, y0 + 70], radius=40, fill=(211, 90, 34, 255))
    d.rectangle([x0, y0 + 40, x1, y0 + 70], fill=(211, 90, 34, 255))
    for x in range(x0 + 70, x1 - 60, 56):
        d.rectangle([x, cy - 6, x + 28, cy + 6], fill=green)
    # Plus
    cx, py = s // 2, y0 + 70 + (cy - 6 - (y0 + 70)) // 2
    d.rectangle([cx - 70, py - 16, cx + 70, py + 16], fill=green)
    d.rectangle([cx - 16, py - 70, cx + 16, py + 70], fill=green)
    out = img.resize((size, size), Image.LANCZOS)
    if size == 180:  # iOS mag keine Transparenz
        bg = Image.new("RGBA", out.size, green); bg.alpha_composite(out); out = bg
    return out

MIT = """MIT License

Copyright (c) 2026 Jochen G. Fuchs (https://efuchs.net)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

QRGEN_MIT = MIT.replace("Copyright (c) 2026 Jochen G. Fuchs (https://efuchs.net)", "Copyright (c) 2009 Kazuhiko Arase")

def licenses_md():
    ofl = (VEN / "@fontsource/barlow/LICENSE").read_text().strip()
    apache = (VEN / "jsqr/LICENSE").read_text().strip()
    return f"""# Lizenzen

## Thekenfuchs

Copyright (c) 2026 Jochen G. Fuchs – https://efuchs.net
Veröffentlicht unter der MIT-Lizenz (Volltext in `LICENSE` und unten).

Der Thekenfuchs enthält Komponenten Dritter. Sie behalten ihre eigenen Lizenzen:

| Komponente | Zweck | Urheber | Lizenz |
|---|---|---|---|
| Barlow, Barlow Condensed | Schrift (eingebettet) | The Barlow Project Authors | SIL Open Font License 1.1 |
| qrcode-generator 1.4.4 | QR-Code erzeugen | Kazuhiko Arase | MIT |
| jsQR 1.4.0 | QR-Code lesen (nur PWA) | Cosmo Wolfe | Apache License 2.0 |

„QR Code“ ist eine eingetragene Marke der DENSO WAVE INCORPORATED.

---

## Thekenfuchs – MIT License

```
{MIT.strip()}
```

---

## Barlow – SIL Open Font License 1.1

```
{ofl}
```

---

## qrcode-generator – MIT License

```
{QRGEN_MIT.strip()}
```

---

## jsQR – Apache License 2.0

```
{apache}
```
"""

def webclip_profile(url: str, icon_png: bytes, removable: bool = False) -> bytes:
    """Konfigurationsprofil (Web Clip) – identischer Aufbau wie makeProfile() in der App."""
    ns = uuid.uuid5(uuid.NAMESPACE_URL, url)
    clip = {
        "PayloadType": "com.apple.webClip.managed", "PayloadVersion": 1,
        "PayloadIdentifier": "net.efuchs.thekenfuchs.webclip",
        "PayloadUUID": str(uuid.uuid5(ns, "webclip")).upper(),
        "PayloadDisplayName": "Thekenfuchs (Web Clip)",
        "URL": url, "Label": "Thekenfuchs", "Icon": icon_png,
        "FullScreen": True, "IsRemovable": removable, "IgnoreManifestScope": False, "Precomposed": True,
    }
    prof = {
        "PayloadType": "Configuration", "PayloadVersion": 1,
        "PayloadIdentifier": "net.efuchs.thekenfuchs",
        "PayloadUUID": str(uuid.uuid5(ns, "profile")).upper(),
        "PayloadDisplayName": "Thekenfuchs",
        "PayloadDescription": f"{NAME} – {TAGLINE}. Legt die Web-App auf den Home-Bildschirm. {DISCLAIMER}",
        "PayloadOrganization": "Thekenfuchs · efuchs.net",
        "PayloadRemovalDisallowed": False,
        "PayloadContent": [clip],
    }
    return plistlib.dumps(prof, fmt=plistlib.FMT_XML)

SW_JS = """// Thekenfuchs Service Worker – nur App-Dateien, keine Daten.
const CACHE = @CACHE@;
const FILES = @FILES@;
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('thekenfuchs-') && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  if (!new URL(req.url).pathname.startsWith(new URL(self.registration.scope).pathname)) return;
  if (req.mode === 'navigate') {
    e.respondWith(caches.match('index.html').then(r => r || fetch(req)));
    return;
  }
  e.respondWith(caches.match(req, { ignoreSearch: true }).then(r => r || fetch(req)));
});
"""

def main():
    global VERSION
    ap = argparse.ArgumentParser(description="Thekenfuchs bauen")
    ap.add_argument("--url", default=DEFAULT_URL, help=f"HTTPS-Adresse der App (Default {DEFAULT_URL})")
    ap.add_argument("--version", help="Versionsnummer, z. B. 1.0.0 (Default: Zeitstempel-dev)")
    ap.add_argument("--removable", action="store_true", help="Web-Clip-Icon darf vom Home-Bildschirm gelöscht werden")
    args = ap.parse_args()
    if not args.url.startswith("https://") or not args.url.endswith("/"):
        ap.error("--url muss mit https:// beginnen und mit / enden")
    if args.version:
        VERSION = args.version.lstrip("v")
    if DIST.exists():
        shutil.rmtree(DIST)
    site, art, rel = DIST / "site", DIST / "artifact", DIST / "release"
    if SITE.exists():
        shutil.copytree(SITE, site)
    app, demo, inst = site / "app", site / "demo", site / "install"
    for d in (app, demo, inst, art, rel):
        d.mkdir(parents=True, exist_ok=True)

    for sz in (180, 192, 512):
        icon(sz).save(app / f"icon-{sz}.png")
    icon(512, maskable=True).save(app / "icon-512-maskable.png")
    icon180 = (app / "icon-180.png").read_bytes()

    (art / "thekenfuchs.html").write_text(build("artifact"))
    index = build("app", base64.b64encode(icon180).decode())
    (app / "index.html").write_text(index)
    (demo / "index.html").write_text(build("demo"))

    (app / "manifest.webmanifest").write_text(json.dumps({
        "id": "./", "name": NAME, "short_name": NAME, "lang": "de",
        "description": DESCRIPTION,
        "start_url": "./", "scope": "./", "display": "standalone", "orientation": "any",
        "background_color": "#EEF1EC", "theme_color": "#0E6A4C",
        "icons": [
            {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "icon-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }, ensure_ascii=False, indent=2))
    files = ["./", "index.html", "manifest.webmanifest", "icon-180.png", "icon-192.png", "icon-512.png", "icon-512-maskable.png"]
    cache = "thekenfuchs-" + hashlib.sha256(index.encode()).hexdigest()[:10]
    (app / "sw.js").write_text(SW_JS.replace("@CACHE@", json.dumps(cache)).replace("@FILES@", json.dumps(files)))

    profile = webclip_profile(args.url, icon180, args.removable)
    (inst / "thekenfuchs.mobileconfig").write_bytes(profile)
    (rel / "thekenfuchs.mobileconfig").write_bytes(profile)
    fonts = site / "assets" / "fonts"          # Schriften als Dateien für Start- und Installationsseite
    fonts.mkdir(parents=True, exist_ok=True)
    for _, _, rel_path in FONTS:
        shutil.copy(VEN / rel_path, fonts / Path(rel_path).name)
    (site / ".nojekyll").write_text("")
    (site / "version.json").write_text(json.dumps({"name": NAME, "version": VERSION, "app": args.url}, ensure_ascii=False))

    (ROOT / "LICENSE").write_text(MIT)
    (ROOT / "LIZENZEN.md").write_text(licenses_md())
    readme = README.replace("@VERSION@", VERSION).replace("@URL@", args.url)
    with zipfile.ZipFile(rel / "thekenfuchs.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(app.iterdir()):
            z.write(f, f.name)
        z.writestr("LIESMICH.md", readme)
        z.writestr("LICENSE", MIT)
        z.writestr("LIZENZEN.md", licenses_md())
        z.writestr("thekenfuchs.mobileconfig", profile)
    print("Version", VERSION, "· App", args.url)
    for f in sorted(DIST.rglob("*")):
        if f.is_file():
            print(f"{f.stat().st_size:>9}  {f.relative_to(DIST)}")

README = """# Thekenfuchs (Version @VERSION@)

**Antippen statt Kopfrechnen – Thekenrechner für Vereinsfeste.**
Offline-Web-App für Tablet und Smartphone (iPad, Android, Windows): Produkte mit Preisen auf Tasten,
Pfandautomatik, Rückgeld auf einen Blick, Preisliste per QR auf alle Geräte verteilbar.

*Rechenhilfe, keine Kasse: Der Thekenfuchs speichert keine Verkäufe.*

Entwickelt von Jochen G. Fuchs – https://efuchs.net
Lizenz: MIT (siehe `LICENSE`, Komponenten Dritter in `LIZENZEN.md`).

Online-Version: @URL@

## iPad einrichten (einmalig, mit Internet)

**Weg 1 – Installationsprofil (empfohlen für mehrere Vereins-iPads)**
1. `thekenfuchs.mobileconfig` per AirDrop aufs iPad schicken (oder aus der App:
   Einstellungen → Gerät → „Installationsprofil teilen“).
2. Einstellungen → „Profil geladen“ → Installieren. iOS zeigt „Nicht verifiziert“,
   weil das Profil nicht signiert ist – das ist normal.
3. Den Thekenfuchs vom Home-Bildschirm **einmal mit Internet** starten. Ab dann offline.

Entfernen: Einstellungen → Allgemein → VPN und Geräteverwaltung → Thekenfuchs.

**Weg 2 – von Hand**
1. @URL@ in Safari öffnen → Teilen → „Zum Home-Bildschirm“.
2. Vom Home-Bildschirm einmal starten. Ab dann offline.

**Danach auf jedem iPad**
- Preisliste übernehmen: Einstellungen → „QR scannen“ → QR-Code am Master-Gerät.
  In der installierten App scannen, nicht mit der Kamera-App (die öffnet Safari,
  und Safari hat einen getrennten Speicher).
- Kennung „Preisliste XXXX“ oben mit dem Master-Gerät vergleichen.
- Optional: PIN setzen, Geführten Zugriff aktivieren, Auto-Sperre aus.

## Android (Tablet und Smartphone)

1. @URL@ in **Chrome** öffnen.
2. Menü (⋮) → „App installieren“ bzw. „Zum Startbildschirm hinzufügen“.
   Oft bietet Chrome die Installation von selbst an.
3. Vom Startbildschirm einmal mit Internet starten. Ab dann offline.

Samsung Internet kann ebenfalls installieren. Das Installationsprofil ist nur für
iPad/iPhone und wird auf Android nicht gebraucht. Preislisten wie beim iPad per
„QR scannen“ in der App übernehmen.

## Windows-Tablet

**Online (empfohlen):** @URL@ in Edge oder Chrome öffnen → als App installieren
(Edge: Menü → Apps; Chrome: Installieren-Symbol in der Adressleiste).

**Lokal ohne Internet:** Diese ZIP entpacken, Ordner an einen festen Ort legen
(nicht mehr verschieben – die Preislisten hängen am Speicherort), `index.html`
in Edge oder Chrome öffnen, Verknüpfung auf den Desktop. Kein QR-Scan per Kamera,
Preislisten dann per „Code einfügen“ übernehmen.

Firefox kann keine Web-Apps installieren – Edge oder Chrome verwenden.

## Bedienung

**Gegebenes Geld:** Geldtasten 50 ct bis 100 €, dazu „+“, „−“ und „C“.
Normal ersetzt jeder Tipp den Betrag; „+“ bzw. „−“ gilt für den nächsten Tipp
(20 € → + → 2 € = 22 €). Einstellungen → Gerät → „Auto-Addieren“: Jeder Tipp addiert,
„−“ zieht den nächsten Betrag ab. Gilt nur für dieses Gerät.

**Mehrere Feste:** Einstellungen → Feste: Namen eingeben, Vorlage wählen (Kopie des
aktiven, leer oder Beispiel), „Fest anlegen“. Bearbeitet und per QR weitergegeben wird
immer das aktive Fest. Beim Import mit gleichem Namen bietet die App „aktualisieren“ an.

**Pfand:**
1. Eine Kategorie als **Pfandkategorie** markieren (eine pro Fest).
2. Ihre Artikel sind die Pfandwerte, z. B. Pfand Glas 2,00 und Pfand Krug 5,00.
   Einer davon ist **Standard**. Pfandrückgabe = Artikel mit negativem Preis.
3. „Pfand automatisch hinzufügen“ einschalten.
4. Bei Getränken und Speisen „Pfand“ antippen – ab zwei Pfandwerten mit Auswahl.

## Updates

Jedes Gerät holt die neue Version beim nächsten Start mit Internet.
Die Preislisten bleiben erhalten.

## Steuerliche Leitplanken (nicht ändern)

- Keine Historie, keine Zähler, keine Tagessumme, kein Export von Verkäufen.
- Die Content-Security-Policy (`connect-src 'none'`) verhindert jeden Datenversand.
- Keine Verbindung zu Bestellsystem, Kasse oder Zahlungsdienst.

Keine Steuerberatung. Einsatz mit dem Vereins-Steuerberater abstimmen.
"""

if __name__ == "__main__":
    main()
