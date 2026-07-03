#!/usr/bin/env python3
"""Orchestrate the full warm-start probe study.

Pipeline per task:
  1. load balanced splits  2. extract frozen features per condition (cached)
  3. B0 TF-IDF baseline     4. condition comparison (5 seeds)
  5. learning curves        6. layer x pooling sweep
  7. context distillation to a standalone head (Phase 2)
Then: write CSV tables, generate figures, and auto-write FINDINGS.md.

    python run_all.py                 # full study (config.yaml)
    python run_all.py --quick         # <10 min smoke test (wiring validation)
    python run_all.py --tasks sst2    # subset of tasks
"""
import argparse
import copy
import os
import sys
import time

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src import data as data_mod  # noqa: E402
from src import distill as distill_mod  # noqa: E402
from src import evaluate as ev  # noqa: E402
from src import extract as extract_mod  # noqa: E402
from src import plots as plots_mod  # noqa: E402
from src import prefixes as pfx  # noqa: E402
from src import probe as probe_mod  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TABLES = os.path.join(HERE, "results", "tables")
LOGP = os.path.join(HERE, "results", "run.log")

_LOGF = None


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    if _LOGF:
        _LOGF.write(line + "\n")
        _LOGF.flush()


def load_cfg(path):
    with open(path) as f:
        return yaml.safe_load(f)


def apply_quick(cfg):
    """Small, fast overrides for wiring validation (<10 min)."""
    cfg = copy.deepcopy(cfg)
    cfg["data"] = {"pool_seed": 0, "train_pool": 300, "val": 100, "test": 200}
    cfg["seeds"] = [0, 1]
    cfg["train_sizes"] = [100, 300]
    cfg["layers"] = [12]
    cfg["poolings"] = ["mean"]
    cfg["conditions"] = ["C0", "C1"]
    cfg["distill"]["epochs"] = 100
    return cfg


# ---------------------------------------------------------------------------------------------
def build_condition_features(task, cfg, splits):
    """Extract (and cache) features for every condition; returns dict cond -> {split: X}."""
    _, tok = extract_mod.get_model_and_tokenizer(cfg)
    tr_texts, tr_labels = splits["train"]
    demo_texts, demo_labels, _ = pfx.pick_few_shot_demos(task, cfg, tr_texts, tr_labels)
    few_shot_block = pfx.build_few_shot_demos(task, cfg, demo_texts, demo_labels)

    feats = {}
    for cond in cfg["conditions"]:
        prefix = pfx.build_prefix(cond, task, cfg, tok, few_shot_block)
        sig = pfx.prefix_signature(cond, task, cfg, tok, few_shot_block)
        if cond == "C1":
            log(f"    C1 instruction prefix: {prefix!r}")
        if cond == "C3":
            log(f"    C3 filler prefix (len-matched to C1): {prefix!r}")
        feats[cond] = {}
        for split in ["train", "val", "test"]:
            texts, _ = splits[split]
            feats[cond][split] = extract_mod.extract_features(
                task, cond, split, texts, cfg, prefix, sig, log=log
            )
    return feats


def run_conditions(task, cfg, splits, feats, rows_scores):
    """Condition comparison at full train size, 5 seeds; append per-seed rows."""
    num_labels = cfg["tasks"][task]["num_labels"]
    _, tr_y = splits["train"]
    va_y = splits["val"][1]
    te_y = splits["test"][1]
    full = cfg["data"]["train_pool"]
    for cond in cfg["conditions"]:
        for seed in cfg["seeds"]:
            idx = probe_mod.subsample_indices(tr_y, full, num_labels, seed)
            Xtr, ytr = feats[cond]["train"][idx], tr_y[idx]
            m = probe_mod.select_and_fit(
                Xtr, ytr, feats[cond]["val"], va_y, cfg["layers"], cfg["poolings"], seed
            )
            pred = probe_mod.predict(m, feats[cond]["test"])
            rows_scores.append(
                {
                    "task": task, "condition": cond, "seed": seed,
                    "acc": ev.accuracy(te_y, pred), "f1": ev.macro_f1(te_y, pred),
                    "val_acc": m["val_acc"], "layer": m["layer"], "pooling": m["pooling"],
                }
            )
        accs = [r["acc"] for r in rows_scores if r["task"] == task and r["condition"] == cond]
        log(f"    {cond}: test acc {np.mean(accs):.4f} (±{np.std(accs):.4f}) over {len(accs)} seeds")


def run_learning_curve(task, cfg, splits, feats, rows_lc):
    num_labels = cfg["tasks"][task]["num_labels"]
    _, tr_y = splits["train"]
    va_y, te_y = splits["val"][1], splits["test"][1]
    lc_conditions = [c for c in ["C0", "C1", "C2"] if c in cfg["conditions"]]
    for size in cfg["train_sizes"]:
        if size > cfg["data"]["train_pool"]:
            continue
        for cond in lc_conditions:
            for seed in cfg["seeds"]:
                idx = probe_mod.subsample_indices(tr_y, size, num_labels, seed)
                Xtr, ytr = feats[cond]["train"][idx], tr_y[idx]
                m = probe_mod.select_and_fit(
                    Xtr, ytr, feats[cond]["val"], va_y, cfg["layers"], cfg["poolings"], seed
                )
                pred = probe_mod.predict(m, feats[cond]["test"])
                rows_lc.append(
                    {"task": task, "condition": cond, "train_size": size,
                     "seed": seed, "acc": ev.accuracy(te_y, pred)}
                )


def run_layer_sweep(task, cfg, splits, feats, rows_sweep):
    """Per-condition val accuracy for every (layer,pooling) at seed 0 (for the figure)."""
    num_labels = cfg["tasks"][task]["num_labels"]
    _, tr_y = splits["train"]
    va_y = splits["val"][1]
    idx = probe_mod.subsample_indices(tr_y, cfg["data"]["train_pool"], num_labels, 0)
    for cond in cfg["conditions"]:
        Xtr = feats[cond]["train"][idx]
        for li, L in enumerate(cfg["layers"]):
            for pi, P in enumerate(cfg["poolings"]):
                scaler, clf = probe_mod.fit_head(Xtr[:, li, pi, :], tr_y[idx], 0)
                acc = clf.score(scaler.transform(feats[cond]["val"][:, li, pi, :]), va_y)
                rows_sweep.append(
                    {"task": task, "condition": cond, "layer": L, "pooling": P, "val_acc": acc}
                )


def run_baseline_b0(task, cfg, splits, rows_b0):
    """B0: TF-IDF + logistic regression on raw text (does the backbone help at all?)."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression

    num_labels = cfg["tasks"][task]["num_labels"]
    tr_texts, tr_y = splits["train"]
    te_texts, te_y = splits["test"]
    for seed in cfg["seeds"]:
        idx = probe_mod.subsample_indices(tr_y, cfg["data"]["train_pool"], num_labels, seed)
        vec = TfidfVectorizer(max_features=20000, ngram_range=(1, 2), min_df=2)
        Xtr = vec.fit_transform([tr_texts[i] for i in idx])
        clf = LogisticRegression(max_iter=2000, random_state=seed)
        clf.fit(Xtr, tr_y[idx])
        pred = clf.predict(vec.transform(te_texts))
        rows_b0.append({"task": task, "seed": seed, "acc": ev.accuracy(te_y, pred)})


def run_distillation(task, cfg, splits, feats, summary_scores, rows_distill):
    """Phase 2: pick best primed condition by val, distil into a prefix-free (C0) student."""
    if "C0" not in cfg["conditions"]:
        log("    distillation skipped (no C0 features)")
        return None
    primed = [c for c in ["C2", "C1"] if c in cfg["conditions"]]
    if not primed:
        log("    distillation skipped (no primed condition)")
        return None
    # teacher condition = primed condition with the best mean val accuracy
    teacher_cond = max(
        primed, key=lambda c: summary_scores[(task, c)]["val_acc_mean"]
    )
    log(f"    teacher condition (best val): {teacher_cond}")

    num_labels = cfg["tasks"][task]["num_labels"]
    _, tr_y = splits["train"]
    va_y, te_y = splits["val"][1], splits["test"][1]
    full = cfg["data"]["train_pool"]
    for seed in cfg["seeds"]:
        idx = probe_mod.subsample_indices(tr_y, full, num_labels, seed)
        ytr = tr_y[idx]
        # teacher: primed head -> soft targets on train, accuracy WITH prefix on test
        tm = probe_mod.select_and_fit(
            feats[teacher_cond]["train"][idx], ytr, feats[teacher_cond]["val"], va_y,
            cfg["layers"], cfg["poolings"], seed,
        )
        soft = probe_mod.predict_proba(tm, feats[teacher_cond]["train"][idx])
        teacher_pred = probe_mod.predict(tm, feats[teacher_cond]["test"])

        # standalone students use COLD (C0) features at train and inference (no prefix)
        c0_li, c0_pi = _best_c0_slice(cfg, feats, tr_y, va_y, idx, seed)
        X0_tr = feats["C0"]["train"][idx][:, c0_li, c0_pi, :]
        X0_te = feats["C0"]["test"][:, c0_li, c0_pi, :]

        pred_soft = distill_mod.train_soft_student(X0_tr, soft, X0_te, cfg, seed)
        pred_hard = distill_mod.train_hard_student(X0_tr, ytr, X0_te, cfg, seed)

        for variant, pred in [
            ("teacher_with_prefix", teacher_pred),
            ("distilled_standalone", pred_soft),
            ("hard_standalone", pred_hard),
        ]:
            rows_distill.append(
                {"task": task, "variant": variant, "seed": seed,
                 "acc": ev.accuracy(te_y, pred), "f1": ev.macro_f1(te_y, pred)}
            )
    return teacher_cond


def _best_c0_slice(cfg, feats, tr_y, va_y, idx, seed):
    """Pick the C0 (layer,pooling) that maximises val accuracy, for the student's input."""
    best, best_acc = (0, 0), -1
    for li in range(len(cfg["layers"])):
        for pi in range(len(cfg["poolings"])):
            scaler, clf = probe_mod.fit_head(feats["C0"]["train"][idx][:, li, pi, :], tr_y[idx], seed)
            acc = clf.score(scaler.transform(feats["C0"]["val"][:, li, pi, :]), va_y)
            if acc > best_acc:
                best, best_acc = (li, pi), acc
    return best


# ---------------------------------------------------------------------------------------------
def summarise_conditions(df, tasks):
    rows = []
    summ_lookup = {}
    for task in tasks:
        for cond in df[df.task == task].condition.unique():
            sub = df[(df.task == task) & (df.condition == cond)]
            am, alo, ahi = ev.mean_ci(sub.acc.values)
            fm, flo, fhi = ev.mean_ci(sub.f1.values)
            rows.append(
                {"task": task, "condition": cond, "acc_mean": am, "acc_lo": alo, "acc_hi": ahi,
                 "f1_mean": fm, "f1_lo": flo, "f1_hi": fhi,
                 "val_acc_mean": sub.val_acc.mean(), "n_seeds": len(sub)}
            )
            summ_lookup[(task, cond)] = {"acc_mean": am, "val_acc_mean": sub.val_acc.mean()}
    return pd.DataFrame(rows), summ_lookup


def paired_stats(df, tasks):
    rows = []
    for task in tasks:
        def accs(c):
            s = df[(df.task == task) & (df.condition == c)].sort_values("seed")
            return s.acc.values
        conds = set(df[df.task == task].condition)
        pairs = []
        if {"C1", "C0"} <= conds:
            pairs.append(("C1-C0", "C1", "C0"))
        if {"C2", "C0"} <= conds:
            pairs.append(("C2-C0", "C2", "C0"))
        if {"C1", "C3"} <= conds:
            pairs.append(("C1-C3", "C1", "C3"))
        for name, a, b in pairs:
            m, lo, hi = ev.paired_diff_ci(accs(a), accs(b))
            rows.append({"task": task, "comparison": name, "mean": m, "lo": lo, "hi": hi})
        # relevance-attributable gain = (C1-C0) - (C3-C0) = C1-C3
        if {"C1", "C3"} <= conds:
            m, lo, hi = ev.paired_diff_ci(accs("C1"), accs("C3"))
            rows.append({"task": task, "comparison": "relevance_gain(C1-C3)",
                         "mean": m, "lo": lo, "hi": hi})
    return pd.DataFrame(rows)


def summarise_distill(df, tasks):
    rows = []
    for task in tasks:
        for v in df[df.task == task].variant.unique():
            sub = df[(df.task == task) & (df.variant == v)]
            am, alo, ahi = ev.mean_ci(sub.acc.values)
            rows.append({"task": task, "variant": v, "acc_mean": am, "acc_lo": alo, "acc_hi": ahi,
                         "n_seeds": len(sub)})
    return pd.DataFrame(rows)


def write_findings(cfg, tasks, cond_summary, paired, distill_summary, b0, teacher_by_task, quick):
    """Auto-write FINDINGS.md with per-hypothesis verdicts and effect sizes."""
    lines = ["# FINDINGS", ""]
    if quick:
        lines += ["> **Generated in `--quick` smoke mode** — tiny data, 2 seeds, 1 layer/pooling, "
                  "C0+C1 only. Numbers validate wiring, not science. Run `python run_all.py` for "
                  "the real study.", ""]
    lines += [
        "Auto-generated by `run_all.py`. Seeds are few (n=5); treat as **directional evidence**, "
        "not proof. All CIs are bootstrap percentile intervals over per-seed scores.",
        "",
    ]

    def cs(task, cond, field):
        r = cond_summary[(cond_summary.task == task) & (cond_summary.condition == cond)]
        return None if r.empty else float(r[field].iloc[0])

    def pr(task, name):
        r = paired[(paired.task == task) & (paired.comparison == name)]
        return None if r.empty else (float(r["mean"].iloc[0]), float(r.lo.iloc[0]), float(r.hi.iloc[0]))

    for task in tasks:
        lines.append(f"## {task}")
        b0m = b0[b0.task == task].acc.mean() if b0 is not None and task in set(b0.task) else float("nan")
        lines.append("")
        lines.append("| condition | test acc | 95% CI |")
        lines.append("|---|---|---|")
        for cond in ["C0", "C1", "C2", "C3"]:
            m = cs(task, cond, "acc_mean")
            if m is None:
                continue
            lo, hi = cs(task, cond, "acc_lo"), cs(task, cond, "acc_hi")
            lines.append(f"| {plots_label(cond)} | {m:.4f} | [{lo:.4f}, {hi:.4f}] |")
        lines.append(f"| B0 TF-IDF+LR | {b0m:.4f} | — |")
        lines.append("")

        # H1
        d = pr(task, "C1-C0")
        if d:
            verdict = "SUPPORTED" if d[1] > 0 else ("null" if d[2] > 0 else "not supported")
            lines.append(f"- **H1 (priming helps features):** C1−C0 = {d[0]:+.4f} "
                         f"[{d[1]:+.4f}, {d[2]:+.4f}] → **{verdict}**"
                         + (" (CI excludes 0)." if d[1] > 0 else " (CI includes 0)."))
        d2 = pr(task, "C2-C0")
        if d2:
            lines.append(f"  - few-shot: C2−C0 = {d2[0]:+.4f} [{d2[1]:+.4f}, {d2[2]:+.4f}].")
        # H2
        rel = pr(task, "relevance_gain(C1-C3)")
        if rel:
            verdict = "SUPPORTED" if rel[1] > 0 else "null (gain may be length/compute, not relevance)"
            lines.append(f"- **H2 (relevance not length):** relevance gain C1−C3 = {rel[0]:+.4f} "
                         f"[{rel[1]:+.4f}, {rel[2]:+.4f}] → **{verdict}**.")
        # H3 handled qualitatively from learning curve figure
        lines.append("- **H3 (low-data advantage):** see `fig_learning_curve_%s.png` (C1−C0 gap vs "
                     "train size); reported qualitatively." % task)
        # H4
        if distill_summary is not None and task in set(distill_summary.task):
            def dv(v):
                r = distill_summary[(distill_summary.task == task) & (distill_summary.variant == v)]
                return None if r.empty else float(r.acc_mean.iloc[0])
            hard, dist, teach = dv("hard_standalone"), dv("distilled_standalone"), dv("teacher_with_prefix")
            if hard is not None and dist is not None:
                gain = dist - hard
                verdict = "SUPPORTED" if gain > 0.002 else "null (distillation ≈ hard labels)"
                lines.append(f"- **H4 (distillable to standalone):** distilled={dist:.4f} vs "
                             f"hard-label={hard:.4f} (Δ={gain:+.4f}); teacher-with-prefix={teach:.4f} "
                             f"→ **{verdict}**. Teacher used: {teacher_by_task.get(task, '?')}.")
        lines.append("")

    # H5 across tasks
    if len(tasks) >= 2 and all(pr(t, "C1-C0") for t in tasks):
        gains = {t: pr(t, "C1-C0")[0] for t in tasks}
        spread = max(gains.values()) - min(gains.values())
        lines.append("## H5 (task dependence)")
        lines.append("C1−C0 gain by task: " + ", ".join(f"{t}={g:+.4f}" for t, g in gains.items()))
        verdict = "SUPPORTED (gain differs across tasks)" if spread > 0.01 else "null (effect similar across tasks)"
        lines.append(f"→ **{verdict}** (spread = {spread:.4f}).")
        lines.append("")

    lines.append("## Notes on null/negative results")
    lines.append("- A null on H1 with C3≈C1 would say the prime adds nothing beyond extra tokens; "
                 "reported, not buried.")
    lines.append("- A null on H4 bounds the deployability story: priming helps only while the prefix "
                 "is present.")
    lines.append("")
    with open(os.path.join(HERE, "FINDINGS.md"), "w") as f:
        f.write("\n".join(lines))
    log("  wrote FINDINGS.md")


def plots_label(cond):
    return {"C0": "C0 cold", "C1": "C1 instruction", "C2": "C2 few-shot",
            "C3": "C3 irrelevant (control)"}.get(cond, cond)


# ---------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--tasks", nargs="*", default=None)
    args = ap.parse_args()

    global _LOGF
    os.makedirs(TABLES, exist_ok=True)
    os.makedirs(os.path.dirname(LOGP), exist_ok=True)
    _LOGF = open(LOGP, "a")

    cfg = load_cfg(os.path.join(HERE, args.config))
    if args.quick:
        cfg = apply_quick(cfg)
    tasks = args.tasks if args.tasks else list(cfg["tasks"].keys())

    t_start = time.time()
    log("=" * 70)
    log(f"WARM-START PROBE  quick={args.quick}  tasks={tasks}  seeds={cfg['seeds']}")
    log(f"conditions={cfg['conditions']}  layers={cfg['layers']}  poolings={cfg['poolings']}")
    est = len(tasks) * len(cfg["conditions"]) * (cfg["data"]["train_pool"] + cfg["data"]["val"] + cfg["data"]["test"])
    log(f"~{est} forward passes to extract (cached; re-runs skip). ETA a few min–hours on CPU.")
    log("=" * 70)

    rows_scores, rows_lc, rows_sweep, rows_b0, rows_distill = [], [], [], [], []
    teacher_by_task = {}
    all_feats = {}

    for task in tasks:
        log(f"\n### TASK: {task}")
        splits = data_mod.load_task(task, cfg)
        log(f"  splits: train={len(splits['train'][0])} val={len(splits['val'][0])} "
            f"test={len(splits['test'][0])}")
        feats = build_condition_features(task, cfg, splits)
        all_feats[task] = (splits, feats)
        log("  -> features extracted; running baseline + heads")
        run_baseline_b0(task, cfg, splits, rows_b0)
        run_conditions(task, cfg, splits, feats, rows_scores)
        run_learning_curve(task, cfg, splits, feats, rows_lc)
        run_layer_sweep(task, cfg, splits, feats, rows_sweep)

    df_scores = pd.DataFrame(rows_scores)
    cond_summary, summ_lookup = summarise_conditions(df_scores, tasks)

    # distillation needs the val-based teacher choice from summ_lookup
    for task in tasks:
        splits, feats = all_feats[task]
        log(f"\n### DISTILLATION: {task}")
        tc = run_distillation(task, cfg, splits, feats, summ_lookup, rows_distill)
        if tc:
            teacher_by_task[task] = tc

    # ---- write tables ----
    df_scores.to_csv(os.path.join(TABLES, "condition_scores.csv"), index=False)
    cond_summary.to_csv(os.path.join(TABLES, "condition_summary.csv"), index=False)
    pd.DataFrame(rows_lc).to_csv(os.path.join(TABLES, "learning_curve.csv"), index=False)
    pd.DataFrame(rows_sweep).to_csv(os.path.join(TABLES, "layer_sweep.csv"), index=False)
    df_b0 = pd.DataFrame(rows_b0)
    df_b0.to_csv(os.path.join(TABLES, "baseline_b0.csv"), index=False)
    df_paired = paired_stats(df_scores, tasks)
    df_paired.to_csv(os.path.join(TABLES, "paired_stats.csv"), index=False)
    df_distill = pd.DataFrame(rows_distill)
    distill_summary = None
    if not df_distill.empty:
        df_distill.to_csv(os.path.join(TABLES, "distill_scores.csv"), index=False)
        distill_summary = summarise_distill(df_distill, tasks)
        distill_summary.to_csv(os.path.join(TABLES, "distill_summary.csv"), index=False)
    log("  wrote tables to results/tables/")

    # ---- figures + findings ----
    plots_mod.make_all(tasks)
    log("  wrote figures to results/figures/")
    write_findings(cfg, tasks, cond_summary, df_paired, distill_summary, df_b0,
                   teacher_by_task, args.quick)

    log(f"\nDONE in {(time.time()-t_start)/60:.1f} min. See FINDINGS.md + results/.")
    _LOGF.close()


if __name__ == "__main__":
    main()
