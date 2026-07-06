"""sat_nd.py — z3 existence of primitive low-complexity configs in any dimension.

Generalizes sat_search.py to d dimensions with a leaner binary encoding (Bool
cells for a=2), so we can (a) push the 2D non-existence sweep to larger tori and
(b) test the DIMENSIONAL analogue: is a primitive torus config with box
complexity P(window) <= prod(window) possible in 3D, where 2D forbids it?

Complexity in d-D: a "box" of shape `w` (a d-tuple) has prod(w) cells; P(w) is
the number of distinct boxes occurring (torus wrap).  "primitive" = no nonzero
period vector v in the torus group.  Encoding mirrors sat_search.py:
  * <= K distinct boxes: every box equals one of K template boxes;
  * primitive: for each nonzero v, some cell differs under the v-shift.
Every SAT witness is re-verified by a direct pure-Python recount before report,
so no claim rests on z3 alone.

Usage:
  python3 sat_nd.py 2 6 6 2 2 4      # dim=2, shape torus 6x6, window 2x2, K=4
  python3 sat_nd.py 3 4 4 4 2 2 2 8  # dim=3, torus 4x4x4, window 2x2x2, K=8
  python3 sat_nd.py                  # default battery (2D sweep + 3D gap)
"""
from __future__ import annotations
import sys
import itertools
import z3


def offsets(window):
    return list(itertools.product(*[range(w) for w in window]))


def coords(shape):
    return list(itertools.product(*[range(s) for s in shape]))


def nonzero_vectors(shape):
    for v in coords(shape):
        if any(c != 0 for c in v):
            yield v


def add(p, v, shape):
    return tuple((p[i] + v[i]) % shape[i] for i in range(len(shape)))


# ---- pure-Python recount for independent verification -----------------------

def recount_P(cfg, shape, window):
    offs = offsets(window)
    boxes = set()
    for p in coords(shape):
        boxes.add(tuple(cfg[add(p, o, shape)] for o in offs))
    return len(boxes)


def recount_primitive(cfg, shape):
    for v in nonzero_vectors(shape):
        if all(cfg[p] == cfg[add(p, v, shape)] for p in coords(shape)):
            return False
    return True


# ---- z3 model ---------------------------------------------------------------

def solve(shape, window, K, a=2, timeout_ms=60000):
    s = z3.Solver()
    s.set("timeout", timeout_ms)
    C = coords(shape)
    offs = offsets(window)
    if a == 2:
        x = {p: z3.Bool("x_%s" % "_".join(map(str, p))) for p in C}
        def cell(p): return x[p]
        def eq(u, w): return u == w
        T = [[z3.Bool("t_%d_%d" % (k, o)) for o in range(len(offs))]
             for k in range(K)]
    else:
        x = {p: z3.Int("x_%s" % "_".join(map(str, p))) for p in C}
        for p in C:
            s.add(x[p] >= 0, x[p] < a)
        def cell(p): return x[p]
        def eq(u, w): return u == w
        T = [[z3.Int("t_%d_%d" % (k, o)) for o in range(len(offs))]
             for k in range(K)]
        for k in range(K):
            for o in range(len(offs)):
                s.add(T[k][o] >= 0, T[k][o] < a)
    # every box matches some template
    for p in C:
        box = [cell(add(p, o, shape)) for o in offs]
        s.add(z3.Or([z3.And([eq(box[o], T[k][o]) for o in range(len(offs))])
                     for k in range(K)]))
    # primitive
    for v in nonzero_vectors(shape):
        s.add(z3.Or([z3.Not(eq(cell(p), cell(add(p, v, shape)))) for p in C]))
    r = s.check()
    if r == z3.sat:
        mdl = s.model()
        if a == 2:
            cfg = {p: (1 if z3.is_true(mdl.eval(x[p], model_completion=True))
                       else 0) for p in C}
        else:
            cfg = {p: mdl.eval(x[p], model_completion=True).as_long() for p in C}
        assert recount_primitive(cfg, shape), "z3 model not primitive on recount!"
        pv = recount_P(cfg, shape, window)
        assert pv <= K, "z3 model P=%d exceeds K=%d on recount!" % (pv, K)
        return "SAT", cfg, pv
    return ("UNSAT" if r == z3.unsat else "UNKNOWN"), None, None


def fmt_cfg(cfg, shape):
    if len(shape) == 2:
        N, M = shape
        return "\n".join("      " + "".join(str(cfg[(i, j)]) for j in range(M))
                         for i in range(N))
    # 3D: print slices
    A, B, Cc = shape
    out = []
    for i in range(A):
        out.append("      slice i=%d:" % i)
        for j in range(B):
            out.append("        " + "".join(str(cfg[(i, j, k)]) for k in range(Cc)))
    return "\n".join(out)


def main():
    if len(sys.argv) > 1:
        dim = int(sys.argv[1])
        rest = list(map(int, sys.argv[2:]))
        shape = tuple(rest[:dim])
        window = tuple(rest[dim:2 * dim])
        K = rest[2 * dim]
        verdict, cfg, pv = solve(shape, window, K)
        print("shape=%s window=%s K=%d (prod=%d) -> %s"
              % (shape, window, K, __import__("math").prod(window), verdict))
        if verdict == "SAT":
            print(fmt_cfg(cfg, shape))
        return

    print("### 2D uniformity sweep: primitive with P(2,2) <= 4 (=mn) ?")
    print("### (UNSAT at every size = strong evidence the mn+1 floor is uniform in N)")
    for N in [9, 10, 11, 12, 14]:
        verdict, cfg, pv = solve((N, N), (2, 2), 4, a=2, timeout_ms=90000)
        print("  Z_%dxZ_%d  P(2,2)<=4 : %s" % (N, N, verdict))
        sys.stdout.flush()

    print("\n### Dimensional gap (planarity necessity):")
    print("### 2D: primitive with P(2,2) <= 4 ?   vs   3D: primitive with P(2,2,2) <= 8 ?")
    v2, _, _ = solve((5, 5), (2, 2), 4, a=2, timeout_ms=60000)
    print("  2D Z_5xZ_5     P(2,2)  <= 4  : %s" % v2)
    for shp in [(3, 3, 3), (4, 4, 4), (4, 4, 2), (5, 5, 2)]:
        v3, cfg3, pv3 = solve(shp, (2, 2, 2), 8, a=2, timeout_ms=120000)
        print("  3D Z_%dxZ_%dxZ_%d P(2,2,2)<= 8  : %s" % (shp + (v3,)))
        if v3 == "SAT":
            print("    primitive 3D witness with P(2,2,2)=%d (re-verified):" % pv3)
            print(fmt_cfg(cfg3, shp))
        sys.stdout.flush()


if __name__ == "__main__":
    main()
