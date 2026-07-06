"""torus_search.py — exhaustive finite probe of the Nivat threshold.

For each torus Z_N x Z_M over an alphabet of size `a`, we enumerate EVERY
configuration, split them into `primitive` (no nonzero period vector; the
finite surrogate for "aperiodic up to scale (N,M)") and `periodic`, and for
each window (m,n) we record

    gap(m,n) = min over PRIMITIVE configs of ( P(m,n) - m*n ).

Interpretation.  On a finite torus every configuration is (trivially) periodic
as an infinite object, so a torus can never *refute* Nivat.  What it can do is
reveal the finite/uniform relationship the conjecture is really about: how much
block complexity a configuration must spend to remain primitive at scale (N,M).
A positive gap for every window smaller than the torus is the finite shadow of
"aperiodic => P(m,n) >= m*n + 1".  A zero or negative gap would be a genuinely
interesting finite phenomenon (a primitive torus config meeting the mn bound),
worth isolating and studying — NOT a Nivat counterexample, but data about the
gap between the finite and infinite statements.

Everything printed is [EXPERIMENTAL]: it is exactly what the enumeration found.
"""
from __future__ import annotations
import json
import sys
import os
from nivat_core import P, is_primitive, all_configs

OUT = os.path.join(os.path.dirname(__file__), "out")


def run(N, M, a, windows=None):
    if windows is None:
        windows = [(m, n) for m in range(1, N + 1) for n in range(1, M + 1)]
    # gap[(m,n)] = (min P-mn over primitive, witness config, its P)
    gap = {}
    n_prim = 0
    n_tot = 0
    # also track: among ALL configs, min P(m,n) with primitivity flag
    for x in all_configs(N, M, a):
        n_tot += 1
        prim = is_primitive(x)
        if not prim:
            continue
        n_prim += 1
        for (m, n) in windows:
            pv = P(x, m, n)
            g = pv - m * n
            cur = gap.get((m, n))
            if cur is None or g < cur[0]:
                gap[(m, n)] = (g, [row[:] for row in x], pv)
    res = {
        "N": N, "M": M, "a": a,
        "n_total": n_tot, "n_primitive": n_prim,
        "windows": {},
    }
    for (m, n), (g, wit, pv) in sorted(gap.items()):
        res["windows"]["%dx%d" % (m, n)] = {
            "m": m, "n": n, "mn": m * n,
            "min_P_over_primitive": pv,
            "gap_min_P_minus_mn": g,
            "meets_or_beats_mn_bound": g <= 0,
            "witness": wit,
        }
    return res


def main():
    # sizes chosen to stay exhaustively enumerable in pure Python:
    #   binary: up to ~2^20 configs.  ternary/larger: tiny tori only.
    # sizes that finish exhaustively in pure Python in well under a minute each.
    # (4x5 binary = 2^20 is enumerable but slow ~10min; run it separately with
    #  `python3 torus_search.py 4 5 2` if desired. The 4x4 data already exhibits
    #  the interior gap=+1 pattern robustly.)
    jobs = [
        (3, 3, 2),
        (3, 4, 2),
        (4, 4, 2),   # 2^16 = 65,536
        (3, 5, 2),   # 2^15 = 32,768
        (3, 3, 3),   # 3^9 = 19,683
        (2, 2, 4),
    ]
    if len(sys.argv) > 1:  # optional: python3 torus_search.py 4 5 2
        jobs = [tuple(int(t) for t in sys.argv[1:4])]
    os.makedirs(OUT, exist_ok=True)
    allres = []
    for (N, M, a) in jobs:
        sys.stderr.write("running N=%d M=%d a=%d ...\n" % (N, M, a))
        sys.stderr.flush()
        r = run(N, M, a)
        allres.append(r)
        # human summary
        print("=" * 64)
        print("Torus Z_%d x Z_%d, alphabet size %d" % (N, M, a))
        print("  configs total=%d  primitive=%d" % (r["n_total"], r["n_primitive"]))
        print("  window |  mn | minP(prim) | gap=minP-mn | meets mn?")
        for key, w in r["windows"].items():
            flag = "  <-- MEETS/BEATS mn" if w["meets_or_beats_mn_bound"] else ""
            print("   %5s | %3d | %10d | %+11d |%s" %
                  (key, w["mn"], w["min_P_over_primitive"],
                   w["gap_min_P_minus_mn"], flag))
    with open(os.path.join(OUT, "torus_search.json"), "w") as f:
        json.dump(allres, f, indent=1)
    print("\nsaved -> out/torus_search.json")


if __name__ == "__main__":
    main()
