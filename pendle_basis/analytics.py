from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .models import MarketSnapshot


@dataclass(frozen=True)
class BasisMetrics:
    basis: float | None
    basis_z: float | None
    convexity_proxy: float | None
    whale_shock: bool


def compute_metrics(s: MarketSnapshot, history_basis: list[float] | None = None) -> BasisMetrics:
    history_basis = history_basis or []

    basis = None
    if s.implied_apy is not None and s.underlying_apy is not None:
        basis = float(s.implied_apy - s.underlying_apy)

    basis_z = None
    if basis is not None and len(history_basis) >= 20:
        arr = np.asarray(history_basis[-120:], dtype=float)
        std = float(np.std(arr, ddof=1)) if arr.size > 2 else 0.0
        if std > 1e-10:
            basis_z = float((basis - float(np.mean(arr))) / std)

    convexity_proxy = None
    if s.yt_price is not None and s.pt_price is not None and s.pt_price > 0:
        # rough convexity proxy: YT/PT ratio deviation
        convexity_proxy = float((s.yt_price / s.pt_price) - 1.0)

    whale_shock = False
    if s.price_impact_1k_bps is not None and s.price_impact_1k_bps >= 120:
        whale_shock = True
    if s.spread_bps is not None and s.spread_bps >= 30:
        whale_shock = True
    if s.volume_24h_usd is not None and s.tvl_usd is not None and s.tvl_usd > 0:
        if (s.volume_24h_usd / s.tvl_usd) >= 0.25:
            whale_shock = True

    return BasisMetrics(
        basis=basis,
        basis_z=basis_z,
        convexity_proxy=convexity_proxy,
        whale_shock=whale_shock,
    )


def mean_reversion_score(m: BasisMetrics) -> float:
    s = 0.0
    if m.basis_z is not None:
        s += min(4.0, abs(m.basis_z) / 2.0)
    if m.whale_shock:
        s += 2.0
    if m.convexity_proxy is not None and abs(m.convexity_proxy) >= 0.2:
        s += 1.0
    return float(s)


def trade_hint(m: BasisMetrics) -> str:
    if m.basis is None:
        return "insufficient basis data"
    # if implied too rich vs underlying and shock occurred -> fade richness
    if m.basis > 0:
        return "watch: implied APY rich vs underlying; consider mean-reversion fade after liquidity shock"
    return "watch: implied APY cheap vs underlying; wait for normalization trigger"
