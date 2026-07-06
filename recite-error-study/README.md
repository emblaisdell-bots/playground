# Do models copy injected errors, or silently "correct" them?

**Research question.** If you ask an open-weight model to *copy / recite* a
well-known, training-data-plentiful string (digits of π, a Shakespeare sonnet,
a nursery rhyme) that you have quietly corrupted with a small error, does the
error show up in the model's output — or does the model "fix" it back to the
canonical version it memorized during training?

This repo answers that empirically on **four real open-weight models** — the
full GPT‑2 family (`distilgpt2` 82M, `gpt2` 124M, `gpt2-medium` 355M,
`gpt2-large` 774M) — spanning ~10× in size, run locally on CPU with
`transformers`.

## The mechanism being measured

Copying a string that is *also* memorized pits two transformer mechanisms
against each other:

| mechanism | wants to output | favored by |
|---|---|---|
| **in‑context copying** (induction / copy heads) | the token literally in the prompt (**the error**) | a clear copy cue, a well‑matched prefix |
| **memorized prior** (parametric recall) | the token seen in training (**the canonical version**) | high‑frequency strings, larger models |

The output at the error position is a competition between the two. We read that
competition directly off the logits.

## Method

We put a base LM into an explicit **copy regime** (no chat template needed):

```
Original: <corrupted source string>
Copy: <corrupted source up to the error>▮      <-- read the distribution here
```

At the error position the two mechanisms predict *different* tokens, so we
define, per stimulus:

```
fidelity  = P(error_token) / (P(error_token) + P(canonical_token))
            1.0  -> faithful copy   (error preserved)
            0.0  -> silent correction (memory overrode the prompt)
corrected = 1 if P(canonical) > P(error)
```

We also **measure "commonness" directly** instead of guessing it:
`memorization_strength` = the model's greedy accuracy at *continuing* the
canonical string from a short prefix (no copy in context). High = burned in.

## Experiments (`src/run_experiment.py`)

- **exp1 – main grid**: 4 models × 15 stimuli (incl. zero‑memorization
  controls), neutral copy. → model‑size × commonness effects.
- **exp2 – framing**: models × 11 memorized stimuli × 5 prompt framings
  (`neutral`, `exact` = "copy exactly", `fix` = "correct errors", `clutter`,
  `recite`). → the "insistence on exactness" and "clutter" factors.
- **exp3 – distance**: one digit of a 100‑digit π corrupted at increasing
  depth. → the "prompt size / copy distance" factor, cleanly isolated.
- **exp4 – generation**: greedy full copies, does the error survive end‑to‑end?
  (tangible examples.)

## Reproduce

```bash
pip install torch transformers matplotlib numpy
# weights are the full-precision GPT-2 PyTorch bins in weights/ (see weights/dir_*)
python3 src/run_experiment.py all      # writes results/*.csv
python3 src/analyze.py                  # writes figures/*.png + summary
```

Weights were pulled from the public `models.huggingface.co` S3 mirror and
arranged as `transformers`-loadable dirs under `weights/dir_<model>/`. The
tokenizer (`vocab.json` + `merges.txt`) is shared across all four sizes.

See **FINDINGS.md** for the full results and the answer to each sub-question.
