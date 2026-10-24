---
type: Briefing
titel: Copilot-Anleitung – Projektsammelseite und Thekenfuchs auf GitHub Pages
stand: 2026-10-24
autor: Jochen G. Fuchs (efuchs.net)
---

# Copilot-Anleitung: Projektsammelseite + Thekenfuchs (Org E-Fuchs)

Diese Anleitung beschreibt zwei öffentliche Repositories in der GitHub-Organisation **E-Fuchs**
(`https://github.com/E-Fuchs`). Alle übrigen Repos der Organisation bleiben privat und unberührt:

| Repo | Veröffentlicht unter | Inhalt |
|---|---|---|
| `E-Fuchs/e-fuchs.github.io` | `https://e-fuchs.github.io/` | Projektsammelseite (Teil A) |
| `E-Fuchs/thekenfuchs` | `https://e-fuchs.github.io/thekenfuchs/` | Thekenfuchs: Quellen, Build, Startseite, Demo, App (Teil B) |

Teil C ist der Ablauf für Jochen, Teil D die Abnahme.

---

## 0. Feste Entscheidungen – nicht ändern

1. **Die App-Adresse ist fest:** `https://e-fuchs.github.io/thekenfuchs/app/`.
   Installierte Apps, gespeicherte Preislisten und Installationsprofile hängen an dieser
   Adresse (Ursprung + Pfad). Eine Änderung zwingt alle Geräte zur Neueinrichtung und
   löscht deren Preislisten.
2. **Eigene Domain nur jetzt oder nie.** Eine eigene Domain (z. B. `projekte.efuchs.net`) auf
   `e-fuchs.github.io` gilt für alle Projektseiten der Organisation. Sie darf nur gesetzt werden,
   **bevor** das erste Gerät produktiv eingerichtet ist (dann `build.py --url` anpassen).
   Später würde GitHub umleiten, der Ursprung ändert sich, siehe Punkt 1 – installierte Geräte
   bekämen keine Updates mehr. Copilot setzt keine Domain.
3. **Gemeinsamer Ursprung:** Alle Projekte unter `e-fuchs.github.io` teilen sich
   `localStorage` und Service-Worker-Bereich. Deshalb:
   - **Kein Service Worker** auf der Sammelseite und in keinem anderen Projekt mit Scope `/`.
   - **Nie** `localStorage.clear()`, `sessionStorage.clear()` oder Löschen aller Caches.
     Jedes Projekt nutzt nur eigene Schlüssel mit Präfix (Thekenfuchs: `thekenfuchs.`).
4. **Kein Tracking, keine externen Ressourcen** (keine CDNs, kein Google Fonts, keine
   Analytics, keine eingebetteten Fremdinhalte). Schriften und Bilder liegen im Repo.
5. **App-Code ist tabu:** `src/`, `build.py`, `test_e2e.py` und die Workflows in
   `.github/workflows/` werden von Copilot nicht verändert. Copilot arbeitet nur in `site/`
   (Teil B) bzw. im Sammelseiten-Repo (Teil A).
6. Sprache Deutsch, Du-Form, kurze Sätze. Keine Werbesprache.

---

## A. Repo `e-fuchs.github.io` – Projektsammelseite

### A.1 Zweck

Eine schlichte Übersicht aller Projekte von Jochen G. Fuchs. Jedes Projekt ist ein
eigenes Repo mit eigener Pages-Seite unter `/<repo>/`. Die Sammelseite verlinkt nur.

### A.2 Dateien

```
index.html          Übersicht mit Projektkarten
datenschutz.html    Datenschutzhinweis (Text siehe A.5)
assets/style.css    Gemeinsames Stylesheet
assets/fonts/       Barlow / Barlow Condensed (woff2, aus dem Thekenfuchs-Repo kopieren)
assets/projects/    Vorschaubilder je Projekt (z. B. thekenfuchs.webp)
.nojekyll
README.md
```

Pages-Quelle: **Deploy from a branch → `main` / root**. Kein Build nötig.

### A.3 Inhalt `index.html`

- Kopf: „e-fuchs · Projekte“, darunter: „Werkzeuge, Experimente und Helfer von
  Jochen G. Fuchs – frei nutzbar, quelloffen.“ Link zu `https://efuchs.net`.
- Projektkarten in einem Raster (1 Spalte am Telefon, 2–3 ab Tablet). Jede Karte:
  Vorschaubild, Name, Untertitel, ein Satz, Status-Plakette, Links.
- Erste Karte **Thekenfuchs**:
  - Bild: `assets/projects/thekenfuchs.webp` (Kopie von `thekenfuchs/site/assets/screen-theke-light.webp`)
  - Name: **Thekenfuchs**
  - Untertitel: **Antippen statt Kopfrechnen – für Vereinsfeste**
  - Text: „Preise auf Tasten · Pfand rechnet mit · Rückgeld auf einen Blick · eine
    Preisliste für alle Geräte. Rechenhilfe, keine Kasse.“
  - Plakette: „Offline-Web-App · iPad, Android, Windows“
  - Links: „Ansehen“ → `/thekenfuchs/`, „Demo“ → `/thekenfuchs/demo/`,
    „Quellcode“ → `https://github.com/E-Fuchs/thekenfuchs`
- Neue Projekte = neue Karte im HTML (bewusst ohne JavaScript, damit die Seite auch ohne
  Skripte und für Suchmaschinen vollständig ist).
- Fuß: „© 2026 Jochen G. Fuchs · efuchs.net“ · Impressum (`https://efuchs.net/impressum/`) ·
  Datenschutz (`datenschutz.html`). Auf jeder Seite der Sammelseite, auch auf `datenschutz.html`.

### A.4 Gestaltung

- Farben als CSS-Variablen, hell und dunkel über `prefers-color-scheme`:
  hell `--bg:#EEF1EC --surface:#FFFFFF --ink:#17201B --muted:#59665F --line:#CBD3CC --accent:#0E6A4C`,
  dunkel `--bg:#101513 --surface:#18201C --ink:#E6ECE8 --muted:#9AA8A0 --line:#2C3832 --accent:#3FB386`.
- Schriften: Überschriften „Barlow Condensed“ 600/700, Text „Barlow“ 400/500/600, Fallback
  `system-ui, sans-serif`. `@font-face` mit `font-display: swap`.
- Ruhig, viel Weißraum, Karten mit 1 px Rand statt Schatten. Sichtbarer Fokus-Rahmen.
  `prefers-reduced-motion` beachten.

### A.5 Impressum und Datenschutz

- **Impressum:** kein eigenes. Alle Seiten (Sammelseite und Projekte) verlinken mit der
  Beschriftung „Impressum“ auf `https://efuchs.net/impressum/`.
- **Datenschutz:** eigene Seite `datenschutz.html` im Sammelseiten-Repo. Text 1:1 aus
  `https://github.com/E-Fuchs/thekenfuchs/blob/main/docs/datenschutz-sammelseite.md`
  übernehmen (Frontmatter und HTML-Kommentar weglassen, Gestaltung wie A.4). Stellen in
  [eckigen Klammern] als solche stehen lassen und im Pull Request auflisten – nichts erfinden.
  Diese Seite gilt für alle Projektseiten unter `e-fuchs.github.io`.
- Keine Rechtsberatung – Jochen prüft beide Texte vor dem Merge.

---

## B. Repo `thekenfuchs` – Start- und Installationsseite

> **Stand 24.10.2026: umgesetzt** (`site/index.html`, `site/install/index.html`, `site/assets/site.css`).
> Teil B dient nur noch als Referenz für spätere Änderungen. Für Copilot offen ist **Teil A**.

### B.1 Was schon da ist (nicht ändern)

| Pfad | Inhalt |
|---|---|
| `src/` | App-Quelltext |
| `build.py` | baut `dist/site/` (Pages), `dist/release/` (ZIP + Profil) |
| `test_e2e.py` | End-to-End-Tests |
| `.github/workflows/pages.yml` | Push auf `main` → bauen, testen, auf Pages veröffentlichen |
| `.github/workflows/release.yml` | Tag `v*` → Release mit `thekenfuchs.zip` und `thekenfuchs.mobileconfig` |
| `site/assets/` | Bildschirmfotos (`screen-*.webp`), `icon-512.png` |
| `site/index.html` | **Platzhalter – ersetzen** (B.3) |

`build.py` kopiert `site/` nach `dist/site/` und ergänzt:

| Veröffentlichter Pfad | Quelle |
|---|---|
| `/thekenfuchs/` | `site/index.html` |
| `/thekenfuchs/install/` | `site/install/index.html` (**neu anlegen**, B.4) |
| `/thekenfuchs/install/thekenfuchs.mobileconfig` | von `build.py` erzeugt |
| `/thekenfuchs/app/` | von `build.py` erzeugt |
| `/thekenfuchs/demo/` | von `build.py` erzeugt |
| `/thekenfuchs/assets/fonts/*.woff2` | von `build.py` kopiert (Barlow, Barlow Condensed) |

Alle Links **relativ** setzen (`demo/`, `install/`, `app/`, `assets/…`; von `install/` aus
`../`). So funktioniert die Seite auch lokal unter `dist/site/`.

Gestaltung wie A.4 (gleiche Farben, gleiche Schriften aus `assets/fonts/`). Eigenes
Stylesheet `site/assets/site.css`, von beiden Seiten genutzt. Kein JavaScript nötig.

### B.2 Feste Texte

- Name: **Thekenfuchs**
- Untertitel: **Antippen statt Kopfrechnen – für Vereinsfeste**
- Leistungszeile: **Preise auf Tasten · Pfand rechnet mit · Rückgeld auf einen Blick · eine Preisliste für alle Geräte**
- Abgrenzung: **Rechenhilfe, keine Kasse: Der Thekenfuchs speichert keine Verkäufe.**
- Geräte: **Tablet und Smartphone – iPad, Android, Windows**
- Kurzbeschreibung (Repo-Beschreibung, Meta-Description der Startseite):
  „Antippen statt Kopfrechnen – Thekenrechner für Vereinsfeste. Offline-Web-App für Tablet und Smartphone (iPad, Android, Windows): Produkte mit Preisen auf Tasten, Pfandautomatik, Rückgeld auf einen Blick, Preisliste per QR auf alle Geräte verteilbar. Rechenhilfe, keine Kasse – speichert keine Verkäufe.“
- Wortwahl: nie „Kasse“, „Kassensystem“, „Kassierer“ oder „Bon“ als Beschreibung dessen, was der
  Thekenfuchs ist – nur in der Abgrenzung („keine Kasse“).
- Entwickler: Jochen G. Fuchs · https://efuchs.net · Lizenz MIT
- Download-Link (stabil): `https://github.com/E-Fuchs/thekenfuchs/releases/latest/download/thekenfuchs.zip`

### B.3 `site/index.html` – Startseite

1. **Kopf:** Icon `assets/icon-512.png` (96 px), Name, Untertitel, Leistungszeile.
   Drei Schaltflächen: **Demo ausprobieren** (`demo/`, Hauptaktion), **Installieren**
   (`install/`), **Download** (Release-Link). Darunter klein die Abgrenzung.
2. **Bild:** `assets/screen-theke-light.webp` mit `<picture>` und
   `assets/screen-theke-dark.webp` für `prefers-color-scheme: dark`.
   Alt-Text: „Thekenfuchs auf dem iPad: Marken für Speisen, Getränke und Pfand, rechts die
   Liste des Gastes mit Summe 27,00 €, gegeben 30,00 €, Rückgeld 3,00 €.“
3. **Was er besser kann als ein Taschenrechner** (Raster, je Punkt Überschrift + 1–2 Sätze):
   - **Preise auf Tasten** – Bratwurst antippen statt 3,50 eintippen. Zweimal antippen = zwei Stück.
   - **Pfand rechnet mit** – Getränke bringen ihr Pfand automatisch mit in die Summe. Glas, Krug,
     Rückgabe – alles in einer Pfandkategorie, mit Standard-Pfandwert. Bild `assets/screen-pfand.webp`.
   - **Rückgeld auf einen Blick** – Geldtasten von 50 ct bis 100 €, mit „+“ und „−“ für mehrere
     Scheine. Auf Wunsch addiert jeder Tipp automatisch.
   - **Eine Preisliste für alle Geräte** – Preise einmal pflegen, per QR-Code auf die anderen
     Tablets übertragen. Eine Kennung zeigt, ob alle Geräte gleich rechnen. Bild `assets/screen-qr.webp`.
   - **Läuft ohne Internet** – einmal installiert, funktioniert er auch im Festzelt ohne Netz.
   - **Auf jedem Gerät** – iPad, Android-Tablet, Windows-Tablet oder Smartphone. Kein App Store,
     keine Anmeldung.
   - **Mehrere Feste** – Sommerfest, Weinfest, Weihnachtsmarkt: je eigene Preisliste, schnell
     gewechselt. Einstellungen auf Wunsch mit PIN geschützt.
4. **Was er bewusst nicht kann** (eigener, ruhig abgesetzter Kasten):
   - Keine Kasse und kein Bon: Er speichert keine Verkäufe, keine Summen, keine Tagesabschlüsse.
   - Keine Daten verlassen das Gerät. Gespeichert sind nur die Preislisten.
   - Kassiert wird wie gewohnt bar in die Kassette.
   - Satz: „Keine Steuerberatung – den Einsatz bitte mit dem Steuerberater des Vereins abstimmen.“
5. **Am Telefon:** Bild `assets/screen-phone.webp` (schmal, neben kurzem Text „Läuft auch auf
   dem Smartphone – iPhone oder Android – für den Getränkestand ohne Tablet.“).
6. **So kommt er aufs Gerät:** drei Kurzschritte (Installieren → einmal mit Internet starten →
   Preisliste per QR übernehmen), Link „Ausführliche Anleitung“ → `install/`.
7. **Fuß:** „Entwickelt von Jochen G. Fuchs · efuchs.net“, „MIT-Lizenz“,
   „Quellcode“ (`https://github.com/E-Fuchs/thekenfuchs`), „Lizenzen“
   (`https://github.com/E-Fuchs/thekenfuchs/blob/main/LIZENZEN.md`),
   „Alle Projekte“ (`../`), Impressum (`https://efuchs.net/impressum/`),
   Datenschutz (`../datenschutz.html` – liegt auf der Sammelseite).

`<title>Thekenfuchs – Antippen statt Kopfrechnen</title>`, Meta-Description = Untertitel + Leistungszeile,
Open-Graph-Bild `assets/screen-theke-light.webp`.

### B.4 `site/install/index.html` – Installationsseite

Überschrift „Thekenfuchs installieren“. Abschnitte mit Sprungmarken (`#ipad`, `#android`, `#windows`, `#danach`).
Oben eine kurze Sprungleiste zu den vier Abschnitten. iPhone wie iPad.

**iPad – mit Installationsprofil (empfohlen für mehrere Vereins-iPads)** `#ipad`
1. Schaltfläche **„Installationsprofil laden“** → `thekenfuchs.mobileconfig` (in Safari öffnen).
   Alternative: Datei per AirDrop schicken, oder in der installierten App unter
   Einstellungen → Gerät → „Installationsprofil teilen“.
2. Einstellungen → „Profil geladen“ → Installieren. iOS zeigt „Nicht verifiziert“, weil das
   Profil nicht signiert ist. Das ist normal.
3. Thekenfuchs vom Home-Bildschirm **einmal mit Internet** starten. Danach läuft er offline.
4. Entfernen: Einstellungen → Allgemein → VPN und Geräteverwaltung → Thekenfuchs.

**iPad – von Hand**
1. `../app/` in Safari öffnen (Link anbieten).
2. Teilen → „Zum Home-Bildschirm“.
3. Vom Home-Bildschirm einmal mit Internet starten.

**Android (Tablet und Smartphone)** `#android`
1. `../app/` in **Chrome** öffnen (Link anbieten).
2. Menü (⋮) → „App installieren“ bzw. „Zum Startbildschirm hinzufügen“ → „Installieren“.
   Oft bietet Chrome die Installation von selbst unten im Bild an.
3. Vom Startbildschirm einmal mit Internet starten. Danach läuft er offline.
- Samsung Internet kann ebenfalls installieren (Menü → „Seite hinzufügen zu“ → „Startbildschirm“).
- Das Installationsprofil (`.mobileconfig`) ist nur für iPad/iPhone und wird auf Android nicht gebraucht.

**Windows-Tablet** `#windows`
- Online (empfohlen): `../app/` in Edge oder Chrome öffnen, als App installieren
  (Edge: Menü → Apps; Chrome: Installieren-Symbol in der Adressleiste).
- Ohne Internet: Download-ZIP entpacken, Ordner an festen Ort legen, `index.html` in Edge
  oder Chrome öffnen. Preislisten dann per „Code einfügen“ übernehmen (kein Kamera-Scan).
- Firefox kann keine Web-Apps installieren.

**Nach der Installation** `#danach`
- Preisliste übernehmen: In der installierten App Einstellungen → „QR scannen“ → QR-Code am
  Master-Gerät scannen. **Immer in der App scannen**, nicht mit der Kamera-App oder Google Lens –
  die öffnen den Browser, und der hat einen getrennten Speicher (vor allem auf iPad/iPhone).
- Kennung „Preisliste XXXX“ oben auf beiden Geräten vergleichen.
- Optional: PIN für die Einstellungen, Geführter Zugriff (Bedienungshilfen), Auto-Sperre aus.

**Fuß** wie Startseite, relative Links mit einem `../` mehr (Datenschutz: `../../datenschutz.html`).

### B.5 Arbeitsweise

- Änderungen als Pull Request gegen `main`. Der Workflow `Pages` läuft erst nach dem Merge.
- Bilder nicht neu erzeugen oder komprimieren – die vorhandenen `site/assets/*.webp` verwenden.
- HTML validieren, keine Konsolenfehler, kein horizontales Scrollen bei 390 px Breite.

---

## C. Ablauf für Jochen

0. **Organisation absichern (einmalig):** `https://github.com/organizations/E-Fuchs/settings/member_privileges`
   → „Pages creation“: nur **Public** zulassen. Prüfen, dass kein privates Repo schon eine
   Pages-Seite hat (Seiten aus privaten Repos wären öffentlich erreichbar; die Sperre nimmt
   bestehende Seiten nicht offline). Entscheiden, ob eine eigene Domain kommt – jetzt oder nie
   (Abschnitt 0, Punkt 2).
1. **Repo `E-Fuchs/thekenfuchs` anlegen:** öffentlich, ohne README/Lizenz/.gitignore (kommt mit).
   Description: „Antippen statt Kopfrechnen – Thekenrechner für Vereinsfeste. Offline-Web-App für Tablet und Smartphone (iPad, Android, Windows): Produkte mit Preisen auf Tasten, Pfandautomatik, Rückgeld auf einen Blick, Preisliste per QR auf alle Geräte verteilbar. Rechenhilfe, keine Kasse – speichert keine Verkäufe.“
   Website: `https://e-fuchs.github.io/thekenfuchs/` · Topics: `pwa`, `offline-first`, `ipad`,
   `android`, `verein`, `vereinsfest`, `thekenrechner`, `pfand`, `rechner`, `german`.
2. **Quellen hochladen** – per Git, weil der Ordner `.github` beim Hochladen im Browser leicht
   verloren geht:
   ```bash
   unzip thekenfuchs-repo.zip && cd thekenfuchs
   git init -b main && git add . && git commit -m "Thekenfuchs 1.0.0"
   git remote add origin https://github.com/E-Fuchs/thekenfuchs.git
   git push -u origin main
   ```
3. **Pages aktivieren:** Settings → Pages → Source: **GitHub Actions**. Unter Actions den Lauf
   „Pages“ abwarten (beim ersten Mal ggf. „Re-run“).
4. **Copilot Teil B** geben (diese Datei liegt im Repo). PR prüfen, mergen.
5. **Repo `E-Fuchs/e-fuchs.github.io` anlegen** (öffentlich, Name exakt so), Copilot Teil A geben,
   Pages: Branch `main` / root.
6. **Version veröffentlichen:** `git tag v1.0.0 && git push origin v1.0.0` → Release mit ZIP
   und Profil.
7. **Abnahme** nach Teil D, dann Praxistest auf zwei iPads.

---

## D. Abnahme

| Prüfung | Erwartung |
|---|---|
| `https://e-fuchs.github.io/` | Sammelseite mit Thekenfuchs-Karte, hell und dunkel lesbar |
| `https://github.com/E-Fuchs` (abgemeldet ansehen) | nur `e-fuchs.github.io` und `thekenfuchs` sichtbar |
| `/thekenfuchs/` | Startseite, alle Links funktionieren, Bilder laden |
| `/thekenfuchs/demo/` | gelbe Demo-Leiste; nach Neuladen wieder Beispiel-Fest |
| `/thekenfuchs/app/` | App ohne Demo-Leiste; Einstellungen → Gerät zeigt Profil-Adresse `…/thekenfuchs/app/` |
| `/thekenfuchs/version.json` | zeigt die Version (Tag) |
| Impressum- und Datenschutz-Link auf Sammelseite, Start-, Installationsseite, App und Demo | Impressum → efuchs.net/impressum/, Datenschutz → e-fuchs.github.io/datenschutz.html; beide erreichbar |
| `install/thekenfuchs.mobileconfig` in Safari am iPad | iOS meldet „Profil geladen“. **Falls stattdessen Text angezeigt wird** (falscher Dateityp bei GitHub Pages): Profil per AirDrop oder aus dem Release verteilen und den Hinweis auf der Installationsseite entsprechend anpassen |
| Release `v1.0.0` | Anhänge `thekenfuchs.zip` und `thekenfuchs.mobileconfig`; Download-Link auf der Startseite funktioniert |
| iPad, App installiert, Flugmodus | App startet, Preisliste bleibt nach Neustart erhalten |
| Android mit Chrome, „App installieren“, Flugmodus | App startet als eigenes Fenster, Preisliste bleibt erhalten, QR-Scan in der App funktioniert |
| Demo auf einem Vereins-iPad geöffnet | Preislisten der installierten App unverändert |
