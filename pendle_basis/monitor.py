from __future__ import annotations

import argparse
import os

import pandas as pd

from .analytics import compute_metrics
from .detector import LiquidityShockDetector
from .sources import MockSource, PendleApiSource
from .state import BasisState, update_basis_series


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--chain", default="ethereum")
    p.add_argument("--mock", action="store_true")
    p.add_argument("--top", type=int, default=5)
    p.add_argument("--out", default="output/watchlist.csv")
    args = p.parse_args()

    source = MockSource() if args.mock else PendleApiSource()
    detector = LiquidityShockDetector()
    state_store = BasisState(path="output/basis_state.json")

    state = state_store.load()

    snaps = source.fetch(chain=args.chain)
    signals = []
    rows = []
    for s in snaps:
        hist = state.get("series", {}).get(s.market, [])
        metrics = compute_metrics(s, history_basis=hist)

        # update series with current basis if available
        if metrics.basis is not None:
            update_basis_series(state, s.market, metrics.basis)

        sig = detector.score(s, history_basis=hist)
        if sig is not None:
            signals.append(sig)

        rows.append(
            {
                "market": s.market,
                "implied_apy": s.implied_apy,
                "underlying_apy": s.underlying_apy,
                "basis": metrics.basis,
                "basis_z": metrics.basis_z,
                "convexity_proxy": metrics.convexity_proxy,
                "whale_shock": metrics.whale_shock,
                "spread_bps": s.spread_bps,
                "impact_1k_bps": s.price_impact_1k_bps,
                "tvl_usd": s.tvl_usd,
                "vol24h_usd": s.volume_24h_usd,
                "signal_score": sig.score if sig else 0.0,
                "signal_reason": sig.reason if sig else "",
            }
        )

    signals.sort(key=lambda x: x.score, reverse=True)
    state_store.save(state)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    pd.DataFrame(rows).sort_values("signal_score", ascending=False).to_csv(args.out, index=False)

    if not signals:
        print("No shock-like signals found.")
        print(f"watchlist_csv: {args.out}")
        return

    print("\nTop signals:")
    for sig in signals[: max(args.top, 1)]:
        s = sig.snapshot
        print(
            f"- {sig.market}: score={sig.score:.2f} | {sig.reason} | "
            f"implied={s.implied_apy if s.implied_apy is not None else 'NA'} "
            f"underlying={s.underlying_apy if s.underlying_apy is not None else 'NA'}"
        )
    print(f"watchlist_csv: {args.out}")


if __name__ == "__main__":
    main()
