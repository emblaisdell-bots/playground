"""Metrics, bootstrap CIs, and paired-across-seed statistics."""
import numpy as np
from sklearn.metrics import accuracy_score, f1_score


def accuracy(y_true, y_pred):
    return float(accuracy_score(y_true, y_pred))


def macro_f1(y_true, y_pred):
    return float(f1_score(y_true, y_pred, average="macro"))


def mean_ci(values, alpha=0.05, n_boot=2000, seed=0):
    """Mean and bootstrap (percentile) CI over a small sample of per-seed scores."""
    v = np.asarray(values, dtype=np.float64)
    m = float(v.mean())
    if len(v) < 2:
        return m, m, m
    rng = np.random.default_rng(seed)
    boots = [rng.choice(v, size=len(v), replace=True).mean() for _ in range(n_boot)]
    lo, hi = np.percentile(boots, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return m, float(lo), float(hi)


def paired_diff_ci(a, b, alpha=0.05, n_boot=2000, seed=0):
    """Paired difference (a-b) across seeds with a bootstrap CI. a,b are per-seed score lists."""
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    d = a - b
    m = float(d.mean())
    if len(d) < 2:
        return m, m, m
    rng = np.random.default_rng(seed)
    boots = [rng.choice(d, size=len(d), replace=True).mean() for _ in range(n_boot)]
    lo, hi = np.percentile(boots, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return m, float(lo), float(hi)


def seed_noise_band(per_seed_scores):
    """A simple seed-to-seed noise band: std across seeds (used to judge H1 margins)."""
    v = np.asarray(per_seed_scores, dtype=np.float64)
    return float(v.std(ddof=1)) if len(v) > 1 else 0.0
