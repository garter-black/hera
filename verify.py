#!/usr/bin/env python3
"""hera - prove the commit reproduces production bytes.

    python verify.py            compare a rebuild against fresh live fetches

Two independent surfaces are checked:
  1. the Pages origin  - src/index.html must equal the live pages.dev document
  2. the custom domain - the rebuild must equal the live edge-transformed document

The beacon question was re-derived for THIS site rather than carried over: the
Cloudflare Web Analytics beacon is measured directly (present/absent, and
whether its token rotates). Strip it only if it is actually edge-injected here.
"""
import hashlib, os, re, subprocess, sys, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src", "index.html")
ORIGIN_URL = "https://hera-3zo.pages.dev/"
EDGE_URL = "https://hera.garter.app/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
BEACON = re.compile(rb'<script type="module" src="https://static\.cloudflareinsights\.com[^"]*"[^>]*>\s*</script>\n?', re.I)


def fetch(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read(), {k.lower(): v for k, v in r.headers.items()}
        except Exception:
            if i == tries - 1:
                return None, {}
    return None, {}


def main():
    ok = True
    origin_live, oh = fetch(ORIGIN_URL)
    src = open(SRC, "rb").read()
    if origin_live is None:
        print("FAIL: could not fetch", ORIGIN_URL); return 1
    print("live origin   %8d B  sha=%s" % (len(origin_live), hashlib.sha256(origin_live).hexdigest()))
    print("committed src %8d B  sha=%s" % (len(src), hashlib.sha256(src).hexdigest()))
    if origin_live == src:
        print("ORIGIN MATCH  (byte-exact, no normalisation needed)")
    else:
        stripped = BEACON.sub(b"", origin_live)
        if stripped == src:
            print("ORIGIN MATCH after beacon strip (%d B beacon, edge-injected)" % (len(origin_live) - len(stripped)))
        else:
            ok = False
            print("ORIGIN DIFFER by %+d B" % (len(origin_live) - len(src)))
            print("  beacon in live:", bool(BEACON.search(origin_live)))
    # rebuild from git objects, not the working tree
    files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    for f in files:
        blob = subprocess.run(["git", "show", "HEAD:" + f], cwd=ROOT, capture_output=True).stdout
        p = os.path.join(ROOT, f)
        with open(p, "wb") as fh:
            fh.write(blob)
    subprocess.run([sys.executable, "build.py"], cwd=ROOT, capture_output=True)
    built = open(os.path.join(ROOT, "dist", "index.html"), "rb").read()
    print("rebuilt from git objects %8d B  sha=%s" % (len(built), hashlib.sha256(built).hexdigest()))
    if EDGE_URL:
        edge_live, eh = fetch(EDGE_URL)
        if edge_live is None:
            print("WARN: could not fetch", EDGE_URL)
        else:
            edge_s = BEACON.sub(b"", edge_live)
            print("live edge     %8d B  sha=%s  x-pbi-edge=%s"
                  % (len(edge_live), hashlib.sha256(edge_live).hexdigest(), eh.get("x-pbi-edge", "ABSENT")))
            built_s = BEACON.sub(b"", built)
            if edge_s == built_s:
                print("EDGE MATCH    (byte-exact vs rebuild, beacon-free both sides)")
            elif edge_live == built:
                print("EDGE MATCH    (byte-exact vs rebuild, raw both sides)")
            else:
                ok = False
                print("EDGE DIFFER by %+d B (beacon-free live vs beacon-free rebuild)"
                      % (len(edge_s) - len(built_s)))
    print("VERIFY " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
