#!/usr/bin/env bash
# Fetch full-precision GPT-2 family weights + tokenizer and arrange them as
# transformers-loadable directories (weights/dir_<model>/).
set -euo pipefail
cd "$(dirname "$0")"
BASE="https://s3.amazonaws.com/models.huggingface.co/bert"

for f in gpt2-vocab.json gpt2-merges.txt \
         gpt2-config.json distilgpt2-config.json gpt2-medium-config.json gpt2-large-config.json; do
  [ -f "$f" ] || curl -fSL -o "$f" "$BASE/$f"
done

for m in distilgpt2 gpt2 gpt2-medium gpt2-large; do
  [ -f "${m}-pytorch_model.bin" ] || curl -fSL -o "${m}-pytorch_model.bin" "$BASE/${m}-pytorch_model.bin"
  mkdir -p "dir_$m"
  ln -sf "../${m}-config.json"      "dir_$m/config.json"
  ln -sf "../${m}-pytorch_model.bin" "dir_$m/pytorch_model.bin"
  ln -sf "../gpt2-vocab.json"       "dir_$m/vocab.json"
  ln -sf "../gpt2-merges.txt"       "dir_$m/merges.txt"
done
echo "weights ready under weights/dir_<model>/"
