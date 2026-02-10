from __future__ import annotations

from pydantic import BaseModel, Field


class MarketSnapshot(BaseModel):
    ts: int
    chain: str = "ethereum"
    market: str
    pt_symbol: str | None = None
    yt_symbol: str | None = None

    # pricing-like fields (best-effort; depends on source)
    pt_price: float | None = None
    yt_price: float | None = None
    implied_apy: float | None = None

    # liquidity / microstructure proxies
    tvl_usd: float | None = None
    volume_24h_usd: float | None = None
    spread_bps: float | None = None
    price_impact_1k_bps: float | None = None


class ShockSignal(BaseModel):
    market: str
    score: float = Field(..., ge=0)
    reason: str
    snapshot: MarketSnapshot
