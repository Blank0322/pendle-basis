# Concepts

## Basis / implied APY

Core spread:

- `basis = implied_apy - underlying_apy`

A large positive basis can imply "implied is too rich" vs underlying carry; a large negative basis can imply the opposite.

In this repo, we keep a rolling series and compute:

- `basis_z = (basis - mean) / std`

to detect non-linear dislocation (`|basis_z| >= 2` as a strong deviation signal).

## Why YT is convex

YT concentrates yield exposure; when rates move or liquidity thins, YT can behave like leveraged duration.
This makes it a useful surface for dislocation capture, but also increases execution/liquidation risk.

A practical proxy used here:

- `convexity_proxy = yt_price / pt_price - 1`

## Whale liquidity shock proxy

We cannot reliably identify wallets in this MVP, so we use microstructure proxies:

- high `price_impact_1k_bps`
- wide `spread_bps`
- high `volume_24h / tvl`

When shock proxy + basis z-score are both elevated, we rank as potential mean-reversion setup.
