"""Correctness tests for nivat_core primitives. Run: python3 nivat_core_test.py

These are the ONLY guarantee that experiment outputs mean what we claim, so
every primitive is checked against a hand-computed or independently-derived
value.
"""
from nivat_core import (patterns, P, is_period, period_vectors, is_primitive,
                        min_period_norm, factors_1d, p_1d, least_period_1d)


def check(cond, msg):
    if not cond:
        raise AssertionError("FAIL: " + msg)
    print("ok:", msg)


# --- P(1,1) = number of distinct symbols used ---
x = [[0, 1], [1, 0]]
check(P(x, 1, 1) == 2, "P(1,1) counts distinct symbols on 2x2 checkerboard")

# --- constant config: everything periodic, P(m,n)=1 ---
c = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
check(P(c, 2, 2) == 1, "constant config has P(2,2)=1")
check(is_period(c, 1, 0) and is_period(c, 0, 1), "constant config: (1,0),(0,1) periods")
check(not is_primitive(c), "constant config not primitive")

# --- horizontal stripes: period (1,0); P(m,n) depends only on rows ---
s = [[0, 0, 0], [1, 1, 1], [0, 0, 0], [1, 1, 1]]  # 4x3, vertical period 2
check(is_period(s, 2, 0), "stripes period (2,0)")
check(not is_primitive(s), "stripes not primitive")
# distinct 2x1 vertical windows: (0,1) and (1,0) -> P(2,1)=2
check(P(s, 2, 1) == 2, "stripes P(2,1)=2")
check(P(s, 1, 3) == 2, "stripes P(1,3)=2 (two row types)")

# --- checkerboard 2x2 torus: period (1,1) since x[i+1][j+1]=x[i][j] ---
cb = [[0, 1], [1, 0]]
check(is_period(cb, 1, 1), "checkerboard has period (1,1)")
check(not is_primitive(cb), "checkerboard not primitive")

# --- a primitive config exists: 2x2 with three symbols distinct pattern ---
# 0 1 / 1 1 : check periods manually
q = [[0, 1], [1, 1]]
pv = period_vectors(q)
check(pv == [], "q=[[0,1],[1,1]] is primitive (no nonzero period), got %r" % pv)
check(is_primitive(q), "q primitive")
check(min_period_norm(q) is None, "primitive -> min_period_norm None")

# --- period subgroup closure sanity: if (1,0) and (0,1) are periods so is (1,1)
check(is_period(c, 1, 1), "constant: (1,1) period (subgroup closed)")

# --- pattern set size bounded by a^(mn) and by N*M ---
r = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
check(len(patterns(r, 2, 2)) <= 3 * 3, "P(2,2) <= N*M offsets")

# --- 1D Morse-Hedlund sanity ---
# Sturmian-like: 0 1 0 0 1 (Fibonacci-ish) least period 5 (primitive necklace)
w = [0, 1, 0, 0, 1]
check(least_period_1d(w) == 5, "w=01001 least period 5")
# primitive cyclic word of length L: p(n) >= n+1 for 1<=n<=L-1 (M-H sharpness dir)
for n in range(1, 5):
    check(p_1d(w, n) >= n + 1, "01001 primitive => p(%d) >= %d" % (n, n + 1))
# p(L) for least-period-L word == L
check(p_1d(w, 5) == 5, "p(5)=5 for length-5 primitive word")

# --- factors count: full-period word 010101 (period 2) has p(n)=2 for n>=1 ---
w2 = [0, 1, 0, 1, 0, 1]
check(least_period_1d(w2) == 2, "010101 least period 2")
check(p_1d(w2, 1) == 2 and p_1d(w2, 3) == 2, "period-2 word: p(n)=2")

print("\nALL CORE TESTS PASSED")
