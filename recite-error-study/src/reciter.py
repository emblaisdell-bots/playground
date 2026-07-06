"""
Core library for the "copy-with-errors" study.

Question: when a model is asked to copy/recite a famous, training-data-plentiful
string that contains a small INTENTIONAL error, does it reproduce the error
(faithful copy) or silently "correct" it back to the canonical memorized version?

Two competing mechanisms inside a transformer:
  (1) in-context copying  (induction / copy heads)   -> preserves the error
  (2) memorized prior      (parametric recall)         -> restores canonical token

We measure the tug-of-war directly on GPT-2 family base LMs (no chat template),
by putting the model into an explicit COPY regime and reading the logits at the
exact position where the injected error lives.

Copy regime (induction prompt), no instruction tuning required:

    <preamble?>Original: <SOURCE>\nCopy: <SOURCE up to error>[MEASURE HERE]

The model has seen SOURCE once and is repeating it. At the error position the
two mechanisms disagree:
    faithful copy   -> predicts the ERROR token (what's actually in SOURCE)
    memorized recall-> predicts the CANONICAL token (what training data says)

Primary metric (per error position):
    fidelity   = P(error) / (P(error) + P(canonical))     in [0,1]
                 1.0 => faithful copy (error preserved)
                 0.0 => silent correction (memory overrides the prompt)
    corrected  = 1 if argmax over {error,canonical} == canonical else 0
"""
import os, json, math
import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast

WEIGHTS = os.path.join(os.path.dirname(__file__), "..", "weights")
torch.set_num_threads(int(os.environ.get("NTHREADS", "4")))
torch.manual_seed(0)

_CACHE = {}

def load(model_name):
    """model_name in {distilgpt2, gpt2, gpt2-medium, gpt2-large}"""
    if model_name in _CACHE:
        return _CACHE[model_name]
    d = os.path.join(WEIGHTS, f"dir_{model_name}")
    tok = GPT2TokenizerFast.from_pretrained(d)
    model = GPT2LMHeadModel.from_pretrained(d)
    model.eval()
    _CACHE[model_name] = (model, tok)
    return model, tok


@torch.no_grad()
def next_token_dist(model, ids):
    """logits distribution for the position AFTER the given id sequence."""
    out = model(torch.tensor([ids]))
    logits = out.logits[0, -1]
    return torch.log_softmax(logits, dim=-1)


def single_token_id(tok, text_piece, leading_space=True):
    """Encode a small piece that we expect to be exactly one BPE token.
    Returns (id, n_tokens). We keep the first token id and report how many
    tokens it actually split into so callers can pick clean single-token swaps."""
    s = (" " if leading_space else "") + text_piece
    ids = tok.encode(s)
    return ids[0], len(ids)


@torch.no_grad()
def memorization_strength(model, tok, canonical_text, prefix_frac=0.35):
    """How strongly the model 'knows' this string = its ability to CONTINUE it
    from a short canonical prefix, with NO copy in context. This operationalizes
    'commonness in training data' as a measured quantity.

    Returns dict with:
      greedy_acc : fraction of continuation tokens the model predicts greedily
      mean_logp  : mean log-prob it assigns to the true continuation tokens
    Higher => the string is more 'burned in' (more common / plentiful).
    """
    ids = tok.encode(canonical_text)
    n = len(ids)
    cut = max(1, int(n * prefix_frac))
    correct = 0
    total_lp = 0.0
    steps = 0
    for k in range(cut, n):
        logp = next_token_dist(model, ids[:k])
        true_id = ids[k]
        total_lp += logp[true_id].item()
        if int(torch.argmax(logp)) == true_id:
            correct += 1
        steps += 1
    return {
        "greedy_acc": correct / steps if steps else float("nan"),
        "mean_logp": total_lp / steps if steps else float("nan"),
        "n_tokens": n,
        "scored_tokens": steps,
    }


def build_copy_prompt(source_text, error_prefix_text, preamble="",
                      orig_label="Original: ", copy_label="\nCopy: "):
    """Text fed to the model. Measurement happens right after `error_prefix_text`
    inside the Copy line, i.e. the model is about to emit the error/canonical token."""
    return f"{preamble}{orig_label}{source_text}{copy_label}{error_prefix_text}"


def first_diff_index(a_ids, b_ids):
    """index of first differing token between two id lists."""
    for i in range(min(len(a_ids), len(b_ids))):
        if a_ids[i] != b_ids[i]:
            return i
    return None


@torch.no_grad()
def fidelity_at_error(model, tok, canonical_source, corrupted_source,
                      preamble="", copy_label="\nCopy: ", orig_label="Original: "):
    """
    Token-level, robust to BPE quirks.

    canonical_source : the correct famous string
    corrupted_source : same string with ONE injected error

    Puts the model in copy mode over the CORRUPTED source, walks the Copy line up
    to the first token that differs from canonical, and reads the distribution
    there. At that position:
        faithful copy    -> corrupted token id  (the injected error)
        memorized recall -> canonical token id  (silent correction)
    """
    can_ids = tok.encode(canonical_source)
    cor_ids = tok.encode(corrupted_source)
    p = first_diff_index(can_ids, cor_ids)
    if p is None:
        raise ValueError("canonical and corrupted tokenize identically")
    can_id = can_ids[p]   # canonical token (what memory 'wants')
    err_id = cor_ids[p]   # error token     (what the prompt literally shows)

    # Build: <preamble>Original: <corrupted>\nCopy: <corrupted tokens up to p>
    header_ids = tok.encode(f"{preamble}{orig_label}{corrupted_source}{copy_label}")
    ctx = header_ids + cor_ids[:p]
    logp = next_token_dist(model, ctx)

    p_err = math.exp(logp[err_id].item())
    p_can = math.exp(logp[can_id].item())
    denom = p_err + p_can
    fidelity = p_err / denom if denom > 0 else float("nan")
    greedy_id = int(torch.argmax(logp))
    return {
        "canonical_token": tok.decode([can_id]),
        "error_token": tok.decode([err_id]),
        "err_id": err_id, "can_id": can_id,
        "p_error": p_err, "p_canonical": p_can,
        "fidelity": fidelity,                       # 1=copied error, 0=corrected
        "corrected": int(p_can > p_err),            # memory beat the prompt
        "greedy_is_canonical": int(greedy_id == can_id),
        "greedy_is_error": int(greedy_id == err_id),
        "greedy_token": tok.decode([greedy_id]),
        "error_token_pos": p,
        "prompt_tokens": len(ctx),
    }


@torch.no_grad()
def generate_copy(model, tok, corrupted_source, preamble="", max_new=None,
                  copy_label="\nCopy: ", orig_label="Original: "):
    """Actually generate a full copy (greedy) and return the produced text, so we
    can diff it against the corrupted source and count how many errors survived."""
    prompt = f"{preamble}{orig_label}{corrupted_source}{copy_label}"
    ids = tok.encode(prompt)
    src_len = len(tok.encode(corrupted_source))
    max_new = max_new or (src_len + 4)
    out = model.generate(
        torch.tensor([ids]),
        max_new_tokens=max_new,
        do_sample=False,
        pad_token_id=tok.eos_token_id,
    )
    gen = out[0, len(ids):]
    text = tok.decode(gen)
    # trim at first newline (end of the copy line)
    if "\n" in text:
        text = text[:text.index("\n")]
    return text.strip()
