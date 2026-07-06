"""extremal.py — structure of the minimal-complexity aperiodic configurations.

E2 found that on a torus the minimum block complexity of a PRIMITIVE (totally
aperiodic at scale) configuration, over windows strictly interior to the torus,
is exactly mn+1.  This script isolates the EXTREMAL configs — those primitive
configs that actually attain P(m,n) = mn+1 for a given interior window — and
asks what they look like.

For the 2x2 window we enumerate every binary torus up to a size bound, collect
all primitive configs with P(2,2)=5 (=mn+1), and classify each by:
  * number of minority cells (cells differing from the majority symbol),
  * whether the "defect set" (minority cells) lies on a single line
    (a row, a column, or a diagonal) — the periodic-fault picture,
  * the multiset of 2x2 patterns used.

Everything printed is [EXPERIMENTAL].  No claim about the infinite conjecture is
made; this is descriptive structure of the finite extremals.
"""
from __future__ import annotations
import json
import os
from collections import Counter
from nivat_core import P, is_primitive, all_configs

OUT = os.path.join(os.path.dirname(__file__), "out")


def minority_cells(x):
    N, M = len(x), len(x[0])
    ones = sum(r.count(1) for r in x)
    total = N * M
    minsym = 1 if ones * 2 <= total else 0
    return [(i, j) for i in range(N) for j in range(M) if x[i][j] == minsym], minsym


def on_single_line(cells, N, M):
    """Do all cells share a row, a column, or a (wrapping) diagonal/anti-diag?"""
    if len(cells) <= 1:
        return "trivial(<=1 cell)"
    rows = {i for i, _ in cells}
    cols = {j for _, j in cells}
    if len(rows) == 1:
        return "single-row"
    if len(cols) == 1:
        return "single-column"
    # diagonal: j - i constant (mod something) ; anti: i + j constant
    diffs = {(j - i) % M for i, j in cells} if N == M else set()
    sums = {(i + j) % M for i, j in cells} if N == M else set()
    if N == M and len(diffs) == 1:
        return "single-diagonal"
    if N == M and len(sums) == 1:
        return "single-antidiagonal"
    return "not-a-line"


def study(N, M, m=2, n=2):
    target = m * n + 1
    extremals = []
    for x in all_configs(N, M, 2):
        if not is_primitive(x):
            continue
        if P(x, m, n) != target:
            continue
        cells, minsym = minority_cells(x)
        extremals.append((x, cells, minsym))
    # classify
    kinds = Counter()
    minority_sizes = Counter()
    examples = {}
    for x, cells, minsym in extremals:
        kind = on_single_line(cells, N, M)
        kinds[kind] += 1
        minority_sizes[len(cells)] += 1
        examples.setdefault(kind, x)
    return {
        "N": N, "M": M, "window": "%dx%d" % (m, n), "target_P": target,
        "num_extremal_primitive": len(extremals),
        "defect_shape_counts": dict(kinds),
        "minority_size_counts": dict(minority_sizes),
        "example_per_shape": examples,
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    results = []
    for (N, M) in [(3, 3), (3, 4), (4, 4), (3, 5), (4, 5)]:
        r = study(N, M, 2, 2)
        results.append(r)
        print("=" * 60)
        print("Z_%d x Z_%d, window 2x2, extremal primitive P=%d"
              % (N, M, r["target_P"]))
        print("  # extremal primitive configs:", r["num_extremal_primitive"])
        print("  defect-set shape:", r["defect_shape_counts"])
        print("  #minority cells:", r["minority_size_counts"])
        for shape, ex in r["example_per_shape"].items():
            print("   example [%s]:" % shape,
                  "/".join("".join(map(str, row)) for row in ex))
    with open(os.path.join(OUT, "extremal.json"), "w") as f:
        json.dump(results, f, indent=1)
    print("\nsaved -> out/extremal.json")


if __name__ == "__main__":
    main()
