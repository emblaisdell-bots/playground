"""
Run the copy-with-errors experiments and write CSVs to results/.

  exp1  main grid : 4 models x all stimuli, neutral copy  -> fidelity vs size & commonness
  exp2  framing   : models x common stimuli x prompt conditions (exactness / fix / clutter)
  exp3  distance  : error injected at increasing depth into pi  -> distance/length effect
  exp4  generate  : greedy full-copy examples, did the error survive? (tangible)
"""
import os, sys, csv, json, time
sys.path.insert(0, os.path.dirname(__file__))
import reciter as R
import stimuli as S

RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(RESULTS, exist_ok=True)

MODELS = ["distilgpt2", "gpt2", "gpt2-medium", "gpt2-large"]

# prompt conditions: (preamble, orig_label, copy_label)
CLUTTER = ("Weather report: light rain is expected across the northern hills this "
           "afternoon, with gusts near the coast easing by evening. In unrelated "
           "market news, futures dipped slightly before recovering at the open. ")
CONDITIONS = {
    "neutral": dict(preamble="", orig_label="Original: ", copy_label="\nCopy: "),
    "exact":   dict(preamble="Copy the following text EXACTLY, preserving every "
                             "character including any mistakes or typos.\n",
                    orig_label="Text: ", copy_label="\nExact copy: "),
    "fix":     dict(preamble="Repeat the following text, silently correcting any "
                             "errors so it reads correctly.\n",
                    orig_label="Text: ", copy_label="\nCorrected: "),
    "clutter": dict(preamble=CLUTTER, orig_label="Original: ", copy_label="\nCopy: "),
    "recite":  dict(preamble="Recite the well-known passage from memory:\n",
                    orig_label="Passage: ", copy_label="\nRecited: "),
}

COMMON_SUBSET = ["pi", "e", "fib", "sonnet18", "sonnet18b", "hamlet", "genesis",
                 "twinkle", "lords", "alphabet", "gettysburg"]


def write_csv(name, rows, fields):
    path = os.path.join(RESULTS, name)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fields})
    print("wrote", path, f"({len(rows)} rows)")


def exp1_main():
    rows = []
    for mn in MODELS:
        m, tok = R.load(mn)
        for st in S.STIMULI:
            corr = S.corrupted_of(st)
            mem = R.memorization_strength(m, tok, st["canonical"])
            fid = R.fidelity_at_error(m, tok, st["canonical"], corr, **CONDITIONS["neutral"])
            rows.append(dict(model=mn, stim=st["id"], cat=st["cat"], prior=st["prior"],
                             mem_greedy_acc=round(mem["greedy_acc"], 4),
                             mem_mean_logp=round(mem["mean_logp"], 4),
                             n_tokens=mem["n_tokens"],
                             fidelity=round(fid["fidelity"], 4),
                             corrected=fid["corrected"],
                             greedy_is_canonical=fid["greedy_is_canonical"],
                             p_error=round(fid["p_error"], 5),
                             p_canonical=round(fid["p_canonical"], 5),
                             canonical_token=fid["canonical_token"],
                             error_token=fid["error_token"]))
        print(f"  exp1 {mn} done")
    write_csv("exp1_main.csv", rows,
              ["model","stim","cat","prior","n_tokens","mem_greedy_acc","mem_mean_logp",
               "fidelity","corrected","greedy_is_canonical","p_error","p_canonical",
               "canonical_token","error_token"])
    return rows


def exp2_framing():
    rows = []
    models = ["distilgpt2", "gpt2", "gpt2-medium", "gpt2-large"]
    for mn in models:
        m, tok = R.load(mn)
        for sid in COMMON_SUBSET:
            st = next(s for s in S.STIMULI if s["id"] == sid)
            corr = S.corrupted_of(st)
            for cond, cfg in CONDITIONS.items():
                fid = R.fidelity_at_error(m, tok, st["canonical"], corr, **cfg)
                rows.append(dict(model=mn, stim=sid, condition=cond,
                                 fidelity=round(fid["fidelity"], 4),
                                 corrected=fid["corrected"],
                                 greedy_is_canonical=fid["greedy_is_canonical"],
                                 prompt_tokens=fid["prompt_tokens"]))
        print(f"  exp2 {mn} done")
    write_csv("exp2_framing.csv", rows,
              ["model","stim","condition","fidelity","corrected",
               "greedy_is_canonical","prompt_tokens"])
    return rows


def exp3_distance():
    """Inject the SAME kind of error at increasing depth into a long recited pi,
    to isolate copy-distance / prompt-size effects from string identity."""
    PI = ("3.141592653589793238462643383279502884197169399375105820974944592307"
          "816406286208998628034825342117067")
    rows = []
    # canonical source is 'Pi = <PI>'.  Corrupt a single digit at various depths.
    for mn in ["gpt2", "gpt2-medium", "gpt2-large"]:
        m, tok = R.load(mn)
        for depth in [6, 12, 20, 30, 45, 60, 80, 100]:
            if depth >= len(PI):
                continue
            d = PI[depth]
            newd = str((int(d) + 5) % 10)
            corr_pi = PI[:depth] + newd + PI[depth+1:]
            canonical = f"Pi = {PI}"
            corrupted = f"Pi = {corr_pi}"
            try:
                fid = R.fidelity_at_error(m, tok, canonical, corrupted, **CONDITIONS["neutral"])
            except ValueError:
                continue
            rows.append(dict(model=mn, depth_digits=depth,
                             fidelity=round(fid["fidelity"], 4),
                             corrected=fid["corrected"],
                             error_token_pos=fid["error_token_pos"],
                             prompt_tokens=fid["prompt_tokens"]))
        print(f"  exp3 {mn} done")
    write_csv("exp3_distance.csv", rows,
              ["model","depth_digits","error_token_pos","prompt_tokens",
               "fidelity","corrected"])
    return rows


def exp4_generate():
    """Greedy full-copy: does the injected error survive end-to-end?"""
    rows = []
    examples = ["pi","sonnet18","hamlet","twinkle","genesis","rand_digits","nonsense"]
    for mn in ["gpt2","gpt2-large"]:
        m, tok = R.load(mn)
        for sid in examples:
            st = next(s for s in S.STIMULI if s["id"] == sid)
            corr = S.corrupted_of(st)
            for cond in ["neutral","fix"]:
                cfg = CONDITIONS[cond]
                gen = R.generate_copy(m, tok, corr, preamble=cfg["preamble"],
                                      orig_label=cfg["orig_label"], copy_label=cfg["copy_label"])
                err_survived = int(st["replace"] in gen)
                canon_restored = int(st["find"] in gen and st["replace"] not in gen)
                rows.append(dict(model=mn, stim=sid, condition=cond,
                                 corrupted=corr, generated=gen,
                                 error_survived=err_survived,
                                 canon_restored=canon_restored))
        print(f"  exp4 {mn} done")
    write_csv("exp4_generate.csv", rows,
              ["model","stim","condition","error_survived","canon_restored",
               "corrupted","generated"])
    return rows


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    t0 = time.time()
    if which in ("all","1"): exp1_main()
    if which in ("all","2"): exp2_framing()
    if which in ("all","3"): exp3_distance()
    if which in ("all","4"): exp4_generate()
    print(f"done in {time.time()-t0:.1f}s")
