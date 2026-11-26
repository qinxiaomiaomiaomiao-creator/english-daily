#!/usr/bin/env python3
"""Rebuild the two per-child pages of 英语日课 from the latest merged site.

Usage:
    python3 _tools/build.py SRC_DIR [REPO_DIR]

SRC_DIR   folder of the latest merged web version: index.html (the page that
          carries both courses as base64 in <script id="src:ph"> / "src:lb")
          plus audio/*.mp3.  This is the same folder that is published as the
          claude.ai artifact 「心远和悠然的英语日课」.
REPO_DIR  checkout of github.com/qinxiaomiaomiaomiao-creator/english-daily
          (default: the folder above _tools/).

What it writes into REPO_DIR (nothing else is touched, .git is kept):
    index.html            chooser page (秦心远 / 秦悠然)
    .nojekyll
    audio/                replaced by SRC_DIR/audio
    xinyuan/index.html    秦心远's copy
    youran/index.html     秦悠然's copy

Per-child changes:
  * every localStorage key is prefixed "xinyuan/" or "youran/" (a shim is
    injected first in <head> of the outer page and of both course pages),
    because both copies share one origin on GitHub Pages;
  * audio is loaded from ../audio/ (shared by both copies);
  * the child's name in <title>, a name chip in the header, and the 今日
    greeting; home-screen icon name 心远英语 / 悠然英语.

If the source page changes the strings this script edits, sub1() stops with
an AssertionError naming the string: update the pattern here, never skip it.
"""
import base64, os, re, shutil, sys

KIDS = [
    ("xinyuan", "秦心远", "心远英语"),
    ("youran", "秦悠然", "悠然英语"),
]


def shim(ns):
    return (
        "<script>(function(){try{var P=%r;var S=window.Storage&&Storage.prototype;"
        "if(!S||S.__ns)return;var g=S.getItem,s=S.setItem,r=S.removeItem,c=S.clear,k=S.key;"
        "function L(t){try{return t===window.localStorage}catch(e){return false}}"
        "S.getItem=function(x){return g.call(this,L(this)?P+x:x)};"
        "S.setItem=function(x,v){return s.call(this,L(this)?P+x:x,v)};"
        "S.removeItem=function(x){return r.call(this,L(this)?P+x:x)};"
        "S.clear=function(){if(!L(this))return c.call(this);"
        "for(var i=this.length-1;i>=0;i--){var n=k.call(this,i);if(n&&n.indexOf(P)===0)r.call(this,n)}};"
        "S.__ns=1;}catch(e){}})();</script>" % (ns + "/")
    )


def sub1(s, old, new):
    n = s.count(old)
    assert n == 1, "expected exactly one %r, found %d" % (old, n)
    return s.replace(old, new)


def inject_head(html, ns):
    i = html.index("<head>") + len("<head>")
    return html[:i] + shim(ns) + html[i:]


def build_kid(src, slug, name, short):
    s = src
    for k in ("ph", "lb"):
        m = re.search(r'(<script type="text/plain" id="src:%s">)(.*?)(</script>)' % k, s, re.S)
        assert m, "course block src:%s not found" % k
        inner = base64.b64decode(m.group(2).strip()).decode("utf-8")
        inner = inject_head(inner, slug)
        inner = sub1(inner, 'const AUDIO_BASE = "audio/";', 'const AUDIO_BASE = "../audio/";')
        enc = base64.b64encode(inner.encode("utf-8")).decode("ascii")
        s = s[: m.start(2)] + enc + s[m.end(2):]

    s = inject_head(s, slug)
    s = sub1(s, 'return "audio/"+key;', 'return "../audio/"+key;')
    s = re.sub(r"<title>[^<]*</title>",
               '<title>%s的英语日课</title>\n<meta name="apple-mobile-web-app-title" content="%s">' % (name, short),
               s, count=1)
    s = sub1(s, '<header>\n  <nav class="tabs"',
             '<header>\n  <div class="who">%s</div>\n  <nav class="tabs"' % name)
    s = sub1(s, "</style>",
             ".who{flex:none;font-size:20px;font-weight:800;color:var(--ink,#222);"
             "padding:6px 14px;border-radius:999px;background:rgba(0,0,0,.05);letter-spacing:1px}\n</style>")
    s = sub1(s, '<div class="greet"><h1>${date}</h1>',
             '<div class="greet"><h1>%s，${date}</h1>' % name)
    return s


CHOOSER = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>英语日课</title>
<style>
body{margin:0;min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;
font-family:-apple-system,"PingFang SC",sans-serif;background:#faf7f0;color:#222}
h1{font-size:28px;margin:0 0 32px}
a{display:block;width:280px;margin:10px;padding:26px 0;text-align:center;font-size:30px;font-weight:700;
text-decoration:none;color:#222;background:#fff;border:2px solid #e4ddcc;border-radius:22px}
</style></head><body>
<h1>英语日课</h1>
<a href="xinyuan/">秦心远</a>
<a href="youran/">秦悠然</a>
</body></html>
"""


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src_dir = sys.argv[1]
    repo = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = open(os.path.join(src_dir, "index.html"), encoding="utf-8").read()
    for slug, name, short in KIDS:
        d = os.path.join(repo, slug)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(build_kid(src, slug, name, short))
    a_src, a_dst = os.path.join(src_dir, "audio"), os.path.join(repo, "audio")
    if os.path.isdir(a_src):
        shutil.rmtree(a_dst, ignore_errors=True)
        shutil.copytree(a_src, a_dst)
    open(os.path.join(repo, "index.html"), "w", encoding="utf-8").write(CHOOSER)
    open(os.path.join(repo, ".nojekyll"), "w").write("")
    print("built:", ", ".join(k[0] for k in KIDS), "->", repo)


if __name__ == "__main__":
    main()
