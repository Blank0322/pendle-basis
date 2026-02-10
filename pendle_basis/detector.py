from __future__ import annotations

from dataclasses import dataclass

from .models import MarketSnapshot, ShockSignal


@dataclass
class DetectorConfig:
    min_tvl_usd: float = 1_000_000
    spread_bps_hi: float = 30
    impact_bps_hi: float = 120
    volume_tvl_ratio_hi: float = 0.25


class LiquidityShockDetector:
    def __init__(self, cfg: DetectorConfig | None = None):
        self.cfg = cfg or DetectorConfig()

    def score(self, s: MarketSnapshot) -> ShockSignal | None:
        if (s.tvl_usd or 0) < self.cfg.min_tvl_usd:
            return None

        score = 0.0
        reasons = []

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

        if s.implied_apy is not None:
            # lightweight nudge: extreme implied rates can be temporary dislocations
            if s.implied_apy >= 0.25:
                score += 1.0
                reasons.append(f"high implied APY ({s.implied_apy:.0%})")
            if s.implied_apy <= 0.02:
                score += 0.5
                reasons.append(f"low implied APY ({s.implied_apy:.0%})")

        if score <= 0:
            return None

        return ShockSignal(market=s.market, score=score, reason=", ".join(reasons), snapshot=s)
