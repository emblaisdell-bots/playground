"""Read result CSVs, print summary tables, and render figures to figures/."""
import os, csv, sys
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(__file__)
RES = os.path.join(HERE, "..", "results")
FIG = os.path.join(HERE, "..", "figures")
os.makedirs(FIG, exist_ok=True)
MODELS = ["distilgpt2", "gpt2", "gpt2-medium", "gpt2-large"]
PARAMS = {"distilgpt2": 82, "gpt2": 124, "gpt2-medium": 355, "gpt2-large": 774}  # M
plt.rcParams.update({"figure.dpi": 130, "font.size": 10})


def rd(name):
    return list(csv.DictReader(open(os.path.join(RES, name))))


def fig_size_effect():
    rows = rd("exp1_main.csv")
    by = {(r["stim"], r["model"]): r for r in rows}
    stims, cats = [], {}
    for r in rows:
        if r["stim"] not in stims:
            stims.append(r["stim"]); cats[r["stim"]] = r["cat"]
    fig, ax = plt.subplots(figsize=(8, 5))
    x = list(range(len(MODELS)))
    for s in stims:
        is_ctrl = cats[s].startswith("control")
        y = [float(by[(s, m)]["fidelity"]) for m in MODELS]
        ax.plot(x, y, marker="o", lw=2 if is_ctrl else 1.3,
                color="0.6" if is_ctrl else None,
                ls="--" if is_ctrl else "-",
                label=s + (" (control)" if is_ctrl else ""), alpha=0.9)
    ax.set_xticks(x); ax.set_xticklabels([f"{m}\n{PARAMS[m]}M" for m in MODELS])
    ax.set_xlim(-0.2, len(MODELS) - 0.8)
    ax.set_ylabel("copy fidelity  (1=error preserved, 0=silently corrected)")
    ax.set_xlabel("model (params)")
    ax.set_title("Bigger models 'correct' injected errors in memorized strings;\ncontrols (no prior) stay faithful")
    ax.axhline(0.5, color="k", lw=0.6, ls=":")
    ax.legend(fontsize=6.5, ncol=2, loc="lower left")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig1_size_effect.png")); plt.close(fig)
    print("fig1 done")


def fig_commonness():
    rows = rd("exp1_main.csv")
    fig, ax = plt.subplots(figsize=(7.5, 5))
    colors = {"distilgpt2": "#8ecae6", "gpt2": "#219ebc",
              "gpt2-medium": "#fb8500", "gpt2-large": "#d00000"}
    for m in MODELS:
        xs = [float(r["mem_greedy_acc"]) for r in rows if r["model"] == m]
        ys = [1 - float(r["fidelity"]) for r in rows if r["model"] == m]
        ax.scatter(xs, ys, s=42, color=colors[m], label=f"{m} ({PARAMS[m]}M)",
                   edgecolor="k", linewidth=0.3, alpha=0.85)
    ax.set_xlabel("measured memorization of the string  (greedy continuation accuracy)")
    ax.set_ylabel("correction rate  (1 - fidelity)")
    ax.set_title("Correction requires BOTH a memorized prior (x) AND model capacity (color)")
    ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig2_commonness.png")); plt.close(fig)
    print("fig2 done")


def fig_framing():
    if not os.path.exists(os.path.join(RES, "exp2_framing.csv")):
        return
    rows = rd("exp2_framing.csv")
    conds = ["fix", "recite", "clutter", "neutral", "exact"]
    agg = defaultdict(list)
    for r in rows:
        agg[(r["model"], r["condition"])].append(float(r["fidelity"]))
    fig, ax = plt.subplots(figsize=(8, 5))
    width = 0.15
    import numpy as np
    xbase = np.arange(len(conds))
    colors = {"distilgpt2": "#8ecae6", "gpt2": "#219ebc",
              "gpt2-medium": "#fb8500", "gpt2-large": "#d00000"}
    for i, m in enumerate(MODELS):
        vals = [sum(agg[(m, c)]) / len(agg[(m, c)]) if agg[(m, c)] else float("nan") for c in conds]
        ax.bar(xbase + i * width, vals, width, label=f"{m}", color=colors[m], edgecolor="k", lw=0.3)
    ax.set_xticks(xbase + 1.5 * width); ax.set_xticklabels(conds)
    ax.set_ylabel("mean copy fidelity over memorized stimuli")
    ax.set_xlabel("prompt framing")
    ax.set_title("Prompt framing has only a MODEST effect on base GPT-2 (all means >0.8);\n'exact' is highest for large models — a lower bound (chat models should respond far more)")
    ax.legend(fontsize=8); ax.axhline(0.5, color="k", lw=0.6, ls=":")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig3_framing.png")); plt.close(fig)
    print("fig3 done")


def fig_distance():
    if not os.path.exists(os.path.join(RES, "exp3_distance.csv")):
        return
    rows = rd("exp3_distance.csv")
    fig, ax = plt.subplots(figsize=(7.5, 5))
    colors = {"gpt2": "#219ebc", "gpt2-medium": "#fb8500", "gpt2-large": "#d00000"}
    for m in ["gpt2", "gpt2-medium", "gpt2-large"]:
        pts = [(int(r["depth_digits"]), float(r["fidelity"])) for r in rows if r["model"] == m]
        pts.sort()
        if pts:
            ax.plot([p[0] for p in pts], [p[1] for p in pts], marker="o",
                    label=f"{m} ({PARAMS[m]}M)", color=colors[m])
    ax.set_xlabel("depth of injected error (digits into pi)")
    ax.set_ylabel("copy fidelity")
    ax.set_title("Deeper into the recited string, the copy signal strengthens:\nerrors early in pi get corrected, later ones are copied")
    ax.legend(fontsize=8); ax.axhline(0.5, color="k", lw=0.6, ls=":")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig4_distance.png")); plt.close(fig)
    print("fig4 done")


def summary():
    rows = rd("exp1_main.csv")
    print("\n=== correction counts (fidelity<0.5) by model ===")
    for m in MODELS:
        mr = [r for r in rows if r["model"] == m]
        corr = sum(1 for r in mr if float(r["fidelity"]) < 0.5)
        memhi = [r for r in mr if float(r["mem_greedy_acc"]) >= 0.6 and not r["cat"].startswith("control")]
        corr_hi = sum(1 for r in memhi if float(r["fidelity"]) < 0.5)
        print(f"  {m:12} corrected {corr}/{len(mr)} overall; "
              f"{corr_hi}/{len(memhi)} among high-memorization items")
    ctrl = [r for r in rows if r["cat"].startswith("control")]
    print(f"  controls: mean fidelity {sum(float(r['fidelity']) for r in ctrl)/len(ctrl):.3f} "
          f"(min {min(float(r['fidelity']) for r in ctrl):.3f}) across all models")


if __name__ == "__main__":
    summary()
    fig_size_effect()
    fig_commonness()
    fig_framing()
    fig_distance()
