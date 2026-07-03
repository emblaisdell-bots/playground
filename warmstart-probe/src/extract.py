"""Frozen-backbone feature extraction with on-disk caching.

For each (task, condition, split) we run one forward per example with output_hidden_states=True
(all layers captured in a single pass) and pool the hidden states into features. Two pooling
schemes are computed and stored: last real token, and mean over the *input* tokens only
(prefix excluded). Selected layers are kept. Results are cached to .npz keyed by a hash of
everything that affects the features, so re-runs skip extraction entirely.
"""
import hashlib
import os
import time

import numpy as np
import torch

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(HERE, "results", "cache")

_MODEL = None
_TOK = None


def get_model_and_tokenizer(cfg):
    """Load GPT-2 small (frozen) + tokenizer from the local assets dir. Cached per process."""
    global _MODEL, _TOK
    if _MODEL is not None:
        return _MODEL, _TOK
    from transformers import GPT2Config, GPT2Model, GPT2TokenizerFast

    torch.set_num_threads(cfg["threads"])
    path = os.path.join(HERE, cfg["model"]["path"])
    if not os.path.exists(os.path.join(path, "pytorch_model.bin")):
        raise FileNotFoundError(
            f"Missing GPT-2 weights in {path}. Run `python scripts/prefetch.py` first."
        )
    conf = GPT2Config.from_json_file(os.path.join(path, "config.json"))
    tok = GPT2TokenizerFast(
        vocab_file=os.path.join(path, "vocab.json"),
        merges_file=os.path.join(path, "merges.txt"),
    )
    tok.pad_token = tok.eos_token
    tok.padding_side = "left"  # left-pad so the last real token is always at position -1
    model = GPT2Model(conf)
    sd = torch.load(os.path.join(path, "pytorch_model.bin"), map_location="cpu")
    model.load_state_dict(sd, strict=False)  # only the causal-mask buffers are 'unexpected'
    model.eval()
    for p in model.parameters():
        p.requires_grad_(False)
    _MODEL, _TOK = model, tok
    return model, tok


def _cache_key(task, condition, split, cfg, sig, texts):
    # Include a hash of the exact split texts so different subsamples of the same split never
    # collide on the same cache file (they would otherwise share task/condition/split/prefix).
    texts_h = hashlib.sha1(("\x1f".join(texts)).encode("utf-8")).hexdigest()[:10]
    payload = "|".join(
        [
            task,
            condition,
            split,
            sig,
            str(cfg["model"]["max_len"]),
            ",".join(map(str, cfg["layers"])),
            ",".join(cfg["poolings"]),
            os.path.basename(cfg["model"]["path"]),
            f"n{len(texts)}",
            texts_h,
        ]
    )
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]


def _encode_batch(tok, prefix, texts, max_len):
    """Tokenise prefix+text per example, cap total length, then left-pad into a batch.

    Returns input_ids, attention_mask, and input_lengths (# of input-text tokens per example,
    used for mean-over-input pooling).
    """
    prefix_ids = tok(prefix, add_special_tokens=False)["input_ids"] if prefix else []
    rows, input_lens = [], []
    budget = max_len - len(prefix_ids)
    if budget < 1:  # pathological: prefix alone exceeds cap -> keep at least 1 input token slot
        prefix_ids = prefix_ids[: max_len - 1]
        budget = 1
    for t in texts:
        inp = tok(t, add_special_tokens=False)["input_ids"][:budget]
        if len(inp) == 0:
            inp = tok(".", add_special_tokens=False)["input_ids"]
        rows.append(prefix_ids + inp)
        input_lens.append(len(inp))
    width = max(len(r) for r in rows)
    pad_id = tok.pad_token_id
    ids = np.full((len(rows), width), pad_id, dtype=np.int64)
    mask = np.zeros((len(rows), width), dtype=np.int64)
    for i, r in enumerate(rows):
        ids[i, width - len(r) :] = r  # left pad
        mask[i, width - len(r) :] = 1
    return (
        torch.from_numpy(ids),
        torch.from_numpy(mask),
        np.array(input_lens, dtype=np.int64),
    )


def _pool(hidden_states, layers, poolings, attn_mask, input_lens):
    """Pool selected layers with the requested schemes.

    hidden_states: tuple of [B,S,H] tensors (len n_layer+1). Left-padded, so the last real
    token is at index -1 and the input tokens are the final ``input_lens`` real positions.
    Returns array [B, n_layers, n_poolings, H].
    """
    B, S, H = hidden_states[0].shape
    out = np.zeros((B, len(layers), len(poolings), H), dtype=np.float32)
    for li, L in enumerate(layers):
        hs = hidden_states[L]  # [B,S,H]
        for pi, pool in enumerate(poolings):
            if pool == "last":
                out[:, li, pi, :] = hs[:, -1, :].numpy()
            elif pool == "mean":
                for b in range(B):
                    n = int(input_lens[b])
                    out[b, li, pi, :] = hs[b, S - n : S, :].mean(dim=0).numpy()
            else:
                raise ValueError(f"unknown pooling {pool}")
    return out


def extract_features(task, condition, split, texts, cfg, prefix, sig, log=print):
    """Return features [N, n_layers, n_poolings, H] for a split, using the cache if present."""
    os.makedirs(CACHE, exist_ok=True)
    key = _cache_key(task, condition, split, cfg, sig, texts)
    fpath = os.path.join(CACHE, f"{task}_{condition}_{split}_{key}.npz")
    if os.path.exists(fpath):
        return np.load(fpath)["X"]

    model, tok = get_model_and_tokenizer(cfg)
    layers, poolings = cfg["layers"], cfg["poolings"]
    max_len, bs = cfg["model"]["max_len"], cfg["model"]["batch_size"]
    feats = []
    t0 = time.time()
    n = len(texts)
    for start in range(0, n, bs):
        batch = texts[start : start + bs]
        ids, mask, ilen = _encode_batch(tok, prefix, batch, max_len)
        with torch.no_grad():
            out = model(input_ids=ids, attention_mask=mask, output_hidden_states=True)
        feats.append(_pool(out.hidden_states, layers, poolings, mask, ilen))
        del out
        if start % (bs * 20) == 0 and start > 0:
            rate = start / (time.time() - t0)
            log(f"      [{task}/{condition}/{split}] {start}/{n}  {rate:.1f} ex/s")
    X = np.concatenate(feats, axis=0)
    np.savez_compressed(fpath, X=X)
    log(
        f"      [{task}/{condition}/{split}] extracted {n} in {time.time()-t0:.1f}s "
        f"-> {os.path.relpath(fpath, HERE)}"
    )
    return X
