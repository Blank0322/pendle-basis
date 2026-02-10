# Pendle Basis / Liquidity Shock Monitor

A small monitoring scaffold to detect **temporary mispricing** / **basis dislocations** around Pendle PT/YT markets.

The intuition:
- PT (Principal Token) ≈ discounted principal
- YT (Yield Token) ≈ leveraged exposure to yield (convexity)
- When a large trader hits shallow liquidity, short-term pricing can deviate from a more stable implied-rate baseline.

This repo is designed as a clean, extensible "research-to-monitor" pipeline:

```text
Data Source → Snapshot → Feature Engineering → Shock Detector → Alert
```

## What this MVP does

- Pulls market snapshots from a data source (default: Pendle public API if reachable)
- Computes simple implied-rate features (placeholder formulae where needed)
- Detects liquidity stress using *price impact / spread widening / volume spikes* heuristics
- Emits a ranked "watchlist" of markets worth manual review

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pendle_basis.monitor --mock
```

## Roadmap

- plug in on-chain swap events (Pendle router) for real large-trade detection
- add a persistent store (SQLite) and rolling baselines
- add alert sinks (Telegram / email)
