"""nivat_core.py — verified primitives for Nivat-conjecture experiments.

A *configuration on a torus* Z_N x Z_M is a 2D array `x` of shape (N, M) with
entries in a finite alphabet {0,...,a-1}.  Coordinates wrap (mod N, mod M).

Key notions (all finite / decidable):

* period vector      v=(dv,dw) is a *period* of x iff x[(i+dv)%N,(j+dw)%M]==x[i,j]
                     for all i,j.  The set of periods is a subgroup of Z_N x Z_M.
* genuinely periodic x has some NONZERO period v (i.e. period subgroup != {0}).
                     On a torus every config trivially has the zero element only
                     as "the identity"; (N,0) and (0,M) ARE the identity here, so
                     a config is genuinely periodic iff it has a period v with
                     (dv,dw) != (0,0) in Z_N x Z_M.
* primitive          = NOT genuinely periodic  = trivial period subgroup {(0,0)}.
                     Viewed as an infinite doubly-periodic config, a primitive
                     torus config has period lattice EXACTLY <(N,0),(0,M)> — the
                     coarsest possible; this is the finite surrogate for
                     "aperiodic up to scale (N,M)".
* P(m,n)             block complexity: number of DISTINCT m x n patterns
                     occurring as windows (with torus wrap) over all N*M offsets.

Nothing here asserts anything about Nivat's conjecture itself; these are just
exact, testable definitions used by the experiment scripts.  Correctness is
checked by nivat_core_test.py.
"""
from __future__ import annotations
from itertools import product
from typing import Iterable


def patterns(x: list[list[int]], m: int, n: int) -> set[tuple]:
    """Set of distinct m x n windows of torus config x (wrapping)."""
    N = len(x)
    M = len(x[0])
    out = set()
    for i in range(N):
        for j in range(M):
            out.add(tuple(x[(i + di) % N][(j + dj) % M]
                          for di in range(m) for dj in range(n)))
    return out


def P(x: list[list[int]], m: int, n: int) -> int:
    """Block complexity P_x(m,n) on the torus."""
    return len(patterns(x, m, n))


def is_period(x: list[list[int]], dv: int, dw: int) -> bool:
    N = len(x)
    M = len(x[0])
    for i in range(N):
        row = x[i]
        rv = x[(i + dv) % N]
        for j in range(M):
            if rv[(j + dw) % M] != row[j]:
                return False
    return True


def period_vectors(x: list[list[int]]) -> list[tuple[int, int]]:
    """All NONZERO period vectors (dv,dw) in Z_N x Z_M."""
    N = len(x)
    M = len(x[0])
    out = []
    for dv in range(N):
        for dw in range(M):
            if dv == 0 and dw == 0:
                continue
            if is_period(x, dv, dw):
                out.append((dv, dw))
    return out


def is_primitive(x: list[list[int]]) -> bool:
    """True iff x has NO nonzero period vector (period subgroup is trivial)."""
    N = len(x)
    M = len(x[0])
    for dv in range(N):
        for dw in range(M):
            if dv == 0 and dw == 0:
                continue
            if is_period(x, dv, dw):
                return False
    return True


def min_period_norm(x: list[list[int]]) -> int | None:
    """L-infinity norm of the shortest nonzero period vector, or None if primitive.

    For a period (dv,dw) we take min(dv, N-dv) and min(dw, M-dw) as the signed
    representative magnitudes (shortest wrap distance), then the Linf norm.
    """
    N = len(x)
    M = len(x[0])
    best = None
    for (dv, dw) in period_vectors(x):
        a = min(dv, N - dv)
        b = min(dw, M - dw)
        nrm = max(a, b)
        if best is None or nrm < best:
            best = nrm
    return best


# ---- 1D helpers (Morse-Hedlund sanity) ---------------------------------------

def factors_1d(w: list[int], n: int) -> set[tuple]:
    """Distinct length-n factors of the cyclic word w."""
    L = len(w)
    return {tuple(w[(i + k) % L] for k in range(n)) for i in range(L)}


def p_1d(w: list[int], n: int) -> int:
    return len(factors_1d(w, n))


def least_period_1d(w: list[int]) -> int:
    """Least period p (1<=p<=L, p | L not required) of cyclic word w."""
    L = len(w)
    for p in range(1, L + 1):
        if all(w[(i + p) % L] == w[i] for i in range(L)):
            return p
    return L


# ---- enumeration --------------------------------------------------------------

def all_configs(N: int, M: int, a: int) -> Iterable[list[list[int]]]:
    """Yield every config on Z_N x Z_M over alphabet {0..a-1}. a^(N*M) of them."""
    cells = N * M
    for flat in product(range(a), repeat=cells):
        yield [list(flat[r * M:(r + 1) * M]) for r in range(N)]
