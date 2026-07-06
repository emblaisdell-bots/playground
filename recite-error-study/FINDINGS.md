# Findings: will injected errors in copied famous strings survive, or get "corrected"?

**Short answer.** Yes, models *can* silently correct your errors back to the
memorized canonical version — but only under a specific, predictable set of
conditions. It is **not** an all-or-nothing property of the model; it is a
tug-of-war, resolved token-by-token, between *copying what's in the prompt* and
*recalling what's in the weights*. Whether the error survives depends far more
on **how memorized that specific token is** and **how big the model is** than on
how you word the request.

All numbers below are from four real open-weight models (GPT‑2 family, 82M–774M)
run locally; see `README.md` for method. The core metric is **copy fidelity** at
the error position: `P(error)/(P(error)+P(canonical))`, where **1.0 = the error
is preserved (faithful copy)** and **0.0 = the model silently restored the
canonical token**.

---

## The one-sentence model

> A token in your corrupted string gets "corrected" when the **memorized prior
> for that exact token** is strong enough to beat the **in-context copy signal**
> — and larger models have a much stronger memorized prior.

Everything below is a consequence of that.

---

## Factor-by-factor answer

### 1. Model size — the single biggest factor
Mean copy fidelity on memorized stimuli falls monotonically as the model grows,
while the zero-memorization controls stay pinned near 1.0 at every size:

| model | params | fidelity (memorized strings) | fidelity (controls) |
|---|---:|---:|---:|
| distilgpt2 | 82M | **0.980** | 0.999 |
| gpt2 | 124M | **0.970** | 0.999 |
| gpt2-medium | 355M | **0.870** | 0.998 |
| gpt2-large | 774M | **0.793** | 0.998 |

Small models (82M/124M) are almost perfectly faithful — they copy your error
essentially every time, because their memorized prior is too weak to override
the copy. Correction *emerges with scale*. The correlation between how memorized
a string is and how often it gets corrected literally **flips sign** with size:

| model | corr(memorization, correction) |
|---|---:|
| distilgpt2 | −0.18 |
| gpt2 | −0.19 |
| gpt2-medium | **+0.35** |
| gpt2-large | **+0.45** |

→ **Extrapolation:** modern 7B–70B+ open-weight models (Llama, Qwen, Mistral)
have vastly stronger memorization than gpt2-large, so they will correct
*more* aggressively on truly famous strings. The harness ships ready to test
them (see "Reproducing on bigger / chat models").

### 2. Commonness of the copied data — the second biggest factor
We didn't guess commonness; we **measured** it per string (greedy continuation
accuracy from a bare prefix). Correction rises with measured memorization — but
only once the model is big enough to have a prior at all (Fig. 2).

- **Zero-memorization controls** (random digit code, novel sentences): fidelity
  **0.994–1.000 across *every* model**. With no canonical version to snap back
  to, models copy faithfully — errors and all. This is the clean baseline: *the
  correction effect exists only where memorization exists.*
- **Fully-memorized lines** (mem≈1.0) are the ones that flip hardest. At
  gpt2-large:
  - `"...hallowed be thy fame"` → restored to **"thy name"**, fidelity **0.009**
  - `"it was the strangest of times"` → restored to **"worst"**, fidelity **0.185**

### 3. Commonness is *local*, not global — the most important nuance
Memorization is a property of the **specific token in its context**, not of the
"string" as a whole. Two demonstrations:

- **Same sonnet line, two different errors.** Corrupting `summer's`
  (in *"compare thee to a ___ day"* — a slot that overwhelmingly predicts
  "summer") gets pulled toward correction (fidelity 0.62 at gpt2-large).
  Corrupting `temperate` (in *"more lovely and more ___"* — a weakly-constrained
  slot) is copied faithfully (**fidelity 1.000 at every model**). Same famous
  line; opposite outcome.
- **Depth into π (Fig. 4).** Corrupt one digit of a 100-digit π at increasing
  depth. gpt2-large *corrects* an error in the **6th digit** (fidelity 0.39 —
  everyone's training data "knows" 3.14159…) but faithfully copies errors at
  **depth ≥30** (fidelity ≈1.0 — nobody memorizes π's 40th digit). The common
  *prefix* of a famous string is dangerous; its rare *tail* is safe.

### 4. Prompt's insistence on exactness — real but weak *for base models*
Averaged over memorized stimuli, prompt framing moved fidelity only modestly for
these base LMs, in the expected direction (higher = more faithful):

| framing | gpt2-medium | gpt2-large |
|---|---:|---:|
| `fix` ("correct any errors") | 0.931 | 0.878 |
| `neutral` ("Copy:") | 0.858 | 0.848 |
| `exact` ("copy EXACTLY, preserve mistakes") | **0.921** | **0.907** |

"Copy exactly" *does* raise fidelity and "correct the errors" isn't even needed
to trigger correction — but the swing is small (~0.06) and the hardest flips
(`lords`, `firstlines`) correct under *every* framing including `exact`. **Why
weak:** GPT‑2 is not instruction-tuned, so it barely "obeys" the instruction.
**This is the factor most likely to differ on instruction-tuned/chat models,**
where "copy exactly, character for character" is followed far more literally and
should substantially rescue fidelity — while a bare "recite the poem" invites
correction. (Testable with the shipped harness; base GPT‑2 gives only the lower
bound on this lever.)

### 5. Prompt clutter — minimal effect here
Prepending an unrelated distractor paragraph (`clutter`) barely changed fidelity
(gpt2-large 0.884 vs neutral 0.848 — if anything slightly *more* faithful,
because the extra text pushes the model further into "just continue the text"
copy mode rather than "recall the famous thing" mode). Clutter matters more when
it changes *which mode the model thinks it's in* than as generic noise.

### 6. Prompt size / copy distance — folded into distance (Fig. 4)
Longer well-matched copy context *strengthens* the induction/copy signal, so
errors deep in a long recitation are copied faithfully. Combined with factor 3
(deep tokens are also less memorized), both effects point the same way: **the
further into the string the error sits, the more likely it survives.**

---

## Putting it together: when does YOUR error get silently corrected?

**Most likely to be "corrected" (error disappears):**
- large / modern model, **and**
- the corrupted token sits in a **high-frequency, highly-predictable slot** of a
  very famous string (opening of π, first words of a canonical quote/prayer),
  **and**
- the prompt doesn't strongly insist on verbatim copying.

**Most likely to survive (error preserved):**
- small model; **or**
- the data isn't really memorized (random IDs, novel text, the rare *tail* of a
  long constant); **or**
- an explicit "copy exactly, keep all mistakes" instruction (esp. on chat
  models); **or**
- the error is deep in a long verbatim copy.

**The clean invariant:** on strings with *no* memorized prior, fidelity is
≈1.0 regardless of model size, framing, or clutter. Silent correction is a
memorization phenomenon — it can only overwrite what the model already knows.

---

## Caveats / honesty about scope
- **Base LMs, not chat models.** GPT‑2 is not instruction-tuned, so the *shape*
  of every effect is clean but the *instruction-following* factor (exactness) is
  a lower bound. The generation probe (`exp4`) is correspondingly noisy — base
  GPT‑2 tends to riff instead of copy — which is exactly why the primary result
  is the logit-level fidelity metric, not free generation.
- **Single-token errors, one measurement point.** We measure at the first
  corrupted token. Whether correction then *propagates* (does the model re-align
  to canonical for the rest of the line?) is a natural follow-up the harness can
  be extended to.
- **Metric is a 2-way contest.** Fidelity compares P(error) vs P(canonical); the
  model occasionally prefers a *third* token, which we report separately via the
  greedy fields.

## Reproducing on bigger / chat models
`src/reciter.py` is model-agnostic. Point `load()` at any HF causal LM
(Llama‑3.2, Qwen2.5, Mistral) once you have weights, and for chat models wrap
the source in the model's chat template with an explicit copy instruction. The
prediction: the size and commonness effects get *stronger*, and the
exactness-instruction lever becomes *much* more powerful.
