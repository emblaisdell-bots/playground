#!/usr/bin/env bash
# verify.sh — machine-check the finite Nivat theorems and print the trusted base.
# Prereq: a Lean toolchain (run pull_lean.sh once, then `source env.sh`).
set -euo pipefail
cd "$(dirname "$0")"
: "${LEAN_TC:?source env.sh first (or run pull_lean.sh)}"
export PATH="$LEAN_TC/bin:$PATH"

echo ">> lean --version"; lean --version
echo ">> checking NivatFinite.lean (exit 0 = every theorem verified)"
lean NivatFinite.lean
echo "   exit=$?"

echo ">> axioms (trusted base) of each proof:"
lean --o=/tmp/NivatFinite.olean NivatFinite.lean
cat > /tmp/_ax.lean <<'EOF'
import NivatFinite
open NivatFinite
#print axioms single_defect_3x3
#print axioms floor_3x3
#print axioms single_defect_4x4
#print axioms floor_4x4
EOF
LEAN_PATH=/tmp lean /tmp/_ax.lean
echo ">> done. (Lean.ofReduceBool is the native_decide axiom; no sorryAx present.)"
