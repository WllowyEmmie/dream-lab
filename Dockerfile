# dream-lab: Pi with the same versions as the Windows setup (13 Nov 2026).
# Build:  docker build -t dream-lab-pi .
# Run:    see README section at the bottom of this file.

# Node: the version Pi's own runtime uses on Windows (AppData/Local/pi-node).
FROM node:22.23.5-bookworm-slim

# Versions from the Windows install.
ARG PI_VERSION=1.5.2
ARG CLAUDE_BRIDGE_VERSION=0.12.0
ARG SUBAGENTS_VERSION=25.0.5
ARG CLAUDE_USAGE_VERSION=0.2.5
ARG PI_CLAUDE_CODE_COMMIT=d5b5e04c314d3452d357174d16d10dda34daa2d2
ARG RG_VERSION=15.2.0
ARG FD_VERSION=10.5.2

RUN apt-get update \
  && apt-get install -y --no-install-recommends bash ca-certificates curl git \
  && rm -rf /var/lib/apt/lists/*

# ripgrep and fd from their GitHub releases, so the versions match exactly.
RUN curl -fsSL "https://github.com/BurntSushi/ripgrep/releases/download/${RG_VERSION}/ripgrep-${RG_VERSION}-x86_64-unknown-linux-musl.tar.gz" \
    | tar -xz -C /tmp \
  && mv "/tmp/ripgrep-${RG_VERSION}-x86_64-unknown-linux-musl/rg" /usr/local/bin/rg \
  && curl -fsSL "https://github.com/sharkdp/fd/releases/download/v${FD_VERSION}/fd-v${FD_VERSION}-x86_64-unknown-linux-musl.tar.gz" \
    | tar -xz -C /tmp \
  && mv "/tmp/fd-v${FD_VERSION}-x86_64-unknown-linux-musl/fd" /usr/local/bin/fd \
  && rm -rf /tmp/ripgrep-* /tmp/fd-*

RUN npm install -g --ignore-scripts "@earendil-works/pi-coding-agent@${PI_VERSION}"

# Pi extensions, pinned (an exact version or commit is never auto-updated).
RUN pi install "npm:pi-claude-bridge@${CLAUDE_BRIDGE_VERSION}" \
  && pi install "npm:@gotgenes/pi-subagents@${SUBAGENTS_VERSION}" \
  && pi install "npm:@llblab/pi-claude-usage@${CLAUDE_USAGE_VERSION}" \
  && pi install "git:github.com/earendil-works/pi-claude-code@${PI_CLAUDE_CODE_COMMIT}"
# pi-coding-agent-eval isn't installed on Windows yet; add it here at step 19.

# Same default model as on Windows.
RUN node -e '\
  const f=require("os").homedir()+"/.pi/agent/settings.json"; \
  const s=JSON.parse(require("fs").readFileSync(f,"utf8")); \
  s.defaultProvider="claude-bridge"; s.defaultModel="claude-opus-5-5"; \
  require("fs").writeFileSync(f, JSON.stringify(s,null,2));'

# The repo is mounted from Windows, so its owner differs; let git use it anyway.
RUN git config --system safe.directory /workspace

WORKDIR /workspace
ENTRYPOINT ["pi"]

# ---- Running it ----
# From the dream-lab folder (PowerShell):
#   docker run --rm -it `
#     -e CLAUDE_CODE_OAUTH_TOKEN `
#     -v "${PWD}:/workspace" `
#     -v dream-lab-sessions:/root/.pi/agent/sessions `
#     dream-lab-pi
# Dreaming pass:  add  --entrypoint bash  and put  ./dream.sh  at the end.
# CLAUDE_CODE_OAUTH_TOKEN: create it with `claude setup-token`, then set it in the
# shell first ($env:CLAUDE_CODE_OAUTH_TOKEN = "...").
# Only sessions are kept in a volume; mounting all of ~/.pi/agent would hide the
# extensions installed above.
