"""Builds static_site/: a Static Hugging Face Space that runs the app in the browser with stlite.

Every tool page carries all of its Python code and data inside the page itself, so the Space
only needs the four .html files: there are no sub-folders to upload.

Run from the project root:  python tools/build_static.py
Upload the contents of static_site/ to a Space created with the Static SDK.
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "static_site"
STLITE = sys.argv[1] if len(sys.argv) > 1 else "STLITE_VERSION"
TOOLS = [("fee.html", "PMS fee calculator", "app/pages/1_Fee_Calculator.py"),
         ("compare.html", "Compare vehicles", "app/pages/2_Compare_Vehicles.py"),
         ("dashboard.html", "Portfolio dashboard", "app/pages/3_Portfolio_Dashboard.py")]
EMPTY = ["app/__init__.py", "engine/__init__.py"]
CONFIG = {"theme.base": "dark", "theme.primaryColor": "#E0231C", "theme.backgroundColor": "#05070A",
          "theme.secondaryBackgroundColor": "#0A0E12", "theme.textColor": "#DFE7E0"}

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@stlite/mountable@__V__/build/stlite.css">
<style>html,body{margin:0;background:#05070a;color:#aab4ad;font-family:system-ui,sans-serif}
.wait{position:fixed;inset:0;display:grid;place-items:center;font-size:14px;pointer-events:none}
#root{position:relative;z-index:1}
.home{position:fixed;left:14px;bottom:14px;z-index:99999;padding:9px 16px;border:1px solid rgba(223,231,224,.25);border-radius:100px;background:#0a0e12;color:#dfe7e0;text-decoration:none;font-size:12px;letter-spacing:.12em}</style></head>
<body><div class="wait">Loading the tool. The first load can take about 20 seconds.</div><div id="root"></div>
<a class="home" href="index.html">Back to the start</a>
<script src="https://cdn.jsdelivr.net/npm/@stlite/mountable@__V__/build/stlite.js"></script>
<script>stlite.mount(__OPTIONS__, document.getElementById("root"));</script></body></html>
"""


def sources():
    files = [p for p in (ROOT / "app").glob("*.py") if p.name != "streamlit_app.py"]
    files += (ROOT / "app" / "pages").glob("*.py")
    files += (ROOT / "engine").glob("*.py")
    files += (ROOT / "data").glob("*.json")
    files += (ROOT / "data").glob("*.csv")
    return sorted(p for p in files if p.stat().st_size > 0)


def landing():
    s = (ROOT / "app" / "landing_component" / "index.html").read_text(encoding="utf-8")
    start = s.index("/* the Streamlit component protocol")
    end = s.index("var cl=function")
    swaps = [("html,body{margin:0;height:760px", "html,body{margin:0;height:100%"),
             ("#app{position:relative;height:760px;", "#app{position:relative;height:100vh;min-height:520px;"),
             ('<button class="go" type="button"></button>', '<a class="go"></a>'),
             ("go.textContent=c.cta;", "go.textContent=c.cta;go.href=c.path;"),
             ("path:'Fee_Calculator'", "path:'fee.html'"), ("path:'Compare_Vehicles'", "path:'compare.html'"),
             ("path:'Portfolio_Dashboard'", "path:'dashboard.html'")]
    s = s[:start] + s[end:]
    for a, b in swaps:
        assert a in s, a
        s = s.replace(a, b)
    return s


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir()
    mounted = {}
    for p in sources():
        rel = p.relative_to(ROOT).as_posix()
        mounted[rel] = p.read_text(encoding="utf-8")
    for rel in EMPTY:
        mounted[rel] = ""
    for page, title, entry in TOOLS:
        files = dict(mounted)
        files["entry.py"] = f"import runpy\nrunpy.run_path('{entry}', run_name='__main__')\n"
        options = {"requirements": ["altair<6"], "entrypoint": "entry.py", "files": files,
                   "streamlitConfig": CONFIG}
        html = (PAGE.replace("__TITLE__", title).replace("__V__", STLITE)
                .replace("__OPTIONS__", json.dumps(options).replace("</", "<\\/")))
        (OUT / page).write_text(html, encoding="utf-8")
    (OUT / "index.html").write_text(landing(), encoding="utf-8")
    (OUT / "README.md").write_text(
        "---\ntitle: PMS Toolkit\nemoji: 📈\ncolorFrom: red\ncolorTo: gray\nsdk: static\npinned: false\n---\n\n"
        "# PMS toolkit\n\nEducational only. Not investment advice. The Streamlit app runs in your browser "
        "using stlite, so the first load of each tool takes a little while.\n", encoding="utf-8")
    print("built", len(mounted) - len(EMPTY), "embedded files into", OUT)


if __name__ == "__main__":
    main()
