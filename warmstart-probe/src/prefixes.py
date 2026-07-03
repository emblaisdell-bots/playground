"""Prefix builders for conditions C0..C3 (and helpers for C4 soft prompts).

Only the prefix changes across conditions; the backbone, layer, pooling and head budget are
held fixed. The load-bearing control is C3: an *irrelevant* prefix truncated to exactly the
same token length as the C1 instruction, so any C1>C3 gap is attributable to relevance rather
than to sequence length / extra compute.
"""

# --- Natural-language task instructions (C1) -------------------------------------------------
INSTRUCTIONS = {
    "sst2": (
        "The following is a movie review. Decide whether the sentiment it expresses is "
        "positive or negative.\n\nReview: "
    ),
    "agnews": (
        "The following is a news article. Classify its topic as World, Sports, Business, "
        "or Sci/Tech.\n\nArticle: "
    ),
}

# --- Few-shot demo templates (C2) ------------------------------------------------------------
DEMO_TEMPLATES = {
    "sst2": ("Review: {text}\nSentiment: {label}\n\n"),
    "agnews": ("Article: {text}\nTopic: {label}\n\n"),
}
INPUT_LEADIN = {"sst2": "Review: ", "agnews": "Article: "}

# --- Irrelevant filler for the length-matched control (C3) -----------------------------------
# Topic-neutral prose with no sentiment / news-topic signal; sliced to match C1's token length.
IRRELEVANT_FILLER = (
    "The lighthouse keeper recorded the tide tables every morning before dawn. Copper wire "
    "was wound around the spool in even layers while the kettle came slowly to a boil. A map "
    "of the northern railway lines hung above the workbench next to a jar of assorted brass "
    "screws. The recipe called for two cups of flour, a pinch of salt, and a quarter teaspoon "
    "of baking soda folded in gently. Sediment settled at the bottom of the glass as the "
    "afternoon light moved across the wooden floor of the empty reading room. "
)


def instruction_prefix(task):
    return INSTRUCTIONS[task]


def _label_name(cfg, task, y):
    return cfg["tasks"][task]["label_names"][int(y)]


def build_few_shot_demos(task, cfg, demo_texts, demo_labels):
    """Assemble the fixed instruction + k labelled demos block used by C2 (a single string)."""
    tmpl = DEMO_TEMPLATES[task]
    block = INSTRUCTIONS[task].split("\n\n")[0] + "\n\n"  # keep the instruction sentence only
    for t, y in zip(demo_texts, demo_labels):
        block += tmpl.format(text=t, label=_label_name(cfg, task, y))
    block += INPUT_LEADIN[task]
    return block


def irrelevant_prefix(task, tokenizer):
    """C3: irrelevant text truncated to exactly the C1 instruction's token length."""
    target_len = len(tokenizer(INSTRUCTIONS[task], add_special_tokens=False)["input_ids"])
    filler_ids = tokenizer(IRRELEVANT_FILLER, add_special_tokens=False)["input_ids"]
    while len(filler_ids) < target_len:  # unlikely, but be safe
        filler_ids = filler_ids + filler_ids
    sliced = filler_ids[:target_len]
    return tokenizer.decode(sliced)


def pick_few_shot_demos(task, cfg, train_texts, train_labels):
    """Pick k balanced demos from the train pool (deterministic: first-per-class)."""
    import numpy as np

    k = cfg["few_shot_k"]
    num_labels = cfg["tasks"][task]["num_labels"]
    per = max(1, k // num_labels)
    idx = []
    labels = np.asarray(train_labels)
    for c in range(num_labels):
        cls_idx = np.where(labels == c)[0][:per]
        idx.extend(cls_idx.tolist())
    idx = idx[:k]
    return [train_texts[i] for i in idx], [int(train_labels[i]) for i in idx], idx


def build_prefix(condition, task, cfg, tokenizer, few_shot_block=None):
    """Return the prefix STRING for a condition (input text is appended by the caller).

    C0 -> "" ; C1 -> instruction ; C2 -> instruction+demos+leadin ; C3 -> length-matched filler.
    """
    if condition == "C0":
        return ""
    if condition == "C1":
        return instruction_prefix(task)
    if condition == "C2":
        if few_shot_block is None:
            raise ValueError("C2 requires a precomputed few_shot_block")
        return few_shot_block
    if condition == "C3":
        return irrelevant_prefix(task, tokenizer)
    raise ValueError(f"unknown / non-string condition {condition}")


def prefix_signature(condition, task, cfg, tokenizer, few_shot_block=None):
    """A short string fully determining the features, used in the feature-cache hash."""
    if condition == "C2":
        return f"C2::{few_shot_block}"
    return f"{condition}::{build_prefix(condition, task, cfg, tokenizer, few_shot_block)}"
