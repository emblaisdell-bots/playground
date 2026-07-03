# warmstart-probe

**Does warm-starting from a context-primed transformer yield better standalone classifiers?**

A controlled, CPU-only study on a frozen GPT-2 small (124M) backbone. We test whether
"pre-loading" the transformer with task-relevant context (an instruction or few-shot prefix)
produces **better features for a lightweight downstream classifier** than the same transformer
with no context — and whether that advantage can be **distilled into a prefix-free ("standalone")
classifier** needing no context at inference time.

Only the prefix changes across conditions; backbone, layer, pooling, and head budget are held
fixed. A length-matched *irrelevant* prefix (C3) separates *relevance of context* from *mere
presence of extra tokens* — this is the load-bearing control.

## Conditions

| id | condition | prefix |
|----|-----------|--------|
| C0 | Cold (baseline / B1) | none |
| C1 | Instruction prime | natural-language task description |
| C2 | Few-shot prime | k=4 labelled in-context examples + instruction |
| C3 | Irrelevant prime (control) | unrelated text, token-length-matched to C1 |

Baselines: **B0** = TF-IDF + logistic regression (does the backbone help at all?); **B1** = C0.

## Hypotheses

- **H1** priming helps features (C1/C2 > C0).
- **H2** relevance, not length (C1 > C3). *Load-bearing control.*
- **H3** the priming gain is largest in the low-data regime.
- **H4** the advantage distils into a prefix-free standalone classifier (**the real target**).
- **H5** the effect is task-dependent (SST-2 vs AG News).

## How to run

```bash
pip install -r requirements.txt

# 1. Download GPT-2 weights + datasets into ./assets (run where network is available).
python scripts/prefetch.py

# 2. Smoke test (<10 min): validates wiring end-to-end.
python run_all.py --quick

# 3. Full study (CPU, ~1–2.5 h). Features are cached, so re-runs skip extraction.
python run_all.py

# Optionally restrict tasks:
python run_all.py --tasks sst2
```

Outputs land in:

- `FINDINGS.md` — per-hypothesis verdicts, effect sizes, explicit null/negative call-outs.
- `results/tables/*.csv` — per-seed scores, summaries with 95% CIs, paired stats, distillation.
- `results/figures/*.png` — (a) condition bars + C3 control + B0 line, (b) learning curves +
  C1−C0 gap, (c) layer×pooling sweep, (d) distillation panel.
- `results/cache/` — cached features (git-ignored); delete to force re-extraction.

## Network / offline notes

`huggingface.co` is blocked in many sandboxes. `scripts/prefetch.py` deliberately avoids it,
sourcing everything from mirrors that are commonly allow-listed:

- GPT-2 weights + tokenizer: the legacy HuggingFace bucket on `s3.amazonaws.com` (static, public).
- SST-2 / AG News: labelled CSV/TSV mirrors on `raw.githubusercontent.com`.

After prefetch, the main run is fully offline. If `./assets` is missing and the network is
blocked, the run fails loudly pointing you back to prefetch.

## Design

- **Frozen-backbone / train-a-head** (not untie-and-prune): pays only the tied-weight cost
  (~0.25 GB) + forward-pass FLOPs, which is what makes a day-on-a-laptop budget real.
- One forward per (example, condition) with `output_hidden_states=True` captures **all layers in
  a single pass**; layers `{4,8,12}` and pooling `{last, mean-over-input}` are selected on val.
- Head: scikit-learn logistic regression. Phase-2 distillation student: a torch linear head
  trained on soft teacher targets (KL) — head-only, so still cheap.
- **Config-driven:** every task / condition / size / seed lives in `config.yaml`; swapping the
  model id, tasks, or head type is a config change, not a rewrite.

## Layout

```
warmstart-probe/
  config.yaml            # tasks, conditions, sizes, seeds, layers, model id
  requirements.txt
  scripts/prefetch.py    # download model + datasets into ./assets (run online)
  src/
    data.py              # load/subsample SST-2 & AG News from offline mirrors
    prefixes.py          # C0..C4 prefix builders; length-match C3 to C1
    extract.py           # frozen forwards, all hidden states, cache to .npz
    probe.py             # sklearn heads; layer x pooling sweep; select on val
    distill.py           # Phase 2 context distillation (soft-label head)
    evaluate.py          # accuracy, macro-F1, bootstrap CIs, paired seed stats
    plots.py             # condition bars, learning curves, layer sweep, distill panel
  run_all.py             # orchestrates the full study; --quick smoke mode
  results/               # tables/, figures/, cache/ (cache git-ignored)
```
