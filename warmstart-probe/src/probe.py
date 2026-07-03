"""Logistic-regression probe heads with layer x pooling selection on val.

Features come in as [N, n_layers, n_poolings, H]. For each (layer, pooling) slice we
standardise and fit a logistic-regression head; the slice with the best val accuracy is
selected. Per-seed subsampling of the train pool drives the seed variability and the
learning curves.
"""
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


def _slice(X, li, pi):
    return X[:, li, pi, :]


def subsample_indices(labels, n, num_labels, seed):
    """Balanced draw of ``n`` indices from a pool, seed-dependent (train-subset draw)."""
    rng = np.random.default_rng(1000 + seed)
    per = n // num_labels
    idx = []
    labels = np.asarray(labels)
    for c in range(num_labels):
        pool = np.where(labels == c)[0]
        take = min(per, len(pool))
        idx.extend(rng.choice(pool, size=take, replace=False).tolist())
    rng.shuffle(idx)
    return np.array(idx, dtype=np.int64)


def fit_head(Xtr, ytr, seed):
    scaler = StandardScaler().fit(Xtr)
    clf = LogisticRegression(max_iter=2000, C=1.0, random_state=seed)
    clf.fit(scaler.transform(Xtr), ytr)
    return scaler, clf


def select_and_fit(Xtr, ytr, Xva, yva, layers, poolings, seed):
    """Sweep (layer,pooling), fit on train, select the slice with best val accuracy.

    Returns dict with the fitted scaler/clf, chosen (li,pi), and the val accuracy.
    """
    best = None
    for li in range(len(layers)):
        for pi in range(len(poolings)):
            scaler, clf = fit_head(_slice(Xtr, li, pi), ytr, seed)
            acc = clf.score(scaler.transform(_slice(Xva, li, pi)), yva)
            if best is None or acc > best["val_acc"]:
                best = {
                    "scaler": scaler,
                    "clf": clf,
                    "li": li,
                    "pi": pi,
                    "layer": layers[li],
                    "pooling": poolings[pi],
                    "val_acc": acc,
                }
    return best


def predict(model, X):
    Xs = _slice(X, model["li"], model["pi"])
    Xs = model["scaler"].transform(Xs)
    return model["clf"].predict(Xs)


def predict_proba(model, X):
    Xs = _slice(X, model["li"], model["pi"])
    Xs = model["scaler"].transform(Xs)
    return model["clf"].predict_proba(Xs)
