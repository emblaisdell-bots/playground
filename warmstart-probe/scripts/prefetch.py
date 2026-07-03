#!/usr/bin/env python3
"""Prefetch GPT-2 small weights/tokenizer and the SST-2 / AG News datasets into ./assets.

Run this ONCE where network is available. After it succeeds, the main study is fully
offline. All sources are chosen to be reachable from restricted sandboxes that allow-list
GitHub + the legacy HuggingFace S3 bucket but block huggingface.co itself:

  * GPT-2 weights/tokenizer : s3.amazonaws.com/models.huggingface.co/bert/  (public, static)
  * SST-2                   : raw.githubusercontent.com (clairett mirror, labelled splits)
  * AG News                 : raw.githubusercontent.com (CharCnn_Keras mirror)

Usage:
    python scripts/prefetch.py            # download everything missing
    python scripts/prefetch.py --force    # re-download even if present
"""
import argparse
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(HERE, "assets")

GPT2_BASE = "https://s3.amazonaws.com/models.huggingface.co/bert"
GPT2_FILES = {
    "pytorch_model.bin": f"{GPT2_BASE}/gpt2-pytorch_model.bin",
    "config.json": f"{GPT2_BASE}/gpt2-config.json",
    "vocab.json": f"{GPT2_BASE}/gpt2-vocab.json",
    "merges.txt": f"{GPT2_BASE}/gpt2-merges.txt",
}

SST2_BASE = "https://raw.githubusercontent.com/clairett/pytorch-sentiment-classification/master/data/SST2"
SST2_FILES = {  # sentence<TAB>label(0/1), no header
    "sst2_train.tsv": f"{SST2_BASE}/train.tsv",
    "sst2_dev.tsv": f"{SST2_BASE}/dev.tsv",
    "sst2_test.tsv": f"{SST2_BASE}/test.tsv",
}

AGNEWS_BASE = "https://raw.githubusercontent.com/mhjabreel/CharCnn_Keras/master/data/ag_news_csv"
AGNEWS_FILES = {  # "class(1-4)","title","description", no header
    "agnews_train.csv": f"{AGNEWS_BASE}/train.csv",
    "agnews_test.csv": f"{AGNEWS_BASE}/test.csv",
}


def download(url, dest, force=False):
    if os.path.exists(dest) and not force and os.path.getsize(dest) > 0:
        print(f"  [skip] {os.path.relpath(dest, HERE)} ({os.path.getsize(dest)} bytes)")
        return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    print(f"  [get ] {url}")
    try:
        urllib.request.urlretrieve(url, dest)
    except Exception as e:  # noqa: BLE001
        print(f"\nFAILED to download {url}\n  -> {e}\n", file=sys.stderr)
        print(
            "If huggingface.co is blocked, this script deliberately avoids it. A failure here\n"
            "means the sandbox also blocks the GitHub/S3 mirrors. Add these hosts to the\n"
            "network allow-list: s3.amazonaws.com, raw.githubusercontent.com — then re-run.",
            file=sys.stderr,
        )
        sys.exit(1)
    print(f"         -> {os.path.relpath(dest, HERE)} ({os.path.getsize(dest)} bytes)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    print("Prefetching GPT-2 small (124M) weights + tokenizer ...")
    for name, url in GPT2_FILES.items():
        download(url, os.path.join(ASSETS, "gpt2", name), args.force)

    print("Prefetching SST-2 ...")
    for name, url in SST2_FILES.items():
        download(url, os.path.join(ASSETS, "data", name), args.force)

    print("Prefetching AG News ...")
    for name, url in AGNEWS_FILES.items():
        download(url, os.path.join(ASSETS, "data", name), args.force)

    print("\nDone. Assets are in ./assets — the main run is now fully offline.")


if __name__ == "__main__":
    main()
