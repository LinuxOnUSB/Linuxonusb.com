#!/usr/bin/env python3
"""Builds the language editions from the finished English site (dist/). Standard library only.

  python3 build.py                              # 1. English site -> dist/
  python3 i18n_build.py build --out _site       # 2. -> _site/en (English + /<code>/ editions) and _site/langs/<code>
  python3 i18n_build.py status                  # translation freshness report
  python3 i18n_build.py export --lang es --pages stale,missing --limit 20 --out stubs

Translation files: i18n/pages/<code>/<page-name>.json  (see GITHUB_DEPLOYMENT_SETUP.md, section 12)
A page is only published as a translated, indexable page when its translation file's source_hash matches the
current English page. Otherwise it is served as an English fallback with noindex and canonical -> English.
"""
import argparse, hashlib, html, json, os, re, shutil, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
I18N = ROOT / "i18n"
MAIN_RE = re.compile(r"<main[^>]*>(.*?)</main>", re.S)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
DESC_RE = re.compile(r'<meta name="description" content="(.*?)">')
DATE_RE = re.compile(r"\b\d{1,2} (?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4}\b|\b\d{4}-\d{2}-\d{2}\b")
HREFLANG_RE = re.compile(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">\n?')
CANON_RE = re.compile(r'<link rel="canonical" href="([^"]*)">')
SELECT_RE = re.compile(r'<select id="lang" class="lang">.*?</select>', re.S)
LANG_JS_RE = re.compile(r'<script>\(function\(\)\{var l=document\.getElementById\("lang"\).*?</script>', re.S)
SWITCH_JS = ('<script>(function(){var l=document.getElementById("lang");if(l)l.addEventListener("change",function(){var v=l.value;if(!v)return;'
             'var p=location.pathname.split("/").pop()||"";if(/^https?:/.test(v)){location.href=v+p}else{location.href='
             '"https://translate.google.com/translate?sl=en&tl="+v+"&u="+encodeURIComponent(location.href.split("#")[0])}})})();</script>')
ENGLISH_GOOGLE = [("es", "Español"), ("fr", "Français"), ("de", "Deutsch"), ("pt", "Português"), ("it", "Italiano"), ("nl", "Nederlands"), ("pl", "Polski"), ("tr", "Türkçe"), ("ru", "Русский"), ("ar", "العربية"), ("hi", "हिन्दी"), ("id", "Bahasa Indonesia"), ("vi", "Tiếng Việt"), ("zh-CN", "简体中文"), ("ja", "日本語"), ("ko", "한국어")]


def load_config():
    cfg = json.loads((I18N / "languages.json").read_text(encoding="utf-8"))
    site = json.loads((ROOT / "catalog" / "products.json").read_text(encoding="utf-8"))["site"]
    cfg["en_base"] = site["baseUrl"].rstrip("/")
    cfg["domain"] = site.get("domain") or re.sub(r"^https?://", "", cfg["en_base"])
    for l in cfg["languages"]:
        l.setdefault("mode", cfg.get("defaultMode", "subdomain"))
        l.setdefault("dir", "ltr"); l.setdefault("enabled", True)
        l["var"] = "TARGET_REPO_" + l["code"].upper().replace("-", "_")
        if l["mode"] == "subdomain":
            l["host"] = f'{l["subdomain"]}.{cfg["domain"]}'
            l["base"] = f'https://{l["host"]}'; l["path"] = ""
        else:
            l["host"] = cfg["domain"]; l["path"] = "/" + l["code"].lower()
            l["base"] = cfg["en_base"] + l["path"]
    cfg["languages"] = [l for l in cfg["languages"] if l["enabled"]]
    return cfg


def page_url(base, name):
    return base + "/" if name == "index.html" else f"{base}/{name}"


def source_hash(h):
    m = MAIN_RE.search(h); main = m.group(1) if m else h
    t = TITLE_RE.search(h); d = DESC_RE.search(h)
    s = " ".join(DATE_RE.sub("", main).split()) + "|" + (t.group(1) if t else "") + "|" + (d.group(1) if d else "")
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def load_translation(code, name):
    p = I18N / "pages" / code / (name[:-5] + ".json")
    if not p.exists(): return None
    try: return json.loads(p.read_text(encoding="utf-8"))
    except ValueError as e: raise SystemExit(f"::error::Invalid JSON in {p}: {e}")


def classify(code, name, h):
    t = load_translation(code, name)
    if t is None: return "missing", None
    return ("fresh" if t.get("source_hash") == source_hash(h) else "stale"), t


def live_codes(cfg):
    """Languages that visitors may be linked to: subdirectory ones, plus subdomain ones whose repo variable is set."""
    raw = os.environ.get("VARS_JSON")
    if raw is None: return {l["code"] for l in cfg["languages"]}  # local run: treat all as live
    v = json.loads(raw or "{}")
    return {l["code"] for l in cfg["languages"] if l["mode"] == "subdirectory" or (v.get(l["var"]) or "").strip()}


def replace_text(h, key, val):
    if len(key) >= 30: return h.replace(key, val)
    return h.replace(f">{key}<", f">{val}<").replace(f'="{key}"', f'="{val}"')


def switcher(cfg, live, cur=None, ui=None):
    """<option> list for the language menu. Live languages link to their real site; others fall back to Google Translate (English site only)."""
    by = {l["code"]: l for l in cfg["languages"]}
    if cur is None:
        return '<option value="">Language</option>' + "".join(
            f'<option value="{by[c]["base"]}/">{n}</option>' if (c in live and c in by) else f'<option value="{c}">{n}</option>' for c, n in ENGLISH_GOOGLE)
    return (f'<option value="">{cur["name"]}</option><option value="{cfg["en_base"]}/">English</option>'
            + "".join(f'<option value="{l["base"]}/">{l["name"]}</option>' for l in cfg["languages"] if l["code"] in live and l["code"] != cur["code"]))


def extract_keys(h):
    m = MAIN_RE.search(h); main = m.group(1) if m else h
    main = re.sub(r"<(script|style)\b.*?</\1>", "", main, flags=re.S)
    seen, out = set(), []
    for t in re.findall(r">([^<>]{12,})<", main):
        t = t.strip()
        if len(t.split()) >= 2 and t not in seen: seen.add(t); out.append(t)
    return out


def with_alternates(h, name, en_base, alts):
    """alts: [(hreflang, url)] -> replace the head's hreflang block with the full cluster."""
    block = "".join(f'<link rel="alternate" hreflang="{a}" href="{u}">\n' for a, u in alts)
    h = HREFLANG_RE.sub("", h)
    return CANON_RE.sub(lambda m: m.group(0) + "\n" + block.rstrip("\n"), h, count=1)


def transform(h, name, lang, cfg, status, ui, live, cluster):
    en = cfg["en_base"]
    h = h.replace(en, lang["base"])
    h = h.replace('<html lang="en">', f'<html lang="{lang["code"]}"' + (' dir="rtl"' if lang["dir"] == "rtl" else "") + ">", 1)
    h = h.replace('content="en_AU"', f'content="{lang["locale"]}"').replace('"inLanguage": "en"', f'"inLanguage": "{lang["code"]}"')
    for k, v in ui.items(): h = replace_text(h, k, v)
    h = SELECT_RE.sub(f'<select id="lang" class="lang">{switcher(cfg, live, lang, ui)}</select>', h)
    h = LANG_JS_RE.sub(lambda m: SWITCH_JS, h)
    if name == "404.html":
        return h
    kind, t = status
    en_url = page_url(en, name)
    if kind == "fresh":
        if t.get("title") and (m := TITLE_RE.search(h)):
            old = m.group(1); h = h.replace(old, html.escape(t["title"], quote=False))
        if t.get("description") and (m := DESC_RE.search(h)):
            old = m.group(1); h = h.replace(old, html.escape(t["description"], quote=True))
        mm = MAIN_RE.search(h)
        if mm and t.get("replace"):
            main = mm.group(1)
            for k, v in t["replace"].items():
                main = re.sub(r">(\s*)" + re.escape(k) + r"(\s*)<", lambda m, v=v: ">" + m.group(1) + v + m.group(2) + "<", main)
            h = h[:mm.start(1)] + main + h[mm.end(1):]
        return with_alternates(h, name, en, cluster)
    h = CANON_RE.sub(f'<link rel="canonical" href="{en_url}">', h, count=1)
    h = HREFLANG_RE.sub("", h)
    return re.sub(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="noindex,follow">', h, count=1)


def sitemap(base, names, lastmod):
    rows = "".join(f"<url><loc>{page_url(base, n)}</loc><lastmod>{lastmod}</lastmod></url>\n" for n in names)
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + rows + "</urlset>\n"


def build(out):
    cfg = load_config(); dist = ROOT / "dist"
    if not (dist / "index.html").exists(): raise SystemExit("::error::dist/ is missing. Run python3 build.py first.")
    names = sorted(p.name for p in dist.glob("*.html"))
    pages = {n: (dist / n).read_text(encoding="utf-8") for n in names}
    live = live_codes(cfg); today = date.today().isoformat()
    status = {(l["code"], n): classify(l["code"], n, pages[n]) for l in cfg["languages"] for n in names if n != "404.html"}
    out = Path(out)
    if out.exists(): shutil.rmtree(out)
    en_out = out / "en"; shutil.copytree(dist, en_out)
    manifest = {"sites": [], "deploy": []}
    report = {"languages": {}, "stale_total": 0}

    # --- English: real language switcher + hreflang cluster for pages that have fresh translations
    for n in names:
        h = pages[n]
        h = SELECT_RE.sub(f'<select id="lang" class="lang">{switcher(cfg, live)}</select>', h)
        h = LANG_JS_RE.sub(lambda m: SWITCH_JS, h)
        fresh = [l for l in cfg["languages"] if n != "404.html" and status[(l["code"], n)][0] == "fresh"]
        if fresh:
            en_url = page_url(cfg["en_base"], n)
            alts = [("en-AU", en_url)] + [(l["code"], page_url(l["base"], n)) for l in fresh] + [("x-default", en_url)]
            h = with_alternates(h, n, cfg["en_base"], alts)
        (en_out / n).write_text(h, encoding="utf-8")
    en_pages = [n for n in names if n != "404.html"]
    manifest["sites"].append({"code": "en", "dir": "en", "base": cfg["en_base"], "indexable": en_pages, "mode": "root"})

    # --- language editions
    extra_sitemaps = []
    for lang in cfg["languages"]:
        code = lang["code"]; ui_path = I18N / "ui" / f"{code}.json"
        ui = json.loads(ui_path.read_text(encoding="utf-8")) if ui_path.exists() else {}
        target = (en_out / lang["code"].lower()) if lang["mode"] == "subdirectory" else (out / "langs" / code)
        target.mkdir(parents=True, exist_ok=True)
        for sub in ("assets", "img"):
            if (dist / sub).exists(): shutil.copytree(dist / sub, target / sub)
        shutil.copy(dist / "favicon.ico", target / "favicon.ico")
        (target / ".nojekyll").write_text("")
        wm = (dist / "site.webmanifest").read_text(encoding="utf-8").replace('"start_url": "/"', f'"start_url": "{lang["path"] or ""}/"')
        (target / "site.webmanifest").write_text(wm, encoding="utf-8")
        fresh_names = []
        counts = {"fresh": 0, "stale": 0, "missing": 0}; stale_list = []
        for n in names:
            st = status.get((code, n), ("missing", None))
            if n != "404.html":
                counts[st[0]] += 1
                if st[0] == "stale": stale_list.append(n)
            cluster = []
            if st[0] == "fresh":
                fresh_here = [(l, status[(l["code"], n)]) for l in cfg["languages"] if status[(l["code"], n)][0] == "fresh"]
                en_url = page_url(cfg["en_base"], n)
                cluster = [("en-AU", en_url)] + [(l["code"], page_url(l["base"], n)) for l, _ in fresh_here] + [("x-default", en_url)]
                fresh_names.append(n)
            (target / n).write_text(transform(pages[n], n, lang, cfg, st, ui, live, cluster), encoding="utf-8")
        if fresh_names:
            (target / "sitemap.xml").write_text(sitemap(lang["base"], fresh_names, today), encoding="utf-8")
            robots = f"User-agent: *\nAllow: /\n\nSitemap: {lang['base']}/sitemap.xml\n"
        else:
            robots = "User-agent: *\nAllow: /\n"
        if lang["mode"] == "subdomain":
            (target / "robots.txt").write_text(robots, encoding="utf-8")
            (target / "CNAME").write_text(lang["host"] + "\n", encoding="utf-8")
            if code in live: manifest["deploy"].append({"code": code, "var": lang["var"], "host": lang["host"]})
        elif fresh_names:
            extra_sitemaps.append(f'{lang["base"]}/sitemap.xml')
        manifest["sites"].append({"code": code, "dir": str(target.relative_to(out)), "base": lang["base"], "mode": lang["mode"], "host": lang["host"],
                                  "indexable": fresh_names, "all_pages": [n for n in names], "dir_attr": lang["dir"]})
        report["languages"][code] = {**counts, "stale_pages": stale_list}
        report["stale_total"] += counts["stale"]
    if extra_sitemaps:  # subdirectory languages are listed in the English sitemap index
        p = en_out / "sitemap.xml"; s = p.read_text(encoding="utf-8")
        add = "".join(f"<sitemap><loc>{u}</loc><lastmod>{today}</lastmod></sitemap>\n" for u in extra_sitemaps)
        p.write_text(s.replace("</sitemapindex>", add + "</sitemapindex>"), encoding="utf-8")
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    write_report(out, cfg, report, manifest)
    print(f"Built English ({len(names)} pages) + {len(cfg['languages'])} language editions into {out}/")
    print(f"Languages to deploy to their own repository: {[d['code'] for d in manifest['deploy']] or 'none'}")


def write_report(out, cfg, report, manifest):
    rows = ["| Language | Translated | Stale (needs review) | Not yet translated |", "|---|---|---|---|"]
    for c, r in report["languages"].items(): rows.append(f"| {c} | {r['fresh']} | {r['stale']} | {r['missing']} |")
    md = ["## Translation status", "", *rows, ""]
    if report["stale_total"]:
        md += ["### Pages whose English source changed after they were translated", "",
               "These are served as noindex English fallback pages until the translation file is updated.", ""]
        for c, r in report["languages"].items():
            if r["stale_pages"]:
                md.append(f"- **{c}**: " + ", ".join(r["stale_pages"][:40]) + (f" (+{len(r['stale_pages']) - 40} more)" if len(r["stale_pages"]) > 40 else ""))
    md += ["", "Deploying to own repositories: " + (", ".join(d["code"] for d in manifest["deploy"]) or "none (no TARGET_REPO_* variables set)")]
    (Path(out) / "i18n-report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (Path(out) / "i18n-report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    gh = os.environ.get("GITHUB_OUTPUT")
    if gh:
        with open(gh, "a") as f: f.write(f"stale_total={report['stale_total']}\n")
    summ = os.environ.get("GITHUB_STEP_SUMMARY")
    if summ:
        with open(summ, "a") as f: f.write("\n".join(md) + "\n")


def cmd_status(_):
    out = ROOT / "_status_tmp"; build(out)
    print((out / "i18n-report.md").read_text(encoding="utf-8")); shutil.rmtree(out)


def cmd_export(a):
    cfg = load_config(); dist = ROOT / "dist"
    if not any(l["code"] == a.lang for l in cfg["languages"]): raise SystemExit(f"Unknown language {a.lang}")
    want = [w.strip() for w in a.pages.split(",") if w.strip()]
    out = Path(a.out); (out / a.lang).mkdir(parents=True, exist_ok=True); n_done = 0
    for p in sorted(dist.glob("*.html")):
        if p.name == "404.html": continue
        h = p.read_text(encoding="utf-8"); kind, old = classify(a.lang, p.name, h)
        if not (kind in want or "all" in want or p.name in want or p.stem in want): continue
        if "all" not in want and p.name not in want and p.stem not in want and kind == "fresh": continue
        t = TITLE_RE.search(h); d = DESC_RE.search(h)
        stub = {"_instructions": f"Translate every VALUE below into the language '{a.lang}'. Keep the KEYS in English exactly as they are. Keep HTML entities such as &amp; and any tags unchanged. Do not change source_hash.",
                "source_hash": source_hash(h), "reviewed": False,
                "title": html.unescape(t.group(1)) if t else "", "description": html.unescape(d.group(1)) if d else "",
                "replace": {k: (old or {}).get("replace", {}).get(k, k) for k in extract_keys(h)}}
        (out / a.lang / (p.stem + ".json")).write_text(json.dumps(stub, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        n_done += 1
        if a.limit and n_done >= a.limit: break
    print(f"Wrote {n_done} translation stub(s) to {out / a.lang}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    b = sp.add_parser("build"); b.add_argument("--out", default="_site"); b.set_defaults(fn=lambda a: build(a.out))
    sp.add_parser("status").set_defaults(fn=cmd_status)
    e = sp.add_parser("export"); e.add_argument("--lang", required=True); e.add_argument("--pages", default="stale,missing")
    e.add_argument("--limit", type=int, default=20); e.add_argument("--out", default="translation-stubs"); e.set_defaults(fn=cmd_export)
    a = ap.parse_args(); a.fn(a)
