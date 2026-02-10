from __future__ import annotations

import argparse

from .detector import LiquidityShockDetector
from .sources import MockSource, PendleApiSource


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--chain", default="ethereum")
    p.add_argument("--mock", action="store_true")
    args = p.parse_args()

    source = MockSource() if args.mock else PendleApiSource()
    detector = LiquidityShockDetector()

    snaps = source.fetch(chain=args.chain)
    signals = [detector.score(s) for s in snaps]
    signals = [s for s in signals if s is not None]
    signals.sort(key=lambda x: x.score, reverse=True)

    if not signals:
        print("No shock-like signals found.")
        return

    print("\nTop signals:")
    for sig in signals:
        s = sig.snapshot
        print(
            f"- {sig.market}: score={sig.score:.2f} | {sig.reason} | tvl=${(s.tvl_usd or 0):,.0f} | vol24h=${(s.volume_24h_usd or 0):,.0f}"
        )


if __name__ == "__main__":
    main()
