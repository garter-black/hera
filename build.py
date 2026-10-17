#!/usr/bin/env python3
"""hera - rebuild the pbi-edge output from committed source.

    python build.py            src/index.html -> dist/index.html
    python build.py --verify   build, then print SHA-256 and byte count

src/index.html is the source of truth and is byte-identical to the live Pages
origin. dist/ is what a request to a pbi-edge-routed custom domain receives
after the Worker transform. dist/ is a build artifact and is git-ignored.

Constants below are verbatim from the deployed pbi-edge worker source
(work/witchcraft-identity-lock-20261013/candidates/pbi-edge/worker.js). They are
copied, not re-derived from live bytes, so the builder and the verifier do not
encode the same assumption.

Read-only against Cloudflare: this never deploys and never changes DNS.
"""
import hashlib, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src", "index.html")
DIST = os.path.join(ROOT, "dist")
OUT = os.path.join(DIST, "index.html")

# --- verbatim from pbi-edge worker.js ---
PLAYER_TAG = '<script src="/_pbi/player.js" defer></script>'
LAYOUT = ('<style>elevenlabs-convai{right:16px!important;bottom:24px!important}'
          '@media(max-width:640px){elevenlabs-convai{right:10px!important;bottom:76px!important}</style>')
CONVAI_STYLE = ('<style>elevenlabs-convai{position:fixed;right:16px;bottom:24px;z-index:2147482000}'
                '@media(max-width:640px){elevenlabs-convai{bottom:76px;right:10px}</style>')
AGENT = ('agent_1901kzp4j332fg8a31tssz296c5n', '#d8c49a', '#0a0a0a')


def convai_tag(a):
    aid, c1, c2 = a
    return (CONVAI_STYLE
            + '<elevenlabs-convai agent-id="' + aid
            + '" avatar-orb-color-1="' + c1 + '" avatar-orb-color-2="' + c2
            + '"></elevenlabs-convai>'
            + '<script src="https://unpkg.com/@elevenlabs/convai-widget-embed" async type="text/javascript"></script>')


def transform(html):
    """Reproduce the pbi-edge BodyInjector/HeadInjector output.

    HTMLRewriter's append() fires on the END tag, so the payload lands flush
    against </body> - there is NO newline between the payload and </body>.
    Measured on 2 sites in this batch and 6 in run33; see the decision record.
    """
    out = html
    if "/_pbi/player.js" not in out:
        out = re.sub(r"</head\s*>", PLAYER_TAG + "</head>", out, count=1, flags=re.I)
    out = re.sub(r"</body\s*>", LAYOUT + convai_tag(AGENT) + "</body>", out, count=1, flags=re.I)
    return out


def main():
    origin = open(SRC, "rb").read().decode("utf-8")
    built = transform(origin).encode("utf-8")
    os.makedirs(DIST, exist_ok=True)
    # newline="" - Windows must not convert LF to CRLF in bytes that matter.
    with open(OUT, "wb") as f:
        f.write(built)
    print("origin  %8d B  sha=%s" % (len(origin.encode("utf-8")), hashlib.sha256(origin.encode("utf-8")).hexdigest()))
    print("built   %8d B  sha=%s" % (len(built), hashlib.sha256(built).hexdigest()))
    print("delta   %+8d B" % (len(built) - len(origin.encode("utf-8"))))
    if "--verify" in sys.argv:
        print("VERIFY: wrote", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
