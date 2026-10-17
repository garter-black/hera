// hera - the pbi-edge Worker transform, verbatim.
//
// Source of truth for these constants:
//   work/witchcraft-identity-lock-20261013/candidates/pbi-edge/worker.js
// which is the deployed source of Worker `pbi-edge`.
//
// This hostname is routed by `pbi-edge` (route pattern "hera.garter.app/*",
// proven by the live `x-pbi-edge: 1` response header), so the brand hostname is
// NOT the Pages document - it is the Pages document after this transform.
//
// host: hera-3zo.pages.dev
// agent: AGENTS["hera.garter.app"] - this host HAS its own agent in the Worker, so the
// live widget names agent_1901kzp4j332fg8a31tssz296c5n, NOT NETWORK_DEFAULT.
// A page naming NETWORK_DEFAULT would have proved no AGENTS entry matched; here one does.

export const PLAYER_TAG = "<script src=\"/_pbi/player.js\" defer></script>";

export const LAYOUT = "<style>elevenlabs-convai{right:16px!important;bottom:24px!important}@media(max-width:640px){elevenlabs-convai{right:10px!important;bottom:76px!important}}</style>";

// convaiTag() from worker.js
export const CONVAI_STYLE = "<style>elevenlabs-convai{position:fixed;right:16px;bottom:24px;z-index:2147482000}@media(max-width:640px){elevenlabs-convai{bottom:76px;right:10px}}</style>";

export const AGENT = {"id": "agent_1901kzp4j332fg8a31tssz296c5n", "c1": "#d8c49a", "c2": "#0a0a0a"};

export const NETWORK_DEFAULT = {"id": "agent_7601kv76b5cgfq9thvb5mxsdqsw0", "c1": "#c9c5bb", "c2": "#0a0a0a"};

export function convaiTag(a) {
  return (
    CONVAI_STYLE +
    '<elevenlabs-convai agent-id="' + a.id +
    '" avatar-orb-color-1="' + a.c1 + '" avatar-orb-color-2="' + a.c2 +
    '"></elevenlabs-convai>' +
    '<script src="https://unpkg.com/@elevenlabs/convai-widget-embed" async type="text/javascript"></script>'
  );
}

// BodyInjector fires on the END tag: the payload lands FLUSH against </body>.
export function transform(html) {
  let out = html;
  if (!out.includes("/_pbi/player.js")) {
    out = out.replace("</head>", PLAYER_TAG + "</head>");
  }
  out = out.replace("</body>", LAYOUT + convaiTag(AGENT) + "</body>");
  return out;
}

// footerBlock is "" for this host: it appears in neither SPONSORS nor SPONSORS2,
// which is why the injected delta is a flat 608 B constant.
export const FOOTER_BLOCK = "";
