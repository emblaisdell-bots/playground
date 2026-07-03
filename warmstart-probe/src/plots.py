"""Figures, generated from results/tables/*.csv so a reviewer can re-plot without re-extracting."""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES = os.path.join(HERE, "results", "tables")
FIGS = os.path.join(HERE, "results", "figures")

COND_COLOR = {"C0": "#6c757d", "C1": "#2a9d8f", "C2": "#264653", "C3": "#e76f51"}
COND_LABEL = {
    "C0": "C0 cold",
    "C1": "C1 instruction",
    "C2": "C2 few-shot",
    "C3": "C3 irrelevant (ctrl)",
}


def _load(name):
    p = os.path.join(TABLES, name)
    return pd.read_csv(p) if os.path.exists(p) else None


def plot_conditions(task):
    """(a) Condition comparison bars with the C3 control and the B0 baseline line."""
    summ = _load("condition_summary.csv")
    b0 = _load("baseline_b0.csv")
    if summ is None:
        return
    d = summ[summ.task == task].set_index("condition")
    conds = [c for c in ["C0", "C1", "C2", "C3"] if c in d.index]
    means = [d.loc[c, "acc_mean"] for c in conds]
    los = [d.loc[c, "acc_mean"] - d.loc[c, "acc_lo"] for c in conds]
    his = [d.loc[c, "acc_hi"] - d.loc[c, "acc_mean"] for c in conds]
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.bar(
        range(len(conds)),
        means,
        yerr=[los, his],
        capsize=5,
        color=[COND_COLOR[c] for c in conds],
    )
    ax.set_xticks(range(len(conds)))
    ax.set_xticklabels([COND_LABEL[c] for c in conds], rotation=15, ha="right")
    ax.set_ylabel("test accuracy")
    ax.set_title(f"{task}: condition comparison (mean ± 95% CI over seeds)")
    if b0 is not None and task in set(b0.task):
        m = b0[b0.task == task].acc.mean()
        ax.axhline(m, ls="--", color="black", lw=1)
        ax.text(len(conds) - 0.5, m, f" B0 TF-IDF {m:.3f}", va="bottom", ha="right", fontsize=8)
    lo = min(means) - 0.05
    ax.set_ylim(max(0, lo), 1.0)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, f"fig_conditions_{task}.png"), dpi=130)
    plt.close(fig)


def plot_learning_curve(task):
    """(b) Learning curves for C0/C1/C2 and the C1-C0 gap."""
    lc = _load("learning_curve.csv")
    if lc is None:
        return
    d = lc[lc.task == task]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
    for c in ["C0", "C1", "C2"]:
        sub = d[d.condition == c]
        if sub.empty:
            continue
        g = sub.groupby("train_size").acc.agg(["mean", "std"]).reset_index()
        ax1.errorbar(
            g.train_size, g["mean"], yerr=g["std"], marker="o", capsize=3,
            color=COND_COLOR[c], label=COND_LABEL[c],
        )
    ax1.set_xscale("log")
    ax1.set_xlabel("head train size")
    ax1.set_ylabel("test accuracy")
    ax1.set_title(f"{task}: learning curves")
    ax1.legend(fontsize=8)

    c0 = d[d.condition == "C0"].groupby("train_size").acc.mean()
    c1 = d[d.condition == "C1"].groupby("train_size").acc.mean()
    gap = (c1 - c0).reset_index()
    ax2.axhline(0, color="black", lw=0.8)
    ax2.plot(gap.train_size, gap.acc, marker="o", color=COND_COLOR["C1"])
    ax2.set_xscale("log")
    ax2.set_xlabel("head train size")
    ax2.set_ylabel("C1 - C0 accuracy gap")
    ax2.set_title(f"{task}: priming gain vs data (H3)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, f"fig_learning_curve_{task}.png"), dpi=130)
    plt.close(fig)


def plot_layer_sweep(task):
    """(c) Layer x pooling val-accuracy sweep per condition (seed 0)."""
    sw = _load("layer_sweep.csv")
    if sw is None:
        return
    d = sw[sw.task == task]
    conds = sorted(d.condition.unique())
    poolings = sorted(d.pooling.unique())
    layers = sorted(d.layer.unique())
    fig, axes = plt.subplots(1, len(conds), figsize=(3.1 * len(conds), 3.4), squeeze=False)
    for j, c in enumerate(conds):
        ax = axes[0][j]
        grid = np.zeros((len(poolings), len(layers)))
        for pi, p in enumerate(poolings):
            for li, L in enumerate(layers):
                row = d[(d.condition == c) & (d.pooling == p) & (d.layer == L)]
                grid[pi, li] = row.val_acc.mean() if not row.empty else np.nan
        im = ax.imshow(grid, aspect="auto", cmap="viridis", vmin=grid.min(), vmax=grid.max())
        ax.set_xticks(range(len(layers)))
        ax.set_xticklabels(layers)
        ax.set_yticks(range(len(poolings)))
        ax.set_yticklabels(poolings)
        ax.set_title(COND_LABEL.get(c, c), fontsize=9)
        ax.set_xlabel("layer")
        for pi in range(len(poolings)):
            for li in range(len(layers)):
                ax.text(li, pi, f"{grid[pi,li]:.2f}", ha="center", va="center",
                        color="white", fontsize=7)
    fig.suptitle(f"{task}: val accuracy by layer x pooling")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, f"fig_layer_sweep_{task}.png"), dpi=130)
    plt.close(fig)


def plot_distill(task):
    """(d) Distillation panel: standalone-distilled vs hard-label vs prefix-carrying teacher."""
    ds = _load("distill_summary.csv")
    if ds is None:
        return
    d = ds[ds.task == task].set_index("variant")
    order = [v for v in ["hard_standalone", "distilled_standalone", "teacher_with_prefix"] if v in d.index]
    labels = {
        "hard_standalone": "standalone\n(hard labels)",
        "distilled_standalone": "standalone\n(distilled)",
        "teacher_with_prefix": "teacher\n(with prefix)",
    }
    colors = {"hard_standalone": "#6c757d", "distilled_standalone": "#2a9d8f",
              "teacher_with_prefix": "#264653"}
    means = [d.loc[v, "acc_mean"] for v in order]
    los = [d.loc[v, "acc_mean"] - d.loc[v, "acc_lo"] for v in order]
    his = [d.loc[v, "acc_hi"] - d.loc[v, "acc_mean"] for v in order]
    fig, ax = plt.subplots(figsize=(6, 4.2))
    ax.bar(range(len(order)), means, yerr=[los, his], capsize=5,
           color=[colors[v] for v in order])
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([labels[v] for v in order])
    ax.set_ylabel("test accuracy")
    ax.set_title(f"{task}: context distillation to standalone (H4)")
    lo = min(means) - 0.05
    ax.set_ylim(max(0, lo), 1.0)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS, f"fig_distill_{task}.png"), dpi=130)
    plt.close(fig)


def make_all(tasks):
    os.makedirs(FIGS, exist_ok=True)
    for task in tasks:
        plot_conditions(task)
        plot_learning_curve(task)
        plot_layer_sweep(task)
        plot_distill(task)
