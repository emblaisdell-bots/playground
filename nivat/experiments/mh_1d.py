"""mh_1d.py — computational Morse-Hedlund (the 1D base case Nivat generalizes).

Morse-Hedlund (1938): a bi-infinite word is periodic iff its factor complexity
p(n) <= n for some n; equivalently p(n) <= n+? ... precisely, the word has
period <= n iff p(n) <= n.

Finite surrogate on a cycle Z_L: a cyclic word of LEAST period L ("primitive
necklace") is the finite analogue of an aperiodic word up to scale L.  We verify
exhaustively over all binary necklaces up to length Lmax:

  (1) every primitive cyclic word satisfies p(n) >= n+1 for all 1<=n<L
      (the aperiodic direction: complexity strictly exceeds the window),
  (2) the bound is SHARP: min over primitive words of p(n) equals n+1 for each
      n<L (achieved by Sturmian-like necklaces),

so mn=n is exactly the threshold in 1D.  This mirrors, one dimension down, the
2D torus finding that primitive configs need P(m,n) >= mn+1.
"""
from __future__ import annotations
from itertools import product
from nivat_core import p_1d, least_period_1d


def run(Lmax=18):
    print("1D Morse-Hedlund finite check (binary cyclic words)")
    print(" L  | #primitive | min p(n) over primitive words, n=1..L-1")
    ok = True
    for L in range(2, Lmax + 1):
        nprim = 0
        minp = {n: None for n in range(1, L)}
        for bits in product((0, 1), repeat=L):
            w = list(bits)
            if least_period_1d(w) != L:
                continue
            nprim += 1
            for n in range(1, L):
                pv = p_1d(w, n)
                if pv < n + 1:            # would violate M-H sharpness
                    ok = False
                if minp[n] is None or pv < minp[n]:
                    minp[n] = pv
        row = "  ".join("%d:%s" % (n, minp[n]) for n in range(1, L))
        print("%3d | %10d | %s" % (L, nprim, row))
        # check sharpness: min p(n) == n+1 for every n<L (when primitives exist)
        if nprim:
            for n in range(1, L):
                assert minp[n] is not None
                if minp[n] != n + 1:
                    print("   NOTE L=%d n=%d: min p(n)=%d (not n+1=%d)"
                          % (L, n, minp[n], n + 1))
    print("\naperiodic direction p(n)>=n+1 held everywhere:", ok)


if __name__ == "__main__":
    run()
