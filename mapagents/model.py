"""Deep Gravity predictor and semantic input-column weight transfer."""
from __future__ import annotations
from dataclasses import dataclass

import numpy as np
import torch
from torch import nn


class DeepGravity(nn.Module):
    def __init__(self, input_ids: list[str], hidden_sizes=None, dropout=0.):
        super().__init__()
        self.input_ids = list(input_ids)
        # Matches the checked-out DG implementation: five 256-wide layers,
        # followed by ten 128-wide layers, with LeakyReLU activations.
        self.hidden_sizes = list(hidden_sizes or ([256] * 5 + [128] * 10))
        self.dropout = float(dropout)
        sizes = [len(input_ids)] + self.hidden_sizes + [1]
        self.layers = nn.ModuleList([nn.Linear(a, b) for a, b in zip(sizes[:-1], sizes[1:])])
        self.activation = nn.LeakyReLU()
        self.drop = nn.Dropout(dropout)

    def forward(self, x):
        for layer in self.layers[:-1]: x = self.drop(self.activation(layer(x)))
        return self.layers[-1](x).squeeze(-1)

    def transfer_from(self, parent: "DeepGravity") -> dict:
        if self.hidden_sizes != parent.hidden_sizes:
            raise ValueError("Warm start requires identical hidden-layer dimensions")
        shared = []
        previous = {name: i for i, name in enumerate(parent.input_ids)}
        with torch.no_grad():
            self.layers[0].weight.zero_()
            self.layers[0].bias.copy_(parent.layers[0].bias)
            for new_index, name in enumerate(self.input_ids):
                if name in previous:
                    self.layers[0].weight[:, new_index].copy_(parent.layers[0].weight[:, previous[name]])
                    shared.append(name)
            for new, old in zip(self.layers[1:], parent.layers[1:]):
                new.load_state_dict(old.state_dict())
        return {"shared_columns": len(shared), "new_columns": len(self.input_ids) - len(shared),
                "dropped_columns": len(parent.input_ids) - len(shared),
                "all_weights_trainable": True}


@dataclass
class FeatureTransform:
    input_ids: list[str]
    mean: np.ndarray
    scale: np.ndarray

    @classmethod
    def fit(cls, values, input_ids, parent=None):
        values = np.asarray(values, dtype=np.float64)
        logged = np.sign(values) * np.log1p(np.abs(values))
        mean, scale = logged.mean(axis=0), logged.std(axis=0)
        scale = np.where(scale > 1e-30, scale, 1.)
        if parent is not None:
            previous = {k: i for i, k in enumerate(parent.input_ids)}
            for i, key in enumerate(input_ids):
                if key in previous:
                    mean[i], scale[i] = parent.mean[previous[key]], parent.scale[previous[key]]
        return cls(list(input_ids), mean, scale)

    def transform(self, values):
        values = np.asarray(values, dtype=np.float64)
        logged = np.sign(values) * np.log1p(np.abs(values))
        # Clipping is part of the saved feature transform, shared across stages.
        return np.clip((logged - self.mean) / self.scale, -20, 20).astype(np.float32)

    def to_dict(self):
        return {"input_ids": self.input_ids, "mean": self.mean.tolist(), "scale": self.scale.tolist(),
                "transform": "signed_log1p_then_train_standardization_clip20"}

    @classmethod
    def from_dict(cls, data):
        return cls(data["input_ids"], np.asarray(data["mean"]), np.asarray(data["scale"]))
