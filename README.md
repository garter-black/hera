# hera - estate source of truth

Project: `hera`
Pages project: `hera-3zo.pages.dev`
Custom domain(s): hera.garter.app

Source of truth for the page is `src/index.html`. It is byte-identical to the
live Pages origin, verified against a fresh fetch (see `verify.py`).

`dist/index.html` is the output a request to a pbi-edge-routed custom domain
receives after the Worker transform. It is a build artifact and is git-ignored.

## Layout

| Path | What it is |
|---|---|
| `src/index.html` | the origin document, byte-identical to live |
| `edge/pbi-edge-transform.mjs` | the Worker's transform constants, verbatim from the deployed `pbi-edge` source |
| `build.py` | `src/index.html` -> `dist/index.html` |
| `verify.py` | refetches live and compares against a rebuild from git objects |

## Provenance

Winner: `websites-legacy/hera-deploy/` - a two-route Pages project, byte-identical to live:
  `/`            35,569 B  sha fcddb3c6...  (committed as src/index.html)
  `/whitepaper`   4,493 B  sha 854ce755...  (committed as src/whitepaper/index.html)
Both routes were verified against fresh live fetches, not the working tree.

Runner-up, rejected on criterion 4: `sites/hera-garter-live/index.html` (37,157 B). It is a
superset by 7 visible text blocks, and every one of those extra blocks is a footer carrying
2 `<a href>` links and 1 `mailto:` to a forbidden house domain, plus a second entity (Seven Stars
Properties Pty Ltd ABN 87 902 523 599) that the live origin does not carry. The superset rule
says the superset wins UNLESS the extra content is itself a defect; here it is. The exact
strings and their byte offsets are in the decision record, which is deliberately kept
outside this repo so no tracked file carries the forbidden domain as a resolvable link.

`hera.garter.app` is served by Worker `pbi-edge`, which is why the brand hostname is 608 B
larger than the Pages origin. That layer is reproduced here.

## Standing limits

This lane is **read-only against Cloudflare**. It never deploys, never changes
DNS and never edits a Worker. `build.py` exists so the committed source is
provable; publishing it is a separate, reviewed transaction.

Deploying `src/index.html` to a custom domain without the edge layer would
**remove the voice agent**. See `README` note in the lane skill.
