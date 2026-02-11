from __future__ import annotations

import json
import os
from dataclasses import dataclass


@dataclass
class BasisState:
    path: str = "output/basis_state.json"

    def load(self) -> dict:
        if not os.path.exists(self.path):
            return {"series": {}}
        with open(self.path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return {"series": {}}

    def save(self, state: dict) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)


def update_basis_series(state: dict, market: str, basis: float, keep_last: int = 240) -> list[float]:
    series = state.setdefault("series", {}).setdefault(market, [])
    series.append(float(basis))
    if len(series) > keep_last:
        del series[: len(series) - keep_last]
    return series
