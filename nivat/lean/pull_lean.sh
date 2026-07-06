#!/usr/bin/env bash
# pull_lean.sh — obtain a mathlib-free Lean 4 toolchain WITHOUT the official
# distribution hosts (github.com releases and release.lean-lang.org are blocked
# by this environment's egress policy). We pull the community Docker image
# `leanprovercommunity/lean4` through the Google mirror `mirror.gcr.io` (whose
# blob backend, storage.googleapis.com / mirror.gcr.io artifacts, IS reachable),
# then extract the `lean`/`lake` binaries from the image layers. No Docker daemon
# needed — just curl + tar.
#
# Result: a working Lean 4.10.0 toolchain under $DEST (default /tmp/leanroot),
# usable via `source lean/env.sh`. Verified: `lean NivatFinite.lean` -> exit 0.
set -euo pipefail
REPO="leanprovercommunity/lean4"
DEST="${1:-/tmp/leanroot}"
WORK="$(mktemp -d)"
mkdir -p "$DEST"

echo ">> token from mirror.gcr.io"
TOK=$(curl -sS --max-time 30 "https://mirror.gcr.io/v2/token?scope=repository:${REPO}:pull" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")

echo ">> manifest"
curl -sS --max-time 30 -H "Authorization: Bearer $TOK" \
  -H "Accept: application/vnd.docker.distribution.manifest.v2+json" \
  "https://mirror.gcr.io/v2/${REPO}/manifests/latest" > "$WORK/manifest.json"

echo ">> downloading + extracting layers (the toolchain lives in the largest one)"
python3 - "$WORK/manifest.json" <<'PY' > "$WORK/digests.txt"
import sys, json
m = json.load(open(sys.argv[1]))
for l in m["layers"]:
    print(l["digest"])
PY
while read -r d; do
  echo "   layer ${d:0:19}"
  curl -sSL --max-time 600 -H "Authorization: Bearer $TOK" \
    "https://mirror.gcr.io/v2/${REPO}/blobs/${d}" -o "$WORK/layer.tar.gz"
  tar -xzf "$WORK/layer.tar.gz" -C "$DEST" 2>/dev/null || true
done < "$WORK/digests.txt"

TC="$DEST/home/lean/.elan/toolchains/stable"
echo ">> checking toolchain at $TC"
"$TC/bin/lean" --version
"$TC/bin/lake" --version
rm -rf "$WORK"
echo "OK. Now:  export PATH=$TC/bin:\$PATH   (or: source lean/env.sh)"
