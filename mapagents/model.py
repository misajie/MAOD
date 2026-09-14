"""Deep Gravity predictor and semantic input-column weight transfer."""
from __future__ import annotations
from dataclasses import dataclass

import numpy as np
import torch
from torch import nn


class DeepGravity(nn.Module):
    def __init__(self, input_ids: list[str], hidden_sizes=None, dropout=0., backbone_input_ids=None):
        super().__init__()
        self.input_ids = list(input_ids)
        self.program_mode = backbone_input_ids is not None
        self.backbone_input_ids = list(backbone_input_ids if self.program_mode else input_ids)
        if not set(self.backbone_input_ids).issubset(input_ids):
            raise ValueError("A spatial correction cannot remove the DG backbone inputs")
        self.program_input_ids = [k for k in input_ids if k not in self.backbone_input_ids] if self.program_mode else []
        self.register_buffer("backbone_indices", torch.tensor([input_ids.index(k) for k in self.backbone_input_ids], dtype=torch.long), persistent=False)
        self.register_buffer("program_indices", torch.tensor([input_ids.index(k) for k in self.program_input_ids], dtype=torch.long), persistent=False)
        if self.program_mode:
            self.program_weights = nn.Parameter(torch.zeros(len(self.program_input_ids)))
        # Matches the checked-out DG implementation: five 256-wide layers,
        # followed by ten 128-wide layers, with LeakyReLU activations.
        self.hidden_sizes = list(hidden_sizes or ([256] * 5 + [128] * 10))
        self.dropout = float(dropout)
        sizes = [len(self.backbone_input_ids)] + self.hidden_sizes + [1]
        self.layers = nn.ModuleList([nn.Linear(a, b) for a, b in zip(sizes[:-1], sizes[1:])])
        self.activation = nn.LeakyReLU()
        self.drop = nn.Dropout(dropout)

    def backbone_scores(self, x):
        if self.program_mode: x = x.index_select(-1, self.backbone_indices)
        for layer in self.layers[:-1]: x = self.drop(self.activation(layer(x)))
        return self.layers[-1](x).squeeze(-1)

    def program_terms(self, x):
        if not self.program_mode:
            return x[..., :0]
        return x.index_select(-1, self.program_indices) * self.program_weights

    def forward(self, x):
        score = self.backbone_scores(x)
        if self.program_mode: score = score + self.program_terms(x).sum(-1)
        return score

    def transfer_from(self, parent: "DeepGravity") -> dict:
        if self.hidden_sizes != parent.hidden_sizes:
            raise ValueError("Warm start requires identical hidden-layer dimensions")
        shared = []
        previous = {name: i for i, name in enumerate(parent.backbone_input_ids)}
        with torch.no_grad():
            self.layers[0].weight.zero_()
            self.layers[0].bias.copy_(parent.layers[0].bias)
            for new_index, name in enumerate(self.backbone_input_ids):
                if name in previous:
                    self.layers[0].weight[:, new_index].copy_(parent.layers[0].weight[:, previous[name]])
                    shared.append(name)
            for new, old in zip(self.layers[1:], parent.layers[1:]):
                new.load_state_dict(old.state_dict())
            if self.program_mode and parent.program_mode:
                for j, key in enumerate(self.program_input_ids):
                    if key in parent.program_input_ids:
                        self.program_weights[j].copy_(parent.program_weights[parent.program_input_ids.index(key)])
        shared_inputs = set(self.input_ids) & set(parent.input_ids)
        return {"shared_columns": len(shared_inputs), "new_columns": len(self.input_ids) - len(shared_inputs),
                "dropped_columns": len(parent.input_ids) - len(shared_inputs),
                "all_weights_trainable": True, "additive_program_head": self.program_mode,
                "retained_program_columns": len(set(self.program_input_ids) & set(parent.program_input_ids))}


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
