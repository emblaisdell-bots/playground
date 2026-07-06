"""sat_search.py — SAT/SMT existence probe with z3.

Brute force dies past ~2^20 configs.  To reach larger tori we ask z3 the
decision question directly:

    Does there EXIST a primitive configuration on Z_N x Z_M over alphabet a
    with block complexity P(m,n) <= K ?

Encoding.
  * cell vars  x[i][j] in {0..a-1}  (Int with 0<=x<a; a=2 uses Bool-as-Int).
  * "P(m,n) <= K" via K template patterns t[0..K): every window must equal one
    template.  window(i,j) == t[k] is a big AND over the m*n offsets; the
    window is forced to match at least one template (OR over k).  This encodes
    "at most K distinct windows occur", i.e. P(m,n) <= K.  (It is sound: any
    model has <= K distinct windows.  It is complete: given a config with <= K
    distinct windows, choosing the templates = the occurring windows satisfies
    it.)
  * "primitive" : for every nonzero v=(dv,dw) in Z_N x Z_M, the config is NOT
    v-periodic, i.e. OR over cells of ( x[i][j] != x[(i+dv)%N][(j+dw)%M] ).

If UNSAT: no primitive config on that torus meets P(m,n) <= K  -> the finite
"aperiodic => P > K" statement holds at that size.  If SAT: z3 returns an
explicit primitive config meeting the bound (printed and re-verified with
nivat_core, so the claim never rests on z3 alone).

Usage:
    python3 sat_search.py N M a m n K
e.g. python3 sat_search.py 6 6 2 2 3 6      # primitive, P(2,3)<=6 ?
"""
from __future__ import annotations
import sys
from itertools import product
import z3
from nivat_core import P, is_primitive


def build(N, M, a, m, n, K):
    s = z3.Solver()
    x = [[z3.Int("x_%d_%d" % (i, j)) for j in range(M)] for i in range(N)]
    for i in range(N):
        for j in range(M):
            s.add(x[i][j] >= 0, x[i][j] < a)
    # templates
    t = [[z3.Int("t_%d_%d" % (k, o)) for o in range(m * n)] for k in range(K)]
    for k in range(K):
        for o in range(m * n):
            s.add(t[k][o] >= 0, t[k][o] < a)
    # break template symmetry a little: nondecreasing first cell is unsound in
    # general, so we do NOT impose it; instead we only order-break by allowing
    # any assignment (correctness first).
    # every window equals some template
    for i in range(N):
        for j in range(M):
            win = [x[(i + di) % N][(j + dj) % M]
                   for di in range(m) for dj in range(n)]
            s.add(z3.Or([z3.And([win[o] == t[k][o] for o in range(m * n)])
                         for k in range(K)]))
    # primitive: not periodic under any nonzero v
    for dv in range(N):
        for dw in range(M):
            if dv == 0 and dw == 0:
                continue
            s.add(z3.Or([x[i][j] != x[(i + dv) % N][(j + dw) % M]
                         for i in range(N) for j in range(M)]))
    return s, x


def solve(N, M, a, m, n, K, timeout_ms=60000):
    s, x = build(N, M, a, m, n, K)
    s.set("timeout", timeout_ms)
    r = s.check()
    if r == z3.sat:
        model = s.model()
        cfg = [[model.evaluate(x[i][j]).as_long() for j in range(M)]
               for i in range(N)]
        # independent re-verification with nivat_core
        assert is_primitive(cfg), "z3 model NOT primitive under nivat_core!"
        pv = P(cfg, m, n)
        assert pv <= K, "z3 model P=%d exceeds K=%d!" % (pv, K)
        return "SAT", cfg, pv
    elif r == z3.unsat:
        return "UNSAT", None, None
    else:
        return "UNKNOWN", None, None


def main():
    if len(sys.argv) == 7:
        N, M, a, m, n, K = (int(v) for v in sys.argv[1:7])
        verdict, cfg, pv = solve(N, M, a, m, n, K)
        print("Z_%d x Z_%d a=%d  window %dx%d  K=%d (mn=%d) -> %s"
              % (N, M, a, m, n, K, m * n, verdict))
        if verdict == "SAT":
            print("  primitive witness with P(%d,%d)=%d <= %d:" % (m, n, pv, K))
            for row in cfg:
                print("   ", "".join(str(c) for c in row))
        return
    # default battery. Two complementary probes on the P(2,2) window (which z3
    # handles fast), across sizes past brute force:
    #   * K=mn=4   : expect UNSAT  (no primitive config meets the mn bound)
    #   * K=mn+1=5 : expect SAT    (z3 finds & we re-verify an extremal witness)
    # This checks BOTH directions of the sharp E2 threshold at scale.
    print("Battery on the 2x2 window (z3-fast). mn=4.")
    print("K=4 expect UNSAT (finite 'aperiodic=>P>mn'); K=5 expect SAT (sharp).")
    battery = []
    for (N, M, a) in [(5, 5, 2), (6, 6, 2), (7, 7, 2), (8, 8, 2)]:
        battery.append((N, M, a, 2, 2, 4))   # UNSAT expected
        battery.append((N, M, a, 2, 2, 5))   # SAT expected (witness re-verified)
    # one larger-window instance kept to show the solver honestly returning
    # UNKNOWN on timeout (the template encoding is hard for z3 at this size):
    battery.append((5, 5, 2, 3, 3, 9))
    for (N, M, a, m, n, K) in battery:
        verdict, cfg, pv = solve(N, M, a, m, n, K, timeout_ms=60000)
        line = "  Z_%dxZ_%d a=%d  P(%d,%d)<=%d (mn=%d) : %s" % (
            N, M, a, m, n, K, m * n, verdict)
        print(line)
        if verdict == "SAT":
            print("     witness P(%d,%d)=%d, primitive (re-verified):" % (m, n, pv))
            for row in cfg:
                print("     ", "".join(str(c) for c in row))
        sys.stdout.flush()


if __name__ == "__main__":
    main()
