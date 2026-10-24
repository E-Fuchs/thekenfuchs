"""End-to-End-Tests (Playwright, Chromium). Vorher: python3 build.py"""
import asyncio, json, os, subprocess, sys, time
from playwright.async_api import async_playwright

PORT = 8765
ROOT = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(ROOT, "shots")
os.makedirs(SHOTS, exist_ok=True)

async def main():
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "-d", os.path.join(ROOT, "dist", "site")],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.8)
    url = f"http://localhost:{PORT}/app/"
    demo_url = f"http://localhost:{PORT}/demo/"
    fails = []
    def check(cond, msg):
        print(("OK   " if cond else "FAIL ") + msg)
        if not cond: fails.append(msg)
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch()
            ctx = await b.new_context(viewport={"width": 1180, "height": 820}, device_scale_factor=1)
            page = await ctx.new_page()
            errors = []
            page.on("console", lambda m: errors.append(m.text) if m.type in ("error", "warning") else None)
            page.on("pageerror", lambda e: errors.append(str(e)))
            await page.goto(url)
            await page.wait_for_timeout(500)

            keys = await page.locator(".key").count()
            check(keys == 13, f"13 Beispiel-Marken (ist {keys})")
            await page.click('[data-key="0:0"]'); await page.click('[data-key="0:0"]'); await page.click('[data-key="1:0"]')
            check((await page.text_content("#total")).strip() == "13,00 €", "Summe 2×3,50 + Bier 4,00 + Pfand 2,00 = 13,00 €")
            check(await page.locator('[data-dec="2:0"]').count() == 1, "Pfandzeile (Pfand Glas) automatisch angelegt")
            check((await page.text_content('[data-key="0:0"] .stamp')).strip() == "2", "Stempel zeigt Menge 2")
            await page.click('[data-coin="2000"]')
            check((await page.text_content("#changeAmt")).strip() == "7,00 €", "Rückgeld bei 20 € = 7,00 €")
            await page.click('[data-coin="500"]')
            check((await page.text_content("#changeLbl")).strip() == "Es fehlen", "Bei 5 €: 'Es fehlen'")
            # Gegebenes Geld: Ersetzen, +, −, C (Summe hier 13,00 €)
            await page.click('[data-coin="1000"]')
            check((await page.text_content("#givenAmt")).strip() == "gegeben 10,00 €", "Normalmodus: 5 € dann 10 € → 10 € (ersetzt)")
            await page.click('[data-gop="add"]'); await page.click('[data-coin="200"]')
            await page.click('[data-gop="add"]'); await page.click('[data-coin="100"]')
            check((await page.text_content("#givenAmt")).strip() == "gegeben 13,00 €", "+ 2 € + 1 € → 13 €")
            await page.click('[data-coin="50"]')
            check((await page.text_content("#givenAmt")).strip() == "gegeben 0,50 €", "Ohne + ersetzt der nächste Tipp wieder")
            await page.click('[data-coin="2000"]'); await page.click('[data-gop="sub"]'); await page.click('[data-coin="50"]')
            check((await page.text_content("#givenAmt")).strip() == "gegeben 19,50 €" and (await page.text_content("#changeAmt")).strip() == "6,50 €", "20 € − 50 ct = 19,50 €, Rückgeld 6,50 €")
            await page.click('[data-gop="clear"]')
            check(await page.locator("#change").is_hidden(), "C löscht das gegebene Geld")
            await page.click('[data-coin="2000"]')
            await page.click('[data-dec="0:0"]')
            check((await page.text_content("#total")).strip() == "9,50 €", "Minus-Taste: 9,50 €")
            await page.click('[data-dec="2:0"]')
            check((await page.text_content("#total")).strip() == "7,50 €", "Pfand einzeln abziehbar (eigener Becher): 7,50 €")
            await page.click('[data-inc="1:0"]')
            check((await page.text_content('[data-dec="2:0"] + span')).strip() == "1", "Plus am Bier erhöht Pfand mit")
            await page.click('[data-dec="1:0"]'); await page.click('[data-dec="1:0"]')
            check(await page.locator('[data-dec="2:0"]').count() == 0, "Bier ganz entfernt → Pfand weg")
            check((await page.text_content("#total")).strip() == "3,50 €", "Rest: 1 Bratwurst 3,50 €")
            await page.screenshot(path=f"{SHOTS}/ipad-light.png")

            ls = await page.evaluate("Object.keys(localStorage)")
            ls_vals = await page.evaluate("JSON.stringify(localStorage)")
            check(all(k.startswith("thekenfuchs.") for k in ls),
                  f"Storage enthält nur Preisliste/PIN: {ls}")
            check("3,50" not in ls_vals, "Keine Summe im Storage")

            await page.click("#btnNext")
            check((await page.text_content("#total")).strip() == "0,00 €", "Neuer Gast setzt zurück")

            # Pfand-Auszahlung
            await page.click('[data-key="2:1"]')
            check((await page.text_content("#totalLbl")).strip() == "Auszahlen", "Negativer Betrag → 'Auszahlen'")
            await page.click("#btnNext")

            # Einstellungen: Preis ändern, Artikel anlegen, speichern
            fp_before = await page.text_content("#fp")
            await page.click("#btnSettings")
            await page.fill("#p-0-0", "3,80")
            await page.click('[data-iadd="1"]')
            await page.fill("#n-1-5", "Weinschorle 0,25 l")
            await page.fill("#p-1-5", "3,5")
            await page.fill("#f-name", "Sommerfest SV Test")
            await page.wait_for_timeout(300)
            await page.screenshot(path=f"{SHOTS}/settings.png", full_page=False)
            await page.click('[data-act="save"]')
            await page.wait_for_timeout(400)
            fp_after = await page.text_content("#fp")
            check(fp_before != fp_after, f"Kennung ändert sich nach Speichern ({fp_before} → {fp_after})")
            # Fehlerprüfung Preis
            await page.fill("#p-0-1", "drei")
            await page.click('[data-act="save"]')
            check("Preis prüfen" in (await page.text_content("#saveMsg")), "Ungültiger Preis wird abgefangen")
            await page.fill("#p-0-1", "3,50")
            await page.click('[data-act="save"]')
            await page.wait_for_timeout(400)
            await page.locator(".qrbox").scroll_into_view_if_needed()
            await page.screenshot(path=f"{SHOTS}/share.png")

            # QR-Roundtrip: Canvas mit jsQR lesen, dekodieren, vergleichen
            rt = await page.evaluate("""async () => {
              const cv=document.getElementById('qr'); const g=cv.getContext('2d');
              const d=g.getImageData(0,0,cv.width,cv.height);
              const r=jsQR(d.data,cv.width,cv.height);
              if(!r) return {ok:false};
              const c=await window.__thekenfuchs.decodeText(r.data);
              return {ok:true, data:r.data, fp:window.__thekenfuchs.fingerprint(c), cur:window.__thekenfuchs.fingerprint(window.__thekenfuchs.cfg()), len:r.data.length};
            }""")
            check(rt.get("ok") and rt["fp"] == rt["cur"], f"QR → jsQR → Preisliste identisch ({rt.get('fp')}, {rt.get('len')} Zeichen)")
            check(rt.get("data","").startswith(url + "#cfg=FR1."), "QR enthält App-Link mit komprimiertem Code")
            code = await page.text_content("#sh-code")
            await page.click('[data-act="discard"]')
            await page.click('[data-key="0:0"]')
            check((await page.text_content("#total")).strip() == "3,80 €", "Neuer Preis 3,80 € aktiv")

            # Zweites "iPad": frischer Kontext, Import per Einfügen
            ctx2 = await b.new_context(viewport={"width": 820, "height": 1180})
            p2 = await ctx2.new_page()
            await p2.goto(url); await p2.wait_for_timeout(300)
            await p2.click("#btnSettings")
            await p2.fill("#f-paste", code)
            await p2.click('[data-act="check"]')
            await p2.wait_for_timeout(300)
            check(await p2.locator(".preview").count() == 1, "Import-Vorschau erscheint")
            await p2.click('[data-act="pending-yes"]'); await p2.wait_for_timeout(300)
            await p2.click('[data-act="discard"]')
            check((await p2.text_content("#fp")) == fp_after, "Zweites iPad hat gleiche Kennung")
            check((await p2.text_content("#evName")) == "Sommerfest SV Test", "Name übernommen")
            await p2.click('[data-key="0:0"]'); await p2.click('[data-key="1:1"]')
            await p2.screenshot(path=f"{SHOTS}/ipad-portrait.png")

            # Link-Import (#cfg=) wie nach Kamera-App-Scan
            ctx3 = await b.new_context(viewport={"width": 1180, "height": 820}, color_scheme="dark")
            p3 = await ctx3.new_page()
            await p3.goto(rt["data"]); await p3.wait_for_timeout(600)
            check(await p3.locator(".preview").count() == 1, "Link mit #cfg= öffnet Import-Vorschau")
            await p3.click('[data-act="pending-yes"]'); await p3.wait_for_timeout(300); await p3.click('[data-act="discard"]')
            await p3.click('[data-key="0:2"]'); await p3.click('[data-key="1:0"]'); await p3.click('[data-key="1:0"]'); await p3.click('[data-coin="5000"]')
            await p3.screenshot(path=f"{SHOTS}/ipad-dark.png")

            # PIN
            await page.click("#btnSettings")
            await page.click('[data-act="pin-set"]')
            for d in "12341234":
                await page.click(f'[data-pin="{d}"]')
            await page.wait_for_timeout(200)
            await page.click('[data-act="discard"]')
            await page.click("#btnSettings")
            check(not await page.locator("#pinSheet").is_hidden(), "PIN-Sperre greift")
            for d in "0000": await page.click(f'[data-pin="{d}"]')
            check("Falsche PIN" in (await page.text_content("#pinMsg")), "Falsche PIN abgewiesen")
            for d in "1234": await page.click(f'[data-pin="{d}"]')
            check(not await page.locator("#setSheet").is_hidden(), "Richtige PIN öffnet Einstellungen")
            await page.click('[data-act="discard"]')

            # Offline: SW aktiv, Reload ohne Netz
            await page.evaluate("navigator.serviceWorker.ready")
            await page.reload(); await page.wait_for_timeout(400)
            await ctx.set_offline(True)
            await page.reload(); await page.wait_for_timeout(500)
            check(await page.locator(".key").count() == 14, "Offline-Reload lädt App + Preisliste (14 Marken)")
            await ctx.set_offline(False)

            # Feste: anlegen, wechseln, löschen, Import als neues Fest
            await page.click("#btnSettings")
            for d in "1234": await page.click(f'[data-pin="{d}"]')
            check(await page.locator(".fest").count() == 1, "Start: ein Fest")
            await page.click('[data-act="fnew"]')
            check(await page.locator(".fest").count() == 1 and await page.locator("#f-newname.bad").count() == 1, "Ohne Namen wird kein Fest angelegt")
            await page.fill("#f-newname", "sommerfest sv test"); await page.click('[data-act="fnew"]')
            check(await page.locator(".fest").count() == 1, "Doppelter Name wird abgelehnt")
            await page.fill("#f-newname", "Herbstfest 2027"); await page.click('[data-tpl="copy"]')
            check((await page.input_value("#f-newname")) == "Herbstfest 2027", "Name bleibt beim Vorlagenwechsel erhalten")
            await page.press("#f-newname", "Enter"); await page.wait_for_timeout(200)
            check(await page.locator(".fest").count() == 2, "Kopie per Enter angelegt")
            check((await page.text_content("#evName")) == "Herbstfest 2027", "Neues Fest trägt den vergebenen Namen und ist aktiv")
            await page.fill("#f-name", "Weinfest 2027"); await page.fill("#p-1-0", "5,00")
            # Wechsel mit ungespeicherter Änderung → Rückfrage
            first_id = await page.evaluate("window.__thekenfuchs.feste().list[0].id")
            await page.click(f'[data-fsel="{first_id}"]')
            check("verwerfen" in (await page.text_content(f'[data-fsel="{first_id}"]')), "Wechsel fragt bei ungespeicherten Änderungen")
            await page.click('[data-act="save"]'); await page.wait_for_timeout(200)
            await page.click(f'[data-fsel="{first_id}"]'); await page.wait_for_timeout(200)
            check((await page.text_content("#evName")) == "Sommerfest SV Test", "Wechsel auf erstes Fest")
            names = await page.evaluate("window.__thekenfuchs.feste().list.map(f=>f.cfg.name)")
            check(names == ["Sommerfest SV Test", "Weinfest 2027"], f"Beide Feste gespeichert {names}")
            await page.fill("#f-newname", "Probe"); await page.click('[data-tpl="sample"]'); await page.click('[data-act="fnew"]'); await page.wait_for_timeout(200)
            check((await page.text_content("#evName")) == "Probe" and await page.locator(".key").count() == 13, "Beispiel-Vorlage mit eigenem Namen")
            sample_id = await page.evaluate("window.__thekenfuchs.feste().active")
            await page.click(f'[data-fdelask="{sample_id}"]'); await page.click(f'[data-fdel="{sample_id}"]'); await page.wait_for_timeout(200)
            check(await page.locator(".fest").count() == 2, "Aktives Fest gelöscht")
            check(await page.evaluate("window.__thekenfuchs.feste().list.some(f=>f.id===window.__thekenfuchs.feste().active)"), "Danach ist ein anderes Fest aktiv")
            await page.click('[data-act="discard"]')
            await page.reload(); await page.wait_for_timeout(400)
            check(await page.evaluate("window.__thekenfuchs.feste().list.length") == 2, "Feste überstehen Neustart")
            ls = await page.evaluate("Object.keys(localStorage).sort()")
            check(set(ls) <= {"thekenfuchs.feste.v1", "thekenfuchs.pin.v1", "thekenfuchs.geraet.v1"}, f"Storage nur Feste, PIN, Geräte-Einstellung {ls}")
            # Zweites Gerät: gleicher Name → aktualisieren statt doppelt
            await p2.click("#btnSettings")
            await p2.fill("#f-paste", code); await p2.click('[data-act="check"]'); await p2.wait_for_timeout(300)
            check(await p2.locator('[data-act="pending-upd"]').count() == 1, "Gleichnamiges Fest → 'aktualisieren' angeboten")
            await p2.click('[data-act="pending-new"]'); await p2.wait_for_timeout(200)
            check(await p2.locator(".fest").count() == 2, "Import als neues Fest")
            await p2.click('[data-act="discard"]')

            # Migration aus Version mit einer Preisliste
            ctx5 = await b.new_context(); p5 = await ctx5.new_page()
            await p5.goto(url)
            await p5.evaluate("""localStorage.clear(); localStorage.setItem('festrechner.preisliste.v1', JSON.stringify({name:'Altfest',cats:[{name:'Speisen',color:0,items:[['Wurst',300]]}]}))""")
            await p5.reload(); await p5.wait_for_timeout(300)
            check((await p5.text_content("#evName")) == "Altfest", "Alte Preisliste wird übernommen")

            # Manuelles Pfandglas: zählt auf dieselbe Pfandzeile
            await page.click('[data-key="1:3"]'); await page.click('[data-key="2:0"]')
            check((await page.text_content('[data-dec="2:0"] + span')).strip() == "2", "Wasser + extra Glas: Pfandzeile zählt 2")
            await page.click("#btnNext")
            async def open_set():
                await page.click("#btnSettings")
                for d in "1234": await page.click(f'[data-pin="{d}"]')
            # Automatik in der Pfandkategorie abschalten
            await open_set()
            check(await page.locator("#f-pfauto").count() == 0 and await page.locator('[data-cauto="2"]').count() == 1, "Pfand-Option sitzt in der Pfandkategorie")
            await page.click('[data-cauto="2"]'); await page.click('[data-act="save"]'); await page.wait_for_timeout(200)
            await page.click('[data-act="discard"]')
            await page.click('[data-key="1:0"]')
            check(await page.locator('[data-dec="2:0"]').count() == 0, "Automatik aus → kein Pfand")
            await page.click("#btnNext")
            # Zweiter Pfandwert, Auswahlmenü, Standard
            await open_set()
            await page.click('[data-cauto="2"]')
            check(await page.locator('[data-iref]').count() == 0, "Ein Pfandwert → kein Auswahlmenü")
            await page.click('[data-iadd="2"]'); await page.fill("#n-2-2", "Pfand Krug"); await page.fill("#p-2-2", "5,00")
            await page.click('[data-ipf="0:0"]')
            check(await page.locator('[data-iref="0:0"]').count() == 1, "Zwei Pfandwerte → Auswahlmenü erscheint")
            check((await page.input_value('[data-iref="0:0"]')) == "1", "Vorauswahl = Standard (Pfand Glas)")
            await page.select_option('[data-iref="0:0"]', "3")
            await page.click('[data-istd="2"]')
            await page.click('[data-ipf="0:1"]')
            check((await page.input_value('[data-iref="0:1"]')) == "3", "Neuer Standard Krug wird vorausgewählt")
            await page.click('[data-act="save"]'); await page.wait_for_timeout(200)
            await page.click('[data-act="discard"]')
            await page.click('[data-key="0:0"]')
            check((await page.text_content("#total")).strip() == "8,80 €", "Bratwurst 3,80 + Pfand Krug 5,00 = 8,80 €")
            check("+ Pfand Krug" in (await page.text_content('[data-key="0:0"] .kp')), "Taste zeigt '+ Pfand Krug'")
            await page.click('[data-key="1:0"]')
            check(await page.locator('[data-dec="2:0"]').count() == 1 and await page.locator('[data-dec="2:2"]').count() == 1, "Bier → Glas, Wurst → Krug: zwei Pfandzeilen")
            await page.click("#btnNext")
            # Verschieben und Löschen in der Pfandkategorie ziehen Verweise mit
            await open_set()
            await page.click('[data-imove="2:2:-1"]')
            await page.click('[data-idel="2:0"]')
            await page.click('[data-act="save"]'); await page.wait_for_timeout(200)
            await page.click('[data-act="discard"]')
            refs = await page.evaluate("(()=>{ const c=window.__thekenfuchs.cfg(); return {wurst:c.cats[0].items[0][2], bier:c.cats[1].items[0][2], pf:c.cats[2].pf, pfitems:c.cats[2].items.map(i=>i[0])}; })()")
            check(refs["pfitems"] == ["Pfand Krug", "Pfand zurück"] and refs["wurst"] == 1 and refs["bier"] == 1 and refs["pf"]["std"] == 0,
                  f"Nach Verschieben/Löschen zeigen Verweise richtig {refs}")
            pf_rt = await page.evaluate("""async()=>{ const f=window.__thekenfuchs; const c=await f.decodeText(await f.encodeCfg(f.cfg())); return JSON.stringify(c)===JSON.stringify(f.cfg()); }""")
            check(pf_rt, "Pfandkategorie, Standard und Verweise überleben den QR-Code")
            legacy = await page.evaluate("""async()=>{ const c=await window.__thekenfuchs.decodeText(JSON.stringify({v:1,n:'Alt',c:[['Getränke',1,[['Bier',400,1],['Kaffee',200]]],['Pfand',6,[['Pfand zurück',-200]]]],d:[1,250]})); return c; }""")
            check(legacy["cats"][1].get("pf") == {"auto": True, "std": 0} and legacy["cats"][1]["items"][0] == ["Pfand", 250] and legacy["cats"][0]["items"][0] == ["Bier", 400, 1] and len(legacy["cats"][0]["items"][1]) == 2,
                  "Zwischenversion (Pfandbetrag am Fest) wird in Pfandkategorie umgewandelt")

            # Auto-Addieren (Geräte-Einstellung)
            await open_set()
            await page.click("#f-autoadd")
            await page.click('[data-act="discard"]')
            check(await page.locator('[data-gop="add"]').count() == 0, "Auto-Addieren: +-Taste entfällt")
            await page.click('[data-key="0:3"]'); await page.click('[data-key="0:3"]'); await page.click('[data-key="0:3"]'); await page.click('[data-key="0:3"]'); await page.click('[data-key="0:3"]')
            await page.click('[data-coin="500"]'); await page.click('[data-coin="1000"]')
            check((await page.text_content("#givenAmt")).strip() == "gegeben 15,00 €", "Auto-Addieren: 5 € + 10 € = 15 €")
            await page.click('[data-gop="sub"]'); await page.click('[data-coin="500"]')
            check((await page.text_content("#givenAmt")).strip() == "gegeben 10,00 €", "Korrektur mit −: 15 € − 5 € = 10 €")
            await page.click('[data-coin="500"]')
            check((await page.text_content("#givenAmt")).strip() == "gegeben 15,00 €" and (await page.text_content("#changeAmt")).strip() == "0,00 €", "Danach wird wieder addiert; 5× Pommes 15 € passend")
            await page.reload(); await page.wait_for_timeout(300)
            check(await page.evaluate("JSON.parse(localStorage.getItem('thekenfuchs.geraet.v1')).autoAdd") == True and await page.locator('[data-gop="add"]').count() == 0, "Auto-Addieren bleibt nach Neustart an")
            check(await page.evaluate("Object.keys(JSON.parse(localStorage.getItem('thekenfuchs.geraet.v1')))") == ["autoAdd"], "Geräte-Einstellung enthält keine Beträge")

            # Installationsprofil: makeProfile erzeugt gültige plist
            import plistlib
            xml = await page.evaluate("window.__makeProfile('https://beispiel.github.io/festrechner/', false)")
            pl = plistlib.loads(xml.encode()); clip = pl["PayloadContent"][0]
            check(clip["PayloadType"] == "com.apple.webClip.managed" and clip["FullScreen"] and not clip["IsRemovable"] and clip["Icon"][:4] == b"\x89PNG" and clip["URL"].endswith("/festrechner/"),
                  "Web-Clip-Profil ist gültig (Vollbild, geschützt, Icon, URL)")
            check(await page.locator('[data-act="webclip"]').count() == 0, "Ohne HTTPS kein Profil-Button")

            # Demo: eigener Bereich, nichts im Speicher, Teilen-Link zeigt auf die App
            ctx6 = await b.new_context(viewport={"width": 1180, "height": 820}); p6 = await ctx6.new_page()
            await p6.goto(url); await p6.wait_for_timeout(300)
            await p6.evaluate("localStorage.setItem('thekenfuchs.feste.v1', JSON.stringify({active:'x',list:[{id:'x',cfg:{name:'Echtes Fest',cats:[{name:'Speisen',color:0,items:[['Wurst',300]]}]}}]}))")
            await p6.goto(demo_url); await p6.wait_for_timeout(400)
            check(not await p6.locator("#demoBar").is_hidden(), "Demo zeigt Hinweisleiste")
            check((await p6.text_content("#evName")) == "Sommerfest (Beispiel)", "Demo startet mit Beispiel, nicht mit echten Daten")
            await p6.click('[data-key="0:0"]'); await p6.click("#btnSettings")
            await p6.fill("#f-newname", "Demo-Fest"); await p6.click('[data-act="fnew"]'); await p6.wait_for_timeout(200)
            check(await p6.locator(".wc a[href='../install/']").count() == 1 and await p6.locator('[data-act="webclip"]').count() == 0, "Demo verweist auf Installation statt Profil")
            share = await p6.text_content("#sh-code")
            check(share.startswith(url + "#cfg="), "QR aus der Demo zeigt auf die App")
            real = await p6.evaluate("localStorage.getItem('thekenfuchs.feste.v1')")
            check("Echtes Fest" in real and "Demo-Fest" not in real, "Demo lässt echte Preislisten unangetastet")
            check(await p6.evaluate("navigator.serviceWorker.controller") is None, "Demo läuft ohne Service Worker")
            await p6.screenshot(path=f"{SHOTS}/demo.png")
            await p6.reload(); await p6.wait_for_timeout(300)
            check((await p6.text_content("#evName")) == "Sommerfest (Beispiel)", "Demo nach Neuladen zurückgesetzt")

            # Phone width
            ctx4 = await b.new_context(viewport={"width": 390, "height": 844})
            p4 = await ctx4.new_page(); await p4.goto(url); await p4.wait_for_timeout(300)
            await p4.click('[data-key="0:0"]'); await p4.click('[data-key="1:0"]')
            sw = await p4.evaluate("document.documentElement.scrollWidth")
            check(sw <= 390, f"Kein horizontales Scrollen bei 390 px ({sw})")
            await p4.screenshot(path=f"{SHOTS}/phone.png")

            bad = [e for e in errors if "favicon" not in e]
            check(not bad, f"Keine Konsolenfehler {bad[:3]}")
            await b.close()
    finally:
        srv.terminate()
    print("\n%d Fehler" % len(fails))
    return len(fails)

if __name__ == "__main__":
    sys.exit(1 if asyncio.run(main()) else 0)
