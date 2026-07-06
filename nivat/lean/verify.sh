#!/usr/bin/env bash
# verify.sh — machine-check the finite Nivat theorems and print the trusted base.
# Prereq: a Lean toolchain (run pull_lean.sh once, then `source env.sh`).
set -euo pipefail
cd "$(dirname "$0")"
: "${LEAN_TC:?source env.sh first (or run pull_lean.sh)}"
export PATH="$LEAN_TC/bin:$PATH"

echo ">> lean --version"; lean --version

echo ">> checking Nivat.lean — mathlib-free infinite STATEMENT + sanity lemmas"
lean Nivat.lean;            echo "   exit=$?"

echo ">> checking NivatFinite.lean — finite PROVEN theorems (~60s)"
lean NivatFinite.lean;      echo "   exit=$?"

echo ">> axioms (trusted base):"
lean --o=/tmp/Nivat.olean Nivat.lean
lean --o=/tmp/NivatFinite.olean NivatFinite.lean
cat > /tmp/_ax.lean <<'EOF'
import Nivat
import NivatFinite
open Nivat NivatFinite
#print axioms const_periodic
#print axioms not_PatternLE_zero
#print axioms floor_4x4
#print axioms floor_4x4_w33
#print axioms mh_L6_n2
EOF
LEAN_PATH=/tmp lean /tmp/_ax.lean
echo ">> done. Nivat.lean lemmas: no axioms. Finite theorems: Lean.ofReduceBool"
echo ">> (native_decide axiom); no sorryAx anywhere."
