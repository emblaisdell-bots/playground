"""Phase 2: context distillation into a prefix-free (standalone) head.

The teacher is the best primed condition (by val). We record its soft predictions on the
train pool, then train a student head on COLD (C0) features to match those soft targets. The
student carries no prefix at inference -- it is the genuine standalone deliverable. We compare
it against an identical student trained on hard labels only.

Heads here are torch linear layers (softmax) so we can optimise a soft-target KL objective
that sklearn's LogisticRegression cannot express. Everything is head-only, so it stays cheap.
"""
import numpy as np
import torch
import torch.nn.functional as F


class LinearHead(torch.nn.Module):
    def __init__(self, in_dim, n_cls):
        super().__init__()
        self.fc = torch.nn.Linear(in_dim, n_cls)

    def forward(self, x):
        return self.fc(x)


def _standardise(Xtr, Xte):
    mu = Xtr.mean(axis=0, keepdims=True)
    sd = Xtr.std(axis=0, keepdims=True) + 1e-6
    return (Xtr - mu) / sd, (Xte - mu) / sd


def train_soft_student(X, soft_targets, Xtest, cfg, seed):
    """Train a standalone head to match soft targets (KL). Returns test-set predictions."""
    torch.manual_seed(seed)
    Xtr, Xte = _standardise(X.astype(np.float32), Xtest.astype(np.float32))
    xt = torch.from_numpy(Xtr)
    tgt = torch.from_numpy(soft_targets.astype(np.float32))
    T = cfg["distill"]["temperature"]
    model = LinearHead(xt.shape[1], tgt.shape[1])
    opt = torch.optim.Adam(model.parameters(), lr=cfg["distill"]["lr"])
    # soft targets are teacher probabilities; sharpen/soften by temperature then renormalise
    tgt_T = tgt.pow(1.0 / T)
    tgt_T = tgt_T / tgt_T.sum(dim=1, keepdim=True)
    for _ in range(cfg["distill"]["epochs"]):
        opt.zero_grad()
        logp = F.log_softmax(model(xt) / T, dim=1)
        loss = F.kl_div(logp, tgt_T, reduction="batchmean")
        loss.backward()
        opt.step()
    with torch.no_grad():
        pred = model(torch.from_numpy(Xte)).argmax(dim=1).numpy()
    return pred


def train_hard_student(X, y, Xtest, cfg, seed):
    """Identical architecture trained on hard labels only (the control for H4)."""
    torch.manual_seed(seed)
    Xtr, Xte = _standardise(X.astype(np.float32), Xtest.astype(np.float32))
    xt = torch.from_numpy(Xtr)
    yt = torch.from_numpy(y.astype(np.int64))
    n_cls = int(yt.max().item()) + 1
    model = LinearHead(xt.shape[1], n_cls)
    opt = torch.optim.Adam(model.parameters(), lr=cfg["distill"]["lr"])
    for _ in range(cfg["distill"]["epochs"]):
        opt.zero_grad()
        loss = F.cross_entropy(model(xt), yt)
        loss.backward()
        opt.step()
    with torch.no_grad():
        pred = model(torch.from_numpy(Xte)).argmax(dim=1).numpy()
    return pred
