#!/usr/bin/env python3
"""Build both portfolio sites from one source.

src/en.html and src/tr.html are the only page templates. Every value that differs
between the two domains (which name leads, which email comes first, which CV is
offered, canonical and language links) lives in SITES below, so the two sites
cannot drift apart the way the Yaldaz and Yildiz CVs once did.

  dist/yaldaz/      alpyaldaz.online       English
  dist/yildiz/      alpyildiz.online       Turkish (default)
  dist/yildiz/en/   alpyildiz.online/en/   English

Location and phone numbers are kept off both public sites on purpose (decided
2026-09-14). FORBIDDEN fails the build if either creeps back into a page. The CV
PDFs are checked separately, at generation time, by generate_cv_master.py.

Only files a page actually references are copied, so old PDFs lying around in
assests/ never get published.

Standard library only, so the GitHub Actions runner needs no installs.
Run: python3 build.py
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
DIST = ROOT / "dist"
SHARED_FILES = ["style.css", "mediaqueries.css", "script.js"]

FORBIDDEN = [
    "Berlin", "Istanbul", "İstanbul",
    "0538", "538 498", "572 279", "+48", "+90",
    "\u2014", "\u2013", "&mdash;", "&ndash;",  # em and en dash, Alp's standing rule
]

SITES = [
    {
        "key": "yaldaz",
        "domain": "alpyaldaz.online",
        "name": "Alp Yaldaz",
        "alt_name": "Alp Yıldız",
        "lead": "eu",
        "email_primary": "alpyaldaz59@gmail.com",
        "email_secondary": "alpyildiz59@gmail.com",
        "cv": "assests/AlpYaldaz_CV.pdf",
        "other_domain": "alpyildiz.online",
        "pages": [{"lang": "en", "path": ""}],
    },
    {
        "key": "yildiz",
        "domain": "alpyildiz.online",
        "name": "Alp Yıldız",
        "alt_name": "Alp Yaldaz",
        "lead": "tr",
        "email_primary": "alpyildiz59@gmail.com",
        "email_secondary": "alpyaldaz59@gmail.com",
        "cv": "assests/AlpYildiz_CV.pdf",
        "other_domain": "alpyaldaz.online",
        # First page is the default language, served at the domain root.
        "pages": [{"lang": "tr", "path": ""}, {"lang": "en", "path": "en/"}],
    },
]

META_NAMES = {
    ("en", "eu"): "Alp Yaldaz in Europe, Alp Yıldız in Türkiye, one person, two records.",
    ("en", "tr"): "Alp Yıldız in Türkiye, Alp Yaldaz in Europe, one person, two records.",
    ("tr", "tr"): "Türkiye'de Alp Yıldız, Avrupa'da Alp Yaldaz: aynı kişi, iki resmi kayıt.",
    ("tr", "eu"): "Avrupa'da Alp Yaldaz, Türkiye'de Alp Yıldız: aynı kişi, iki resmi kayıt.",
}

# Keyed by (page language, which audience the OTHER site faces).
OTHER_SITE_LABEL = {
    ("en", "tr"): "My Türkiye-facing site:",
    ("en", "eu"): "My Europe-facing site:",
    ("tr", "tr"): "Türkiye'ye yönelik sitem:",
    ("tr", "eu"): "Avrupa'ya yönelik sitem:",
}

# "TÜRKİYE" is written out in capitals: CSS uppercasing under lang="en" would
# drop the dot and print "TÜRKIYE".
NAME_ALT_LABELS = {"en": ("Europe", "TÜRKİYE"), "tr": ("Avrupa", "TÜRKİYE")}

LANG_ARIA = {"en": "English version", "tr": "Türkçe sürüm"}

NOT_FOUND = {
    "en": ("Page not found", "Back to the homepage"),
    "tr": ("Sayfa bulunamadı", "Ana sayfaya dön"),
}


def name_alt_block(lang, lead):
    eu_label, tr_label = NAME_ALT_LABELS[lang]
    eu = (eu_label, "Alp Yaldaz")
    tr = (tr_label, "Alp Yıldız")
    first, second = (eu, tr) if lead == "eu" else (tr, eu)
    part = (
        '          <span class="name-alt__part">\n'
        '            <span class="name-alt__label">{}</span>\n'
        '            <span class="name-alt__value">{}</span>\n'
        '          </span>\n'
    )
    return (
        '<p class="name-alt">\n'
        + part.format(*first)
        + '          <span class="name-alt__sep" aria-hidden="true"></span>\n'
        + part.format(*second)
        + '        </p>'
    )


def alternate_links(site):
    if len(site["pages"]) < 2:
        return ""
    base = f"https://{site['domain']}/"
    links = [f'\n    <link rel="alternate" hreflang="{p["lang"]}" href="{base}{p["path"]}" />' for p in site["pages"]]
    links.append(f'\n    <link rel="alternate" hreflang="x-default" href="{base}{site["pages"][0]["path"]}" />')
    return "".join(links)


def lang_switch(site, page):
    if len(site["pages"]) == 1:
        # Single-language site: the switch leads to the other domain's default page.
        other = next(s for s in SITES if s["domain"] == site["other_domain"])
        other_lang = other["pages"][0]["lang"]
        return {
            "LANG_HREF": f"https://{other['domain']}/",
            "LANG_LABEL": other_lang.upper(),
            "LANG_HREFLANG": other_lang,
            "LANG_ARIA": f"{LANG_ARIA[other_lang]} ({other['domain']})",
        }
    other_page = next(p for p in site["pages"] if p is not page)
    return {
        "LANG_HREF": "../" if page["path"] else other_page["path"],
        "LANG_LABEL": other_page["lang"].upper(),
        "LANG_HREFLANG": other_page["lang"],
        "LANG_ARIA": LANG_ARIA[other_page["lang"]],
    }


def page_values(site, page):
    lang = page["lang"]
    other_audience = "tr" if site["other_domain"] == "alpyildiz.online" else "eu"
    values = {
        "ROOT": "../" * page["path"].count("/"),
        "NAME": site["name"],
        "ALT_NAME": site["alt_name"],
        "META_NAMES": META_NAMES[(lang, site["lead"])],
        "PAGE_URL": f"https://{site['domain']}/{page['path']}",
        "ALTERNATE_LINKS": alternate_links(site),
        "EMAIL_PRIMARY": site["email_primary"],
        "EMAIL_SECONDARY": site["email_secondary"],
        "CV_FILE": site["cv"],
        "NAME_ALT_BLOCK": name_alt_block(lang, site["lead"]),
        "OTHER_SITE_LABEL": OTHER_SITE_LABEL[(lang, other_audience)],
        "OTHER_SITE_HOST": site["other_domain"],
    }
    values.update(lang_switch(site, page))
    return values


def render(template, values):
    out = template
    for key, value in values.items():
        out = out.replace("{{" + key + "}}", value)
    left = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", out)))
    if left:
        raise SystemExit(f"unreplaced placeholders: {left}")
    return out


def not_found_page(site):
    lang = site["pages"][0]["lang"]
    title, back = NOT_FOUND[lang]
    return f"""<!DOCTYPE html>
<html lang="{lang}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title} | {site['name']}</title>
    <link rel="stylesheet" href="/style.css" />
  </head>
  <body>
    <section style="min-height:80vh;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1rem;">
      <h1 class="title">404</h1>
      <p>{title}</p>
      <a class="btn btn-color-2" href="/">{back}</a>
    </section>
  </body>
</html>
"""


def build():
    templates = {lang: (SRC / f"{lang}.html").read_text(encoding="utf-8") for lang in ("en", "tr")}
    if DIST.exists():
        shutil.rmtree(DIST)
    errors = []
    for site in SITES:
        out_dir = DIST / site["key"]
        assets = set()
        for page in site["pages"]:
            where = f"{site['domain']}/{page['path']}"
            html = render(templates[page["lang"]], page_values(site, page))
            errors += [f"{where}: contains {bad!r}" for bad in FORBIDDEN if bad in html]
            ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
            try:
                json.loads(ld.group(1))
            except (AttributeError, ValueError) as exc:
                errors.append(f"{where}: JSON-LD invalid ({exc})")
            assets.update(re.findall(r"(?:\.\./)?(assests/[A-Za-z0-9._/-]+)", html))
            target = out_dir / page["path"] / "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(html, encoding="utf-8")
        for rel in sorted(assets) + SHARED_FILES:
            source = ROOT / rel
            if not source.is_file():
                errors.append(f"{site['domain']}: referenced file missing: {rel}")
                continue
            dest = out_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
        (out_dir / "CNAME").write_text(site["domain"] + "\n", encoding="utf-8")
        (out_dir / ".nojekyll").write_text("", encoding="utf-8")
        (out_dir / "404.html").write_text(not_found_page(site), encoding="utf-8")
        if site["key"] != "yaldaz":
            (out_dir / "README.md").write_text(
                f"# {site['domain']}\n\nGenerated by build.py in github.com/alpyaldaz/MyWebsite and force-pushed on every deploy.\n"
                "Do not edit files here; change src/ in MyWebsite instead.\n",
                encoding="utf-8",
            )
        pages = ", ".join(f"/{p['path']} ({p['lang']})" for p in site["pages"])
        print(f"{site['domain']}: {pages}, {len(assets)} referenced files")
    if errors:
        print("\nBUILD FAILED:", *errors, sep="\n  ")
        sys.exit(1)
    print("build OK")


if __name__ == "__main__":
    build()
