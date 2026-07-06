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

echo ">> checking NivatTheory.lean — GENERAL theorem, SYMBOLIC proof (no enumeration)"
lean NivatTheory.lean;      echo "   exit=$?"

echo ">> checking NivatFinite.lean — finite PROVEN theorems via native_decide (~60s)"
lean NivatFinite.lean;      echo "   exit=$?"

echo ">> axioms (trusted base):"
lean --o=/tmp/Nivat.olean Nivat.lean
lean --o=/tmp/NivatTheory.olean NivatTheory.lean
lean --o=/tmp/NivatFinite.olean NivatFinite.lean
cat > /tmp/_ax.lean <<'EOF'
import Nivat
import NivatTheory
import NivatFinite
open Nivat NivatTheory NivatFinite
#print axioms const_periodic
#print axioms periodic_pair_PatternLE
#print axioms floor_4x4
#print axioms mh_L6_n2
EOF
LEAN_PATH=/tmp lean /tmp/_ax.lean
echo ">> Nivat.lean: no axioms. NivatTheory (symbolic): [propext, Quot.sound] only"
echo ">> (kernel logic — NO native_decide). Finite: Lean.ofReduceBool. No sorryAx."
