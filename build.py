#!/usr/bin/env python3
"""Generátor webu SlidesByHand.

Z jednoho zdroje (src/app.html a src/pages/*.html) vyrobí anglickou a českou verzi
aplikace a obsahové podstránky, a k nim sitemap.xml, llms.txt, llms-full.txt a 404.html.

Spuštění:  python3 build.py

Vygenerované soubory se ukládají do repozitáře, takže kdo si udělá kopii webu,
nic sestavovat nemusí. Generátor je potřeba jen při úpravě textů nebo aplikace.

Při každé změně obsahu uprav datum ZMENENO níže. Propíše se do všech stránek,
do strukturovaných dat i do sitemap.xml najednou.
"""
import html
import json
import os
import posixpath
import re

WEB = "https://slidesbyhand.com"
REPOZITAR = "https://github.com/pavel-horak-cz/app-slides-by-hand"
AUTOR_ID = "https://phorak.cz/#pavel-horak"
VZNIK = "2026-11-25"       # datum vzniku webu, nemění se
ZMENENO = "2026-11-26"     # datum poslední změny obsahu (RRRR-MM-DD, český čas)
POSUN = "+01:00"           # +01:00 v zimním čase, +02:00 v letním

KOREN = os.path.dirname(os.path.abspath(__file__))
JAZYKY = ("en", "cs")

# Stránky webu. "cesta" je adresa od kořene webu, "titulek" a "popis" jsou pro vyhledávače.
STRANKY = {
    "app": {
        "en": {"cesta": "", "menu": "Open the app",
               "titulek": "SlidesByHand: Control Your Slides with Hand Gestures",
               "popis": "Free browser app that turns your laptop camera into a presentation remote. Add a PDF, show your palm and turn pages by hand. No install, no account."},
        "cs": {"cesta": "cs/", "menu": "Otevřít aplikaci",
               "titulek": "SlidesByHand: ovládání prezentace gesty rukou",
               "popis": "Bezplatná aplikace v prohlížeči, která z kamery notebooku udělá ovladač prezentace. Nahraj PDF, ukaž dlaň a listuj rukou. Bez instalace, bez účtu."},
    },
    "about": {
        "en": {"cesta": "about/", "menu": "About", "nadpis": "What is SlidesByHand?",
               "titulek": "What Is SlidesByHand? Gestures, Privacy and FAQ",
               "popis": "How SlidesByHand works: the six gestures, your own PDF and sound, what happens to the camera image, and answers to common questions."},
        "cs": {"cesta": "cs/o-projektu/", "menu": "O projektu", "nadpis": "Co je SlidesByHand?",
               "titulek": "Co je SlidesByHand? Gesta, soukromí a časté otázky",
               "popis": "Jak SlidesByHand funguje: šest gest, vlastní PDF a zvuk, co se děje s obrazem z kamery a odpovědi na časté otázky."},
    },
    "howto": {
        "en": {"cesta": "how-to-control-slides-with-hand-gestures/", "menu": "How to",
               "nadpis": "How to control slides with hand gestures",
               "titulek": "How to Control Slides with Hand Gestures (5 Minutes)",
               "popis": "Step by step: save your presentation as a PDF, open SlidesByHand, practise the gestures and present without a clicker. No install needed."},
        "cs": {"cesta": "cs/jak-ovladat-prezentaci-gesty/", "menu": "Návod",
               "nadpis": "Jak ovládat prezentaci gesty",
               "titulek": "Jak ovládat prezentaci gesty rukou: návod krok za krokem",
               "popis": "Krok za krokem: ulož prezentaci jako PDF, otevři SlidesByHand, vyzkoušej si gesta a prezentuj bez ovladače. Bez instalace."},
    },
    "alt": {
        "en": {"cesta": "presentation-clicker-alternative/", "menu": "Clicker alternative",
               "nadpis": "A presentation clicker alternative that needs no hardware",
               "titulek": "A Free Presentation Clicker Alternative: Your Hand",
               "popis": "Forgot your clicker? SlidesByHand turns pages with hand gestures through the laptop camera. An honest comparison of a clicker and gesture control."},
        "cs": {"cesta": "cs/prezentace-bez-ovladace/", "menu": "Bez ovladače",
               "nadpis": "Prezentace bez ovladače",
               "titulek": "Prezentace bez ovladače: listuj rukou místo prezentéru",
               "popis": "Zapomněl jsi prezentér? SlidesByHand listuje gesty přes kameru notebooku. Poctivé srovnání ovladače prezentace a ovládání rukou."},
    },
}
OBSAHOVE = ("about", "howto", "alt")

# Ukázkové video na stránce O projektu (soubory jsou ve složce docs/)
VIDEO = {
    "en": {"soubor": "docs/demo-en.mp4", "nahled": "docs/demo-en.jpg", "delka": "PT29S", "nazev": "SlidesByHand in action",
           "popis": "An open palm starts the slides, an index finger turns the pages and a fist ends the presentation. Recorded in the browser, no clicker involved."},
    "cs": {"soubor": "docs/demo-cs.mp4", "nahled": "docs/demo-cs.jpg", "delka": "PT22S", "nazev": "SlidesByHand v akci",
           "popis": "Otevřená dlaň spustí prezentaci, ukazovák listuje a pěst ji ukončí. Natočeno v prohlížeči, bez ovladače."},
}

TEXTY = {
    "en": {"locale": "en_US", "og": "og-image.png", "druhy": "Česky", "domu": "Home",
           "vyzva_nadpis": "Try it now", "vyzva_text": "It takes a minute, costs nothing and needs no install.",
           "vytvoril": "Made by", "reklama": "Websites that Google and AI know about:",
           "kod": "Source code on GitHub", "licence": "MIT License", "proai": "For AI / LLM",
           "popis_webu": "Run your slides with hand gestures in front of a laptop camera.",
           "klicova": "SlidesByHand, control slides with hand gestures, gesture controlled presentation, presentation clicker alternative, hand tracking, webcam presentation remote, PDF presentation, Pavel Horák"},
    "cs": {"locale": "cs_CZ", "og": "og-image-cs.png", "druhy": "English", "domu": "Úvod",
           "vyzva_nadpis": "Vyzkoušej to hned", "vyzva_text": "Trvá to minutu, nic to nestojí a nic se neinstaluje.",
           "vytvoril": "Vytvořil", "reklama": "Weby, o kterých ví Google i umělá inteligence:",
           "kod": "Zdrojový kód na GitHubu", "licence": "Licence MIT", "proai": "Pro AI / LLM",
           "popis_webu": "Pusť prezentaci gesty rukou před kamerou notebooku.",
           "klicova": "SlidesByHand, ovládání prezentace gesty, prezentace bez ovladače, prezentér, gesta rukou, kamera, PDF prezentace, Pavel Horák"},
}


def nacti(cesta):
    with open(os.path.join(KOREN, cesta), encoding="utf-8") as soubor:
        return soubor.read()


def uloz(cesta, obsah):
    plna = os.path.join(KOREN, cesta)
    os.makedirs(os.path.dirname(plna) or KOREN, exist_ok=True)
    with open(plna, "w", encoding="utf-8", newline="\n") as soubor:
        soubor.write(obsah)
    print("  " + cesta)


def koren_od(cesta):
    """Relativní cesta ke kořeni webu ze stránky na dané adrese ('' nebo '../' ...)."""
    return "../" * cesta.count("/")


def odkaz(z, na):
    """Relativní odkaz ze stránky 'z' na stránku 'na' (obě jako cesty od kořene webu)."""
    vysledek = posixpath.relpath("/" + na, "/" + z)
    return "./" if vysledek == "." else vysledek + "/"


def adresa(cesta):
    return WEB + "/" + cesta


def bez_znacek(text):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text))).strip()


def druhy(jazyk):
    return "cs" if jazyk == "en" else "en"


# ---------------------------------------------------------------
# Hlavička stránky: značky pro vyhledávače, sociální sítě a strukturovaná data
# ---------------------------------------------------------------
def autor():
    return {"@type": "Person", "@id": AUTOR_ID, "name": "Pavel Horák", "url": "https://phorak.cz"}


def hlavicka(klic, jazyk, uzly_navic=()):
    s = STRANKY[klic][jazyk]
    t = TEXTY[jazyk]
    url = adresa(s["cesta"])
    koren = koren_od(s["cesta"])
    obrazek = WEB + "/" + t["og"]
    cas = ZMENENO + "T00:00:00" + POSUN
    e = lambda text: html.escape(text, quote=True)

    web = {"@type": "WebSite", "@id": WEB + "/#website", "url": WEB + "/", "name": "SlidesByHand",
           "description": TEXTY["en"]["popis_webu"], "inLanguage": ["en", "cs"],
           "publisher": {"@id": AUTOR_ID}, "copyrightYear": 2026, "copyrightHolder": {"@id": AUTOR_ID},
           "dateCreated": VZNIK + "T00:00:00+01:00", "dateModified": cas}
    stranka = {"@type": "AboutPage" if klic == "about" else "WebPage", "@id": url + "#webpage", "url": url,
               "name": s["titulek"], "description": s["popis"], "inLanguage": jazyk,
               "isPartOf": {"@id": WEB + "/#website"}, "about": {"@id": WEB + "/#app"},
               "primaryImageOfPage": obrazek, "datePublished": VZNIK if klic == "app" else "2026-11-26",
               "dateModified": cas, "author": autor(), "publisher": {"@id": AUTOR_ID}}
    uzly = [web, stranka]
    if klic == "app":
        uzly.append({
            "@type": "WebApplication", "@id": WEB + "/#app", "name": "SlidesByHand", "url": WEB + "/",
            "description": "A free web app that lets a speaker control a PDF presentation with hand gestures in front of a laptop camera. No clicker, no install, no account. Everything runs in the browser and nothing leaves the computer.",
            "applicationCategory": "BusinessApplication", "operatingSystem": "Any (runs in a web browser)",
            "browserRequirements": "Requires JavaScript, a camera and a modern browser. Tested in Chrome.",
            "inLanguage": ["en", "cs"], "isAccessibleForFree": True,
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
            "featureList": ["Start, page through and end a presentation with hand gestures",
                            "Pointer that follows the fingertip",
                            "Own PDF presentation and MP3 sound stored in the browser",
                            "Guided practice of the gestures", "Keyboard backup",
                            "English and Czech interface",
                            "Camera image, slides and sound never leave the computer"],
            "image": WEB + "/og-image.png", "screenshot": WEB + "/docs/screenshot.png",
            "license": "https://opensource.org/licenses/MIT", "isPartOf": {"@id": WEB + "/#website"},
            "datePublished": VZNIK, "dateModified": ZMENENO, "author": autor(), "creator": {"@id": AUTOR_ID}})
        uzly.append({
            "@type": "SoftwareSourceCode", "@id": WEB + "/#code", "name": "SlidesByHand",
            "description": "Source code of SlidesByHand, a browser app for controlling presentations with hand gestures.",
            "url": WEB + "/", "codeRepository": REPOZITAR, "license": "https://opensource.org/licenses/MIT",
            "programmingLanguage": "JavaScript", "targetProduct": {"@id": WEB + "/#app"}, "author": autor()})
    else:
        stranka["breadcrumb"] = {"@id": url + "#breadcrumb"}
        uzly.append({"@type": "BreadcrumbList", "@id": url + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "SlidesByHand", "item": adresa(STRANKY["app"][jazyk]["cesta"])},
            {"@type": "ListItem", "position": 2, "name": s["nadpis"], "item": url}]})
    uzly.extend(uzly_navic)
    data = json.dumps({"@context": "https://schema.org", "@graph": uzly}, ensure_ascii=False, indent=2)

    dj = druhy(jazyk)
    radky = [
        "<!-- Základní SEO -->",
        f"<title>{e(s['titulek'])}</title>",
        f'<meta name="description" content="{e(s["popis"])}">',
        f'<meta name="keywords" content="{e(t["klicova"])}">',
        '<meta name="author" content="Pavel Horák">',
        '<meta name="creator" content="Pavel Horák">',
        '<meta name="publisher" content="Pavel Horák">',
        '<meta name="copyright" content="© 2026 Pavel Horák">',
        '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">',
        f'<link rel="canonical" href="{url}">',
        "<!-- Jazykové verze téže stránky -->",
        f'<link rel="alternate" hreflang="en" href="{adresa(STRANKY[klic]["en"]["cesta"])}">',
        f'<link rel="alternate" hreflang="cs" href="{adresa(STRANKY[klic]["cs"]["cesta"])}">',
        f'<link rel="alternate" hreflang="x-default" href="{adresa(STRANKY[klic]["en"]["cesta"])}">',
        f'<link rel="icon" type="image/svg+xml" href="{koren}favicon.svg">',
        f'<link rel="apple-touch-icon" href="{koren}favicon.svg">',
        '<link rel="license" href="https://opensource.org/licenses/MIT">',
        f'<link rel="alternate" type="text/plain" title="llms.txt" href="{koren}llms.txt">',
        "<!-- Časové údaje -->",
        f'<meta name="date" content="{VZNIK}">',
        f'<meta name="dcterms.modified" content="{ZMENENO}">',
        "<!-- Open Graph / Facebook / LinkedIn -->",
        f'<meta property="og:type" content="{"website" if klic == "app" else "article"}">',
        '<meta property="og:site_name" content="SlidesByHand">',
        f'<meta property="og:title" content="{e(s["titulek"])}">',
        f'<meta property="og:description" content="{e(s["popis"])}">',
        f'<meta property="og:image" content="{obrazek}">',
        '<meta property="og:image:width" content="1280">',
        '<meta property="og:image:height" content="640">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:locale" content="{t["locale"]}">',
        f'<meta property="og:locale:alternate" content="{TEXTY[dj]["locale"]}">',
        f'<meta property="article:author" content="{AUTOR_ID}">',
        "<!-- Twitter Card -->",
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{e(s["titulek"])}">',
        f'<meta name="twitter:description" content="{e(s["popis"])}">',
        f'<meta name="twitter:image" content="{obrazek}">',
        '<meta name="twitter:creator" content="@PavelHorakCZ">',
        "<!-- Schema.org. Autor odkazuje na centrální identitu na phorak.cz. -->",
        '<script type="application/ld+json">', data, "</script>",
    ]
    return "\n".join(radky)


# ---------------------------------------------------------------
# Aplikace: jedna šablona, dvě jazykové verze
# ---------------------------------------------------------------
def slovnik_en(zdroj):
    """Anglický slovník je součástí skriptu aplikace (klíčem je český text)."""
    nalez = re.search(r"const EN = (\{.*?\n\});", zdroj, re.S)
    return json.loads(nalez.group(1))


def preloz_staticky(zdroj, en):
    """Přeloží pevné texty a popisky v těle stránky do angličtiny, stejně jako to dřív dělal skript."""
    zacatek = zdroj.index("<body>")
    konec = zdroj.index('<script type="module">')
    telo = zdroj[zacatek:konec]

    def text(nalez):
        puvodni = nalez.group(1)
        klic = " ".join(puvodni.split())
        if klic not in en:
            return nalez.group(0)
        pred = puvodni[:len(puvodni) - len(puvodni.lstrip())]
        po = puvodni[len(puvodni.rstrip()):]
        return ">" + pred + html.escape(en[klic], quote=False) + po + "<"

    def atribut(nalez):
        hodnota = html.unescape(nalez.group(2))
        if hodnota not in en:
            return nalez.group(0)
        return nalez.group(1) + '="' + html.escape(en[hodnota], quote=True) + '"'

    telo = re.sub(r">([^<>]*[^\s<>][^<>]*)<", text, telo)
    telo = re.sub(r'\b(title|aria-label|alt)="([^"]*)"', atribut, telo)
    return zdroj[:zacatek] + telo + zdroj[konec:]


def sestav_aplikaci(zdroj, jazyk, en):
    s = STRANKY["app"][jazyk]
    dj = druhy(jazyk)
    vystup = preloz_staticky(zdroj, en) if jazyk == "en" else zdroj
    nahrady = {
        "{{lang}}": jazyk,
        "{{head}}": hlavicka("app", jazyk),
        "{{root}}": koren_od(s["cesta"]),
        "{{url_other}}": odkaz(s["cesta"], STRANKY["app"][dj]["cesta"]),
        "{{lang_other}}": dj,
        "{{label_other}}": dj.upper(),
        "{{url_about}}": odkaz(s["cesta"], STRANKY["about"][jazyk]["cesta"]),
    }
    for znacka, hodnota in nahrady.items():
        vystup = vystup.replace(znacka, hodnota)
    assert "{{" not in vystup.split('<script type="module">')[0], "V šabloně zůstala nevyplněná značka"
    poznamka = "<!-- VYGENEROVÁNO skriptem build.py ze souboru src/app.html. Neupravuj ručně, uprav zdroj a spusť generátor. -->\n"
    return vystup.replace("<!DOCTYPE html>\n", "<!DOCTYPE html>\n" + poznamka, 1)


# ---------------------------------------------------------------
# Obsahové stránky
# ---------------------------------------------------------------
def ikony(zdroj):
    """Sada obrysových ikon z aplikace, aby je šlo použít i v textu stránek."""
    return re.search(r'<svg class="sada".*?</svg>', zdroj, re.S).group(0)


def otazky(telo):
    blok = re.search(r'<div class="faq">(.*)</div>', telo, re.S)
    if not blok:
        return None
    pary = re.findall(r"<h3>(.*?)</h3>\s*<p>(.*?)</p>", blok.group(1), re.S)
    return [{"@type": "Question", "name": bez_znacek(o),
             "acceptedAnswer": {"@type": "Answer", "text": bez_znacek(a)}} for o, a in pary]


def kroky(telo):
    blok = re.search(r'<ol class="kroky">(.*?)</ol>', telo, re.S)
    if not blok:
        return None
    vysledek = []
    for i, polozka in enumerate(re.findall(r"<li>(.*?)</li>", blok.group(1), re.S), 1):
        nazev = re.search(r"<strong>(.*?)</strong>", polozka, re.S)
        vysledek.append({"@type": "HowToStep", "position": i,
                         "name": bez_znacek(nazev.group(1)).rstrip("."), "text": bez_znacek(polozka)})
    return vysledek


def sestav_stranku(klic, jazyk, sada):
    s = STRANKY[klic][jazyk]
    t = TEXTY[jazyk]
    dj = druhy(jazyk)
    koren = koren_od(s["cesta"])
    na = lambda cil, j=jazyk: odkaz(s["cesta"], STRANKY[cil][j]["cesta"])
    url = adresa(s["cesta"])

    telo = nacti(f"src/pages/{klic}.{jazyk}.html")
    for cil in ("app", "about", "howto", "alt"):
        telo = telo.replace("{{" + cil + "}}", na(cil))
    telo = re.sub(r"\{\{ik:(\w+)\}\}", r'<svg class="ik" aria-hidden="true"><use href="#i-\1"/></svg>', telo)
    # Každá otázka s odpovědí dostane vlastní obal, aby se na široké obrazovce daly řadit do dvou sloupců
    telo = re.sub(r'(<div class="faq">)(.*?)(</div>)',
                  lambda n: n.group(1) + re.sub(r"(<h3>.*?</h3>\s*<p>.*?</p>)", r"<div>\1</div>", n.group(2), flags=re.S) + n.group(3),
                  telo, flags=re.S)
    navic = []
    if "{{video}}" in telo:
        v = VIDEO[jazyk]
        telo = telo.replace("{{video}}", f'''<figure class="ukazka">
  <video autoplay muted loop playsinline controls preload="metadata" width="1280" height="648" poster="{koren}{v['nahled']}" aria-label="{html.escape(v['nazev'])}">
    <source src="{koren}{v['soubor']}" type="video/mp4">
  </video>
  <figcaption>{html.escape(v['popis'])}</figcaption>
</figure>''')
        navic.append({"@type": "VideoObject", "@id": url + "#video", "name": v["nazev"], "description": v["popis"],
                      "thumbnailUrl": WEB + "/" + v["nahled"], "contentUrl": WEB + "/" + v["soubor"],
                      "uploadDate": ZMENENO + "T00:00:00" + POSUN, "duration": v["delka"], "inLanguage": jazyk,
                      "isPartOf": {"@id": url + "#webpage"}, "author": autor()})
    assert "{{" not in telo, f"Nevyplněná značka v {klic}.{jazyk}"

    seznam_otazek = otazky(telo)
    if seznam_otazek:
        navic.append({"@type": "FAQPage", "@id": url + "#faq", "inLanguage": jazyk,
                      "isPartOf": {"@id": url + "#webpage"}, "mainEntity": seznam_otazek})
    seznam_kroku = kroky(telo)
    if seznam_kroku:
        navic.append({"@type": "HowTo", "@id": url + "#howto", "name": s["nadpis"], "description": s["popis"],
                      "inLanguage": jazyk, "totalTime": "PT5M",
                      "tool": [{"@type": "HowToTool", "name": "Laptop with a camera" if jazyk == "en" else "Notebook s kamerou"},
                               {"@type": "HowToTool", "name": "SlidesByHand", "url": WEB + "/"}],
                      "supply": [{"@type": "HowToSupply", "name": "Presentation saved as a PDF" if jazyk == "en" else "Prezentace uložená jako PDF"}],
                      "step": seznam_kroku})

    menu = "".join(
        f'<a href="{na(k)}"{" aria-current=\"page\"" if k == klic else ""}>{html.escape(STRANKY[k][jazyk]["menu"])}</a>'
        for k in OBSAHOVE)
    return f"""<!DOCTYPE html>
<!-- VYGENEROVÁNO skriptem build.py ze souboru src/pages/{klic}.{jazyk}.html. Neupravuj ručně, uprav zdroj a spusť generátor. -->
<html lang="{jazyk}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#FFB20F">
{hlavicka(klic, jazyk, navic)}
<link rel="stylesheet" href="{koren}site.css">
</head>
<body>
{sada}
<header class="zahlavi">
  <div class="obal radek">
    <a class="znacka" href="{na('app')}"><svg class="ik" aria-hidden="true"><use href="#i-dlan"/></svg>SlidesByHand</a>
    <nav aria-label="{'Main' if jazyk == 'en' else 'Hlavní'}">{menu}<a class="jazyk" href="{na(klic, dj)}" hreflang="{dj}" lang="{dj}">{t['druhy']}</a></nav>
  </div>
  <div class="obal uvod">
    <p class="drobecky"><a href="{na('app')}">SlidesByHand</a> <span aria-hidden="true">/</span> {html.escape(s['menu'])}</p>
    <h1>{html.escape(s['nadpis'])}</h1>
    <a class="tlacitko" href="{na('app')}">{html.escape(STRANKY['app'][jazyk]['menu'])}</a>
  </div>
</header>
<main class="obal">
<article>
{telo.strip()}
</article>
<aside class="vyzva">
  <div class="text">
    <h2>{t['vyzva_nadpis']}</h2>
    <p>{t['vyzva_text']}</p>
  </div>
  <a class="tlacitko" href="{na('app')}">{html.escape(STRANKY['app'][jazyk]['menu'])}</a>
</aside>
</main>
<footer class="zapati">
  <div class="obal">
    <p>{t['vytvoril']} <a href="https://pprojects.cz" rel="author noopener">Pavel Horák</a> <span aria-hidden="true">·</span> {t['reklama']} <a href="https://webseoai.cz" rel="noopener">webseoai.cz</a></p>
    <p><a href="{REPOZITAR}" rel="noopener">{t['kod']}</a> <span aria-hidden="true">·</span> <a href="https://opensource.org/licenses/MIT" rel="license noopener">{t['licence']}</a> <span aria-hidden="true">·</span> <a href="{koren}llms.txt">{t['proai']}</a></p>
  </div>
</footer>
</body>
</html>
"""


# ---------------------------------------------------------------
# Soubory pro roboty a umělou inteligenci
# ---------------------------------------------------------------
def sitemap():
    polozky = []
    for klic in STRANKY:
        for jazyk in JAZYKY:
            vazby = "".join(
                f'\n    <xhtml:link rel="alternate" hreflang="{j}" href="{adresa(STRANKY[klic][j if j != "x-default" else "en"]["cesta"])}"/>'
                for j in ("en", "cs", "x-default"))
            polozky.append(f"  <url>\n    <loc>{adresa(STRANKY[klic][jazyk]['cesta'])}</loc>\n    <lastmod>{ZMENENO}</lastmod>{vazby}\n  </url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(polozky) + "\n</urlset>\n")


def llms():
    def seznam(jazyk):
        return "\n".join(f"- [{STRANKY[k][jazyk].get('nadpis', 'SlidesByHand')}]({adresa(STRANKY[k][jazyk]['cesta'])}): {STRANKY[k][jazyk]['popis']}"
                         for k in STRANKY)
    return f"""# SlidesByHand

> SlidesByHand is a free web app that lets a speaker control a PDF presentation with hand gestures in front of a laptop camera. No clicker, no install, no account. Everything runs in the browser and nothing leaves the user's computer. Made by Pavel Horák. Open source under the MIT License.

## Pages in English

{seznam('en')}

## Stránky v češtině

{seznam('cs')}

## Who it is for

Speakers at meetups, trainers, teachers and anyone who connects a laptop to a TV or projector and does not want to hunt for the right window or hold a clicker.

## Gestures

- Open palm: starts the presentation
- Index finger pointing right: next page
- Index finger pointing left: previous page
- Both index fingers up: turns on a pointer, a red dot that follows the fingertip
- Both index fingers down: turns the pointer off
- Fist: ends the presentation

Every gesture has to be held for about a second while a ring on the screen fills up, so nothing fires by accident. A keyboard backup is always available (Enter, arrows, Backspace).

## Features

- Own presentation: drag a PDF onto the page. PowerPoint, Keynote and Google Slides can export to PDF.
- Own sound: drag an MP3 onto the page.
- Files are stored in the browser on the user's computer and stay there for the next visit.
- "Learn the gestures": a guided practice of all six gestures with live feedback from the camera.
- A sample presentation that teaches the gestures is built in.
- English and Czech interface, each on its own address.

## Privacy

- The camera image is processed in the browser. It is not recorded, stored or sent anywhere.
- The presentation and the sound stay in the browser's storage on the user's computer.
- No accounts, no cookies, no tracking.

## How it works

- Hand tracking: MediaPipe Hand Landmarker, running in the browser, returns 21 points for each hand.
- Gesture recognition: plain geometry over those points (distances and directions of fingers).
- Slides: PDF.js renders the pages in the browser.
- Requirements: a modern browser (tested in Chrome), a camera, and an HTTPS connection. The first load is about 30 MB.

## Source code

- [Repository on GitHub]({REPOZITAR}): static files, MIT licensed. Anyone can fork it and run their own copy on GitHub Pages.
- [Full text of all pages for AI](https://slidesbyhand.com/llms-full.txt)

## Author

- Pavel Horák builds websites and web apps.
- [Portfolio of projects](https://pprojects.cz)
- [Websites that Google and AI know about (webseoai.cz)](https://webseoai.cz)
- [Personal site and CV](https://phorak.cz)
- [Custom work and contact (hodinovyvibecoder.cz)](https://hodinovyvibecoder.cz)
- [LinkedIn](https://www.linkedin.com/in/pavelhorakeu)
- [X](https://x.com/PavelHorakCZ)
- [GitHub](https://github.com/pavel-horak-cz)

## License

MIT. If you use SlidesByHand or build on it, the author asks you to keep a visible link to https://slidesbyhand.com.

Last updated: {ZMENENO}
"""


def llms_plny():
    def na_text(telo):
        telo = re.sub(r"\{\{ik:\w+\}\}", "", telo)
        telo = telo.replace("{{video}}", "")
        telo = re.sub(r"\{\{\w+\}\}", WEB + "/", telo)
        telo = re.sub(r"<h2>(.*?)</h2>", r"\n\n### \1\n\n", telo, flags=re.S)
        telo = re.sub(r"<h3>(.*?)</h3>", r"\n\n**\1**\n\n", telo, flags=re.S)
        telo = re.sub(r"<li>(.*?)</li>", r"\n- \1", telo, flags=re.S)
        telo = re.sub(r"</tr>", "\n", telo)
        telo = re.sub(r"</t[dh]>\s*<t[dh]>", " | ", telo)
        telo = re.sub(r"</p>", "\n\n", telo)
        telo = html.unescape(re.sub(r"<[^>]+>", "", telo))
        telo = re.sub(r"[ \t]+", " ", telo)
        return re.sub(r"\n\s*\n\s*\n+", "\n\n", telo).strip()

    casti = ["# SlidesByHand: full text of all pages",
             "> Complete text of the content pages of slidesbyhand.com, in English and in Czech, for AI assistants and language models. "
             "The app itself is at https://slidesbyhand.com/ (English) and https://slidesbyhand.com/cs/ (Czech). "
             f"Author: Pavel Horák (https://phorak.cz). Last updated: {ZMENENO}."]
    for jazyk in JAZYKY:
        for klic in OBSAHOVE:
            s = STRANKY[klic][jazyk]
            casti.append(f"## {s['nadpis']}\n\nAddress: {adresa(s['cesta'])}\nLanguage: {jazyk}\n\n"
                         + na_text(nacti(f"src/pages/{klic}.{jazyk}.html")))
    return "\n\n".join(casti) + "\n"


def stranka_404(sada):
    return f"""<!DOCTYPE html>
<!-- VYGENEROVÁNO skriptem build.py. Neupravuj ručně. -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#FFB20F">
<title>Page not found | SlidesByHand</title>
<meta name="robots" content="noindex">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="stylesheet" href="/site.css">
</head>
<body>
{sada}
<header class="zahlavi">
  <div class="obal radek">
    <a class="znacka" href="/"><svg class="ik" aria-hidden="true"><use href="#i-dlan"/></svg>SlidesByHand</a>
  </div>
  <div class="obal uvod">
    <h1>This page does not exist.</h1>
    <p class="drobecky" lang="cs">Tahle stránka neexistuje.</p>
    <a class="tlacitko" href="/">Open the app</a> <a class="tlacitko obrys" href="/cs/" lang="cs">Česká verze</a>
  </div>
</header>
</body>
</html>
"""


def main():
    print("Generuji web SlidesByHand:")
    zdroj = nacti("src/app.html")
    en = slovnik_en(zdroj)
    sada = ikony(zdroj)
    for jazyk in JAZYKY:
        uloz(STRANKY["app"][jazyk]["cesta"] + "index.html", sestav_aplikaci(zdroj, jazyk, en))
    for klic in OBSAHOVE:
        for jazyk in JAZYKY:
            uloz(STRANKY[klic][jazyk]["cesta"] + "index.html", sestav_stranku(klic, jazyk, sada))
    uloz("sitemap.xml", sitemap())
    uloz("llms.txt", llms())
    uloz("llms-full.txt", llms_plny())
    uloz("404.html", stranka_404(sada))
    print("Hotovo. Datum změny:", ZMENENO)


if __name__ == "__main__":
    main()
