# Source this to use the Lean toolchain extracted from the leanprovercommunity/lean4
# Docker image (pulled via mirror.gcr.io; github.com/release.lean-lang.org are
# egress-blocked). Lean 4.10.0, mathlib-free. Toolchain lives in scratch and is
# NOT committed (binaries). Re-run lean/pull_lean.sh in a fresh container.
export LEAN_TC=/tmp/leanroot/home/lean/.elan/toolchains/stable
export PATH="$LEAN_TC/bin:$PATH"
