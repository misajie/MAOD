"""Shared, JSON-serializable interfaces for the MapAgents pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class ODData:
    """Zone order is authoritative for all feature and OD array axes.

    zones: zone_id, region_id, longitude, latitude, area_km2.
    flows: origin, destination, flow; only internal region edges are retained.
    base_features: zone_id index, named numeric columns.
    splits: train/validation/test lists of region identifiers.
    """

    zones: pd.DataFrame
    flows: pd.DataFrame
    base_features: pd.DataFrame
    splits: dict[str, list[str]]
    metadata: dict[str, Any]
    root: Path | None = None

    def region_ids(self, split: str) -> list[str]:
        return list(self.splits[split])

    def region_zones(self, region_id: str) -> pd.DataFrame:
        return self.zones.loc[self.zones.region_id.astype(str).eq(str(region_id))]


@dataclass
class FeatureBundle:
    """Compiled columns in the exact ODData.zones order.

    pair_specs contain JSON expression trees, evaluated on demand by the
    compiler's pair_features(bundle, origins, destinations, distances_km).
    zone_values provides named arrays needed by pairwise expressions.
    """

    origin: np.ndarray
    destination: np.ndarray
    origin_ids: list[str]
    destination_ids: list[str]
    pair_specs: list[dict[str, Any]] = field(default_factory=list)
    pair_ids: list[str] = field(default_factory=list)
    zone_values: dict[str, np.ndarray] = field(default_factory=dict)
    report: dict[str, Any] = field(default_factory=dict)

    @property
    def input_ids(self) -> list[str]:
        return (["origin:" + v for v in self.origin_ids]
                + ["destination:" + v for v in self.destination_ids]
                + ["distance_km"]
                + ["pair:" + v for v in self.pair_ids])
