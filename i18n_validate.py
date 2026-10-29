#!/usr/bin/env python3
"""Validates the output of i18n_build.py before anything is deployed. Exit code 1 = do NOT deploy.
Usage: python3 i18n_validate.py _site        (standard library only)"""
import json, re, sys, xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
errors, warnings = [], []
def err(m): errors.append(m)

CANON = re.compile(r'<link rel="canonical" href="([^"]*)">')
ALT = re.compile(r'<link rel="alternate" hreflang="([^"]*)" href="([^"]*)">')
ROBOTS = re.compile(r'<meta name="robots" content="([^"]*)">')
HTML_LANG = re.compile(r'<html lang="([^"]*)"')
HREF = re.compile(r'href="([^"#?]+\.html)(?:[#?][^"]*)?"')
SECRET = re.compile(r"ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|gho_[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|AKIA[0-9A-Z]{16}")
BAD_NAMES = re.compile(r"(^\.env|\.pem$|\.key$|\.py$|\.map$|\.bak$|~$|^\.git(?!hub)|__pycache__|^node_modules$|\.DS_Store$|Thumbs\.db$)")
TEXT_EXT = {".html", ".xml", ".txt", ".js", ".json", ".css", ".webmanifest", ".md"}


def page_url(base, name):
    return base + "/" if name == "index.html" else f"{base}/{name}"


def check_site(root, s, en_base, alt_map):
    d = root / s["dir"]; code = s["code"]; base = s["base"]
    if not (d / "index.html").exists(): err(f"[{code}] index.html missing"); return
    indexable = set(s["indexable"])
    names = {p.name for p in d.glob("*.html")}
    if "404.html" not in names: err(f"[{code}] 404.html missing")
    sub_dirs = {x.name for x in d.iterdir() if x.is_dir()}
    for p in d.rglob("*"):
        if p.is_dir():
            if BAD_NAMES.search(p.name): err(f"[{code}] forbidden folder {p.relative_to(root)}")
            continue
        if BAD_NAMES.search(p.name): err(f"[{code}] forbidden file {p.relative_to(root)}")
        if p.suffix in TEXT_EXT and p.stat().st_size < 3_000_000 and "assets" not in p.parts[:3]:
            m = SECRET.search(p.read_text(encoding="utf-8", errors="ignore"))
            if m: err(f"[{code}] possible secret in {p.relative_to(root)} (matched pattern, value hidden)")
    for n in sorted(names):
        h = (d / n).read_text(encoding="utf-8")
        m = HTML_LANG.search(h)
        if not m or m.group(1) != code: err(f"[{code}] {n}: <html lang> is '{m.group(1) if m else None}', expected '{code}'")
        if s["mode"] != "root" and s.get("dir_attr") == "rtl" and 'dir="rtl"' not in h: err(f"[{code}] {n}: missing dir=rtl")
        for href in HREF.findall(h):
            if "://" in href or href.startswith("/") or href.startswith("mailto:"): continue
            if href not in names: err(f"[{code}] {n}: broken internal link {href}")
        if n == "404.html": continue
        canon = CANON.findall(h); alts = ALT.findall(h); rb = ROBOTS.findall(h)
        if len(canon) != 1: err(f"[{code}] {n}: expected exactly 1 canonical, found {len(canon)}"); continue
        url = page_url(base, n)
        if n in indexable:
            if canon[0] != url: err(f"[{code}] {n}: canonical {canon[0]} != {url}")
            if rb and "noindex" in rb[0]: err(f"[{code}] {n}: indexable page has noindex")
            langs = [a for a, _ in alts]
            if len(set(langs)) != len(langs): err(f"[{code}] {n}: duplicate hreflang values")
            if alts or code != "en":  # English pages only carry hreflang once a translation of them is live
                if "x-default" not in langs: err(f"[{code}] {n}: missing x-default")
                if code != "en" and code not in langs: err(f"[{code}] {n}: hreflang cluster lacks self ({code})")
                if code == "en" and "en-AU" not in langs: err(f"[{code}] {n}: missing en-AU")
            alt_map[url] = {a: u for a, u in alts}
            for a, u in alts:
                if not re.fullmatch(r"x-default|[a-z]{2,3}(-[A-Za-z]{2,4})?", a): err(f"[{code}] {n}: bad hreflang '{a}'")
        elif code != "en":
            if canon[0] != page_url(en_base, n): err(f"[{code}] {n}: fallback canonical must point to English ({canon[0]})")
            if not rb or "noindex" not in rb[0]: err(f"[{code}] {n}: untranslated fallback page must be noindex")
            if alts: err(f"[{code}] {n}: fallback page must not declare hreflang")
    # sitemaps
    sm = d / "sitemap.xml"
    if code != "en" and s["mode"] != "root":
        if indexable and not sm.exists(): err(f"[{code}] sitemap.xml missing although {len(indexable)} translated pages exist")
    if sm.exists():
        try: tree = ET.parse(sm)
        except ET.ParseError as e: err(f"[{code}] sitemap.xml is not valid XML: {e}"); return
        locs = [e.text.strip() for e in tree.iter() if e.tag.endswith("}loc")]
        if len(locs) != len(set(locs)): err(f"[{code}] sitemap.xml has duplicate URLs")
        if tree.getroot().tag.endswith("urlset"):
            for u in locs:
                if not u.startswith(base + "/"): err(f"[{code}] sitemap URL outside this site: {u}"); continue
                name = "index.html" if u == base + "/" else u[len(base) + 1:]
                if name not in indexable and code != "en": err(f"[{code}] sitemap lists non-translated page {u}")
                if not (d / name).exists(): err(f"[{code}] sitemap URL has no file: {u}")
    if s["mode"] == "subdomain":
        cn = d / "CNAME"
        if not cn.exists() or cn.read_text().strip() != s["host"]: err(f"[{code}] CNAME must contain {s['host']}")
        rt = (d / "robots.txt").read_text() if (d / "robots.txt").exists() else ""
        if indexable and f"Sitemap: {base}/sitemap.xml" not in rt: err(f"[{code}] robots.txt lacks its Sitemap line")


def main(root):
    root = Path(root); man_path = root / "manifest.json"
    if not man_path.exists(): err("manifest.json missing - run i18n_build.py first"); return finish()
    man = json.loads(man_path.read_text(encoding="utf-8")); cfg = json.loads((ROOT / "i18n" / "languages.json").read_text(encoding="utf-8"))
    en = next(s for s in man["sites"] if s["code"] == "en"); en_base = en["base"]
    if len(en["indexable"]) < cfg.get("minEnglishPages", 1): err(f"English site has only {len(en['indexable'])} pages (minimum {cfg.get('minEnglishPages')}); refusing to deploy a suspiciously small build")
    for f in list((ROOT / "i18n").rglob("*.json")):
        try:
            j = json.loads(f.read_text(encoding="utf-8"))
            if "pages" in f.parts and "source_hash" not in j: err(f"{f.relative_to(ROOT)}: missing source_hash")
        except ValueError as e: err(f"{f.relative_to(ROOT)}: invalid JSON ({e})")
    alt_map = {}
    for s in man["sites"]: check_site(root, s, en_base, alt_map)
    for url, alts in alt_map.items():  # hreflang reciprocity: every page you point to must point back
        for a, target in alts.items():
            if target == url: continue
            back = alt_map.get(target)
            if back is None: err(f"hreflang: {url} points to {target}, which is not an indexable page"); continue
            if url not in back.values(): err(f"hreflang: {url} -> {target}, but {target} does not link back")
    total = sum(p.stat().st_size for p in root.rglob("*") if p.is_file())
    if (root / "en").exists() and sum(p.stat().st_size for p in (root / "en").rglob("*") if p.is_file()) > 900_000_000: err("English site exceeds 900 MB (GitHub Pages limit is 1 GB)")
    finish(len(man["sites"]), total)


def finish(n=0, total=0):
    if errors:
        print(f"VALIDATION FAILED: {len(errors)} problem(s). Nothing will be deployed.")
        for e in errors[:60]: print(f"::error::{e}")
        if len(errors) > 60: print(f"... and {len(errors) - 60} more")
        sys.exit(1)
    print(f"Validation passed: {n} site(s), {total / 1e6:.0f} MB, no problems found.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "_site")
