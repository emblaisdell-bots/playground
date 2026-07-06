#!/usr/bin/env bash
# setup.sh — bring up the Lean + mathlib project for the Nivat formalization.
#
# UNTESTED in the environment where it was written: the Lean toolchain hosts were
# egress-blocked (github releases + release.lean-lang.org -> 403). Run this in an
# environment where those hosts are ALLOWLISTED. It is intentionally verbose and
# fails loudly.
#
# Hosts that must be reachable: github.com, objects.githubusercontent.com,
# raw.githubusercontent.com, release.lean-lang.org (and the mathlib build cache
# on Azure/github). If any 403s, the environment's network policy still blocks it.
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v elan >/dev/null 2>&1; then
  echo ">> installing elan (Lean version manager)"
  curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh \
    -o /tmp/elan-init.sh
  sh /tmp/elan-init.sh -y
  # shellcheck disable=SC1090
  source "$HOME/.elan/env"
fi
export PATH="$HOME/.elan/bin:$PATH"

echo ">> toolchain: $(cat lean-toolchain)"
elan toolchain install "$(cat lean-toolchain | cut -d: -f2)" || true

echo ">> lake update (fetch mathlib; may take a while)"
lake update

echo ">> lake exe cache get (download prebuilt mathlib oleans; avoids hours of build)"
lake exe cache get || echo "WARN: cache miss; 'lake build' will compile mathlib from source"

echo ">> building Nivat.lean"
lake build Nivat

echo
echo "If 'lake build' fails with a toolchain mismatch, set lean-toolchain to the"
echo "value in .lake/packages/mathlib/lean-toolchain and re-run 'lake update && lake build'."
echo "OK: Lean project built. Nivat.lean now compiles under a real verifier."
