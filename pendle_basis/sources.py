from __future__ import annotations

import time
from dataclasses import dataclass

import requests

from .models import MarketSnapshot


@dataclass
class PendleApiSource:
    """Best-effort source using a public Pendle API.

    API surfaces change; this module is intentionally defensive.
    """

    base_url: str = "https://api.pendle.finance"
    timeout: int = 10

    def fetch(self, chain: str = "ethereum") -> list[MarketSnapshot]:
        # Try a few likely endpoints.
        endpoints = [
            f"{self.base_url}/core/v1/markets",
            f"{self.base_url}/core/v1/markets?chain={chain}",
            f"{self.base_url}/core/v2/markets?chain={chain}",
        ]
        last_err = None
        for url in endpoints:
            try:
                r = requests.get(url, timeout=self.timeout)
                if r.status_code != 200:
                    last_err = (url, r.status_code)
                    continue
                data = r.json()
                items = data.get("markets") or data.get("data") or data
                out: list[MarketSnapshot] = []
                ts = int(time.time())
                if isinstance(items, list):
                    for it in items:
                        # map loosely
                        out.append(
                            MarketSnapshot(
                                ts=ts,
                                chain=chain,
                                market=str(it.get("address") or it.get("market") or it.get("id") or it.get("name")),
                                pt_symbol=(it.get("ptSymbol") or it.get("pt") or None),
                                yt_symbol=(it.get("ytSymbol") or it.get("yt") or None),
                                tvl_usd=_to_float(it.get("tvl") or it.get("tvlUsd")),
                                volume_24h_usd=_to_float(it.get("volume24h") or it.get("volume24hUsd")),
                                implied_apy=_to_float(it.get("impliedApy") or it.get("apy")),
                                spread_bps=_to_float(it.get("spreadBps") or it.get("spread")),
                                price_impact_1k_bps=_to_float(it.get("priceImpact1kBps") or it.get("impactBps")),
                            )
                        )
                return out
            except Exception as e:
                last_err = (url, str(e))
                continue

        raise RuntimeError(f"Pendle API fetch failed: {last_err}")


def _to_float(x):
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None


class MockSource:
    def fetch(self, chain: str = "ethereum") -> list[MarketSnapshot]:
        ts = int(time.time())
        return [
            MarketSnapshot(
                ts=ts,
                chain=chain,
                market="PT-weETH-2026",
                pt_symbol="PT-weETH",
                yt_symbol="YT-weETH",
                implied_apy=0.18,
                tvl_usd=25_000_000,
                volume_24h_usd=3_500_000,
                spread_bps=18,
                price_impact_1k_bps=55,
            ),
            MarketSnapshot(
                ts=ts,
                chain=chain,
                market="PT-ezETH-2026",
                pt_symbol="PT-ezETH",
                yt_symbol="YT-ezETH",
                implied_apy=0.11,
                tvl_usd=8_000_000,
                volume_24h_usd=900_000,
                spread_bps=35,
                price_impact_1k_bps=140,
            ),
        ]
