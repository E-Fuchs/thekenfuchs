# Thekenfuchs

**Antippen statt Kopfrechnen – Thekenrechner für Vereinsfeste.**
Produkte mit Preisen auf Tasten · Pfandautomatik · Rückgeld auf einen Blick · Preisliste per QR-Code auf alle Geräte verteilbar · Online-Installation, Offline-Betrieb.

*Rechenhilfe, keine Kasse: Der Thekenfuchs speichert keine Verkäufe.*

- Demo: https://e-fuchs.github.io/thekenfuchs/demo/
- App (zum Installieren): https://e-fuchs.github.io/thekenfuchs/app/
- Installation: https://e-fuchs.github.io/thekenfuchs/install/
- Download: https://github.com/E-Fuchs/thekenfuchs/releases/latest/download/thekenfuchs.zip

Offline-Web-App (PWA) für Tablet und Smartphone – iPad, Android, Windows. Kein App Store, kein Server,
keine Daten über Verkäufe.

## Technik

| | |
|---|---|
| Typ | Progressive Web App – installierbar, offline-fähig |
| Plattformen | iPad/iPhone (Safari), Android (Chrome, Samsung Internet), Windows (Edge, Chrome) |
| Frontend | HTML, CSS, JavaScript ohne Framework, eine Datei, Schriften eingebettet |
| Offline | Service Worker (Cache-first, Scope `/thekenfuchs/app/`), Web App Manifest |
| Speicher | `localStorage` (Preislisten, Geräte-Einstellungen); laufender Gast nur im Arbeitsspeicher |
| Datenaustausch | QR-Code mit Preisliste im URL-Fragment (`CompressionStream` deflate-raw, base64url), Datei, Web Share |
| QR-Code | qrcode-generator (erzeugen), jsQR + `getUserMedia` (lesen) |
| iOS-Installation | Konfigurationsprofil mit Web Clip (`.mobileconfig`) |
| Weitere APIs | Screen Wake Lock, Web Share, Storage Persistence |
| Sicherheit | CSP `connect-src 'none'`, keine externen Ressourcen; PIN als Bedienschutz (kein Zugriffsschutz) |
| Größe | ca. 530 KB, ca. 200 KB komprimiert |
| Build / Tests | `build.py` (Python), Playwright mit 80 Prüfungen |
| CI/CD | GitHub Actions → GitHub Pages; Tag/Release → ZIP + Profil |

Architektur und Entscheidungen: https://e-fuchs.github.io/thekenfuchs/technik/

## Aufbau

| Pfad | Inhalt |
|---|---|
| `src/` | App-Quelltext (`head.html`, `body.html`) – eine Datei, alles inline |
| `build.py` | Baut `dist/site/` (Pages), `dist/release/` (ZIP + Profil), `dist/artifact/` |
| `site/` | Startseite und Installationsseite (statisch), werden nach `dist/site/` kopiert |
| `test_e2e.py` | End-to-End-Tests mit Playwright (Chromium) |
| `.github/workflows/` | `pages.yml` (Push auf `main` → Pages), `release.yml` (Tag `v*` → Release) |

Veröffentlichte Struktur unter `/thekenfuchs/`:

| Pfad | Zweck |
|---|---|
| `/` | Startseite |
| `/demo/` | Demo, Speicher nur im Arbeitsspeicher, kein Service Worker |
| `/app/` | Installierbare App (Manifest, Service Worker, Scope `/thekenfuchs/app/`) |
| `/install/` | Installationsanleitung + `thekenfuchs.mobileconfig` |

## Lokal bauen und testen

```bash
npm ci
pip install pillow playwright && python -m playwright install chromium
python build.py                 # Default-URL https://e-fuchs.github.io/thekenfuchs/app/
python test_e2e.py
```

## Version veröffentlichen

Im Browser: Releases → „Draft a new release“ → neuen Tag `v1.0.0` anlegen → „Publish release“.
Der Workflow `Release` hängt danach `thekenfuchs.zip` und `thekenfuchs.mobileconfig` an.

Oder per Git:

```bash
git tag v1.0.0 && git push origin v1.0.0
```

## Leitplanken (nicht ändern)

- Keine Historie, keine Zähler, keine Tagessumme, kein Export von Verkäufen.
- CSP `connect-src 'none'` in App und Demo – kein Datenversand, keine externen Ressourcen.
- Die App-Adresse `https://e-fuchs.github.io/thekenfuchs/app/` ist fest: installierte Apps,
  Preislisten und Installationsprofile hängen daran. Pfad nicht ändern. Eine eigene Domain auf
  `e-fuchs.github.io` nur vor dem ersten produktiv eingerichteten Gerät setzen (dann
  `build.py --url` anpassen), danach nie mehr.
- Speicherschlüssel beginnen mit `thekenfuchs.` (gemeinsamer Ursprung mit anderen Projekten
  auf `e-fuchs.github.io`).

## Lizenz

MIT – Copyright (c) 2026 Jochen G. Fuchs (https://efuchs.net). Komponenten Dritter siehe `LIZENZEN.md`.
