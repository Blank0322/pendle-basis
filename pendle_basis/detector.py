from __future__ import annotations

from dataclasses import dataclass

from .analytics import compute_metrics, mean_reversion_score, trade_hint
from .models import MarketSnapshot, ShockSignal


@dataclass
class DetectorConfig:
    min_tvl_usd: float = 1_000_000
    spread_bps_hi: float = 30
    impact_bps_hi: float = 120
    volume_tvl_ratio_hi: float = 0.25
    basis_z_hi: float = 2.0


class LiquidityShockDetector:
    def __init__(self, cfg: DetectorConfig | None = None):
        self.cfg = cfg or DetectorConfig()

    def score(self, s: MarketSnapshot, history_basis: list[float] | None = None) -> ShockSignal | None:
        if (s.tvl_usd or 0) < self.cfg.min_tvl_usd:
            return None

        score = 0.0
        reasons = []

        # Microstructure stress
        if s.spread_bps is not None and s.spread_bps >= self.cfg.spread_bps_hi:
            score += min(2.0, s.spread_bps / self.cfg.spread_bps_hi)
            reasons.append(f"wide spread ({s.spread_bps:.0f} bps)")

        if s.price_impact_1k_bps is not None and s.price_impact_1k_bps >= self.cfg.impact_bps_hi:
            score += min(3.0, s.price_impact_1k_bps / self.cfg.impact_bps_hi)
            reasons.append(f"high impact@1k ({s.price_impact_1k_bps:.0f} bps)")

        if s.volume_24h_usd is not None and s.tvl_usd is not None and s.tvl_usd > 0:
            ratio = s.volume_24h_usd / s.tvl_usd
            if ratio >= self.cfg.volume_tvl_ratio_hi:
                score += min(2.0, ratio / self.cfg.volume_tvl_ratio_hi)
                reasons.append(f"volume/tvl spike ({ratio:.2f})")

        # Basis + convexity layer
        metrics = compute_metrics(s, history_basis=history_basis)
        score += mean_reversion_score(metrics)

        if metrics.basis is not None:
            reasons.append(f"basis={metrics.basis:.2%}")
        if metrics.basis_z is not None and abs(metrics.basis_z) >= self.cfg.basis_z_hi:
            reasons.append(f"basis {metrics.basis_z:.2f}σ")
        if metrics.convexity_proxy is not None:
            reasons.append(f"yt_convexity={metrics.convexity_proxy:.2f}")
        if metrics.whale_shock:
            reasons.append("whale-liquidity shock")

        hint = trade_hint(metrics)
        if hint != "insufficient basis data":
            reasons.append(hint)

        if score <= 0:
            return None

        return ShockSignal(market=s.market, score=float(score), reason=", ".join(reasons), snapshot=s)
