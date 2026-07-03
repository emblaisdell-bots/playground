"""Load and subsample SST-2 & AG News from the offline CSV/TSV assets.

Produces fixed, balanced train-pool / val / test splits keyed by ``pool_seed`` so the
extracted feature pool is stable across head-training seeds. Per-seed subsampling of the
train pool happens later (in probe.py), not here.
"""
import csv
import os

import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "assets", "data")


def _require(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        raise FileNotFoundError(
            f"Missing dataset asset: {path}\n"
            "Run `python scripts/prefetch.py` (with network) first, or add the GitHub raw\n"
            "mirrors to the sandbox network allow-list. See scripts/prefetch.py."
        )
    return path


def _read_sst2(split):
    """Return (texts, labels) for an SST-2 split. File is `sentence\\tlabel`, no header."""
    path = _require(os.path.join(DATA, f"sst2_{split}.tsv"))
    texts, labels = [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            sent, lab = line.rsplit("\t", 1)
            texts.append(sent.strip())
            labels.append(int(lab))
    return texts, np.array(labels, dtype=np.int64)


def _read_agnews(split):
    """Return (texts, labels) for AG News. Rows: "class(1-4)","title","description"."""
    path = _require(os.path.join(DATA, f"agnews_{split}.csv"))
    texts, labels = [], []
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.reader(f):
            if len(row) < 3:
                continue
            cls, title, desc = row[0], row[1], row[2]
            texts.append(f"{title.strip()}. {desc.strip()}")
            labels.append(int(cls) - 1)  # 1..4 -> 0..3
    return texts, np.array(labels, dtype=np.int64)


def _balanced_subsample(texts, labels, n, num_labels, rng):
    """Draw ``n`` examples, balanced across labels (as evenly as divisible), without replacement."""
    per = n // num_labels
    idx = []
    for c in range(num_labels):
        pool = np.where(labels == c)[0]
        if len(pool) < per:
            raise ValueError(f"class {c} has only {len(pool)} examples, need {per}")
        idx.extend(rng.choice(pool, size=per, replace=False).tolist())
    rng.shuffle(idx)
    idx = np.array(idx, dtype=np.int64)
    return [texts[i] for i in idx], labels[idx]


def load_task(task, cfg):
    """Return a dict of splits: {'train': (texts,labels), 'val': ..., 'test': ...}.

    Balanced pools are drawn with a fixed ``pool_seed`` so feature extraction is deterministic.
    """
    dcfg = cfg["data"]
    num_labels = cfg["tasks"][task]["num_labels"]
    rng = np.random.default_rng(dcfg["pool_seed"])

    if task == "sst2":
        tr_t, tr_y = _read_sst2("train")
        va_t, va_y = _read_sst2("dev")
        te_t, te_y = _read_sst2("test")
    elif task == "agnews":
        tr_t, tr_y = _read_agnews("train")
        te_t, te_y = _read_agnews("test")
        # AG News has no dev split: carve val from the (large) train file, disjoint from the pool.
        n_pool = dcfg["train_pool"]
        n_val = dcfg["val"]
        va_t, va_y = _balanced_subsample(tr_t, tr_y, n_pool + n_val, num_labels, rng)
        # split the (pool+val) draw into disjoint pool and val
        va_t, va_y = list(va_t), va_y
        val_texts, val_labels = va_t[:n_val], va_y[:n_val]
        pool_texts, pool_labels = va_t[n_val:], va_y[n_val:]
        test_texts, test_labels = _balanced_subsample(te_t, te_y, dcfg["test"], num_labels, rng)
        return {
            "train": (pool_texts, pool_labels),
            "val": (val_texts, val_labels),
            "test": (test_texts, test_labels),
        }
    else:
        raise ValueError(f"unknown task {task}")

    train = _balanced_subsample(tr_t, tr_y, dcfg["train_pool"], num_labels, rng)
    val = _balanced_subsample(va_t, va_y, dcfg["val"], num_labels, rng)
    test = _balanced_subsample(te_t, te_y, dcfg["test"], num_labels, rng)
    return {"train": train, "val": val, "test": test}
