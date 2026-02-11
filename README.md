# Pendle Basis (LST/LRT Yield Curve + Whale Shock Mean Reversion)

This repo targets the exact setup:

- decompose LST/LRT yield curve
- measure **Implied APY vs Underlying APY** dislocation (Basis)
- use **YT convexity proxy** + **liquidity shock** to rank mean-reversion opportunities

## Signal framework

```text
Market Snapshot
  -> Basis = Implied APY - Underlying APY
  -> Basis z-score (rolling state)
  -> YT convexity proxy (YT/PT ratio)
  -> Whale shock proxy (impact, spread, volume/tvl)
  -> Mean-reversion score + trade hint
```

## Current implementation

- `pendle_basis/analytics.py`
  - `compute_metrics(...)` -> basis / basis_z / convexity_proxy / whale_shock
  - `mean_reversion_score(...)`
  - `trade_hint(...)`
- `pendle_basis/detector.py`
  - combines microstructure stress + basis/convexity layer
- `pendle_basis/state.py`
  - rolling basis state persistence (`output/basis_state.json`)
- `pendle_basis/monitor.py`
  - end-to-end watchlist build + CSV export (`output/watchlist.csv`)

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_watch.py --mock --top 5
```

Output:
- terminal top signals
- `output/watchlist.csv`
- `output/basis_state.json`

## Notes

- This is a research/ranking engine, not an execution bot.
- API fields across Pendle endpoints can change; source mapping is defensive by design.
