# Concepts

## Basis / implied APY

In Pendle-style fixed-yield markets, a convenient lens is the *implied rate* embedded in PT pricing.
Short-term shocks (large swaps, liquidity withdrawal) can widen spreads and create temporary mispricing.

## Why YT is convex

YT concentrates yield exposure; when rates move or liquidity thins, YT can behave like leveraged duration.
This makes it a useful surface for detecting dislocations (but also increases liquidation / execution risk).
