"""Run: python3 -m unittest tests/test_i18n.py -v   (needs dist/ from python3 build.py). Uses a temporary translation; leaves no files behind."""
import json, shutil, subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import i18n_build as ib
OUT = ROOT / "_test_site"; TR = ROOT / "i18n" / "pages" / "es" / "faq.json"; TR_DE = ROOT / "i18n" / "pages" / "de" / "faq.json"

def run(*a): return subprocess.run([sys.executable, *a], cwd=ROOT, capture_output=True, text=True)

class T(unittest.TestCase):
    def setUp(self):
        for d in (TR.parent, TR_DE.parent): d.mkdir(parents=True, exist_ok=True)
        self.h = (ROOT / "dist" / "faq.html").read_text(encoding="utf-8")
        keys = ib.extract_keys(self.h); self.k = keys[0]
        for f, pre in ((TR, "ES"), (TR_DE, "DE")):
            f.write_text(json.dumps({"source_hash": ib.source_hash(self.h), "title": f"{pre} Ayuda", "description": f"{pre} desc largo de prueba para la pagina de ayuda del sitio web", "replace": {self.k: f"{pre} TRAD"}}), encoding="utf-8")
    def tearDown(self):
        for f in (TR, TR_DE): f.unlink(missing_ok=True)
        for d in (TR.parent, TR_DE.parent):
            try: d.rmdir()
            except OSError: pass
        shutil.rmtree(OUT, ignore_errors=True)
    def build(self): return run("i18n_build.py", "build", "--out", "_test_site")

    def test_fresh_stale_missing_and_validator(self):
        self.assertEqual(self.build().returncode, 0)
        es = (OUT / "langs/es/faq.html").read_text(encoding="utf-8")
        self.assertIn("ES TRAD", es); self.assertIn("<title>ES Ayuda</title>", es)
        self.assertIn('<link rel="canonical" href="https://es.linuxonusb.com/faq.html">', es)
        self.assertIn('hreflang="de" href="https://de.linuxonusb.com/faq.html"', es)
        self.assertIn('hreflang="x-default" href="https://linuxonusb.com/faq.html"', es)
        en = (OUT / "en/faq.html").read_text(encoding="utf-8")
        self.assertIn('hreflang="es" href="https://es.linuxonusb.com/faq.html"', en)
        fr = (OUT / "langs/fr/faq.html").read_text(encoding="utf-8")   # untranslated -> fallback
        self.assertIn("noindex", fr); self.assertIn('rel="canonical" href="https://linuxonusb.com/faq.html"', fr); self.assertNotIn("hreflang", fr)
        self.assertIn("faq.html", (OUT / "langs/es/sitemap.xml").read_text()); self.assertFalse((OUT / "langs/fr/sitemap.xml").exists())
        self.assertEqual((OUT / "langs/es/CNAME").read_text().strip(), "es.linuxonusb.com")
        r = run("i18n_validate.py", "_test_site"); self.assertEqual(r.returncode, 0, r.stdout)

    def test_stale_translation_is_not_published(self):
        d = json.loads(TR.read_text()); d["source_hash"] = "0" * 16; TR.write_text(json.dumps(d))
        self.build(); es = (OUT / "langs/es/faq.html").read_text(encoding="utf-8")
        self.assertNotIn("ES TRAD", es); self.assertIn("noindex", es)
        self.assertIn("faq.html", json.loads((OUT / "i18n-report.json").read_text())["languages"]["es"]["stale_pages"][0])
        self.assertEqual(run("i18n_validate.py", "_test_site").returncode, 0)

    def test_validator_blocks_bad_output(self):
        self.build(); p = OUT / "langs/es/faq.html"; s = p.read_text(encoding="utf-8")
        p.write_text(s.replace('hreflang="de" href="https://de.linuxonusb.com/faq.html"', 'hreflang="de" href="https://de.linuxonusb.com/nope.html"'), encoding="utf-8")
        r = run("i18n_validate.py", "_test_site"); self.assertEqual(r.returncode, 1); self.assertIn("hreflang", r.stdout)
        p.write_text(s, encoding="utf-8"); (OUT / "langs/es/leak.txt").write_text("token ghp_" + "a" * 30)
        r = run("i18n_validate.py", "_test_site"); self.assertEqual(r.returncode, 1); self.assertIn("secret", r.stdout)
        (OUT / "langs/es/leak.txt").unlink(); (OUT / "langs/es/CNAME").write_text("evil.example.com\n")
        self.assertEqual(run("i18n_validate.py", "_test_site").returncode, 1)

    def test_subdirectory_mode(self):
        cfg = ROOT / "i18n" / "languages.json"; orig = cfg.read_text(encoding="utf-8")
        try:
            j = json.loads(orig); j["languages"][0]["mode"] = "subdirectory"; cfg.write_text(json.dumps(j), encoding="utf-8")
            self.assertEqual(self.build().returncode, 0)
            es = (OUT / "en/es/faq.html").read_text(encoding="utf-8")
            self.assertIn('rel="canonical" href="https://linuxonusb.com/es/faq.html"', es)
            self.assertIn("https://linuxonusb.com/es/sitemap.xml", (OUT / "en/sitemap.xml").read_text())
            self.assertFalse((OUT / "langs/es").exists())
            r = run("i18n_validate.py", "_test_site"); self.assertEqual(r.returncode, 0, r.stdout)
        finally: cfg.write_text(orig, encoding="utf-8")

if __name__ == "__main__": unittest.main()
