#!/usr/bin/env python3
"""Reprint the FLOP airdrop economics from data/tokenomics.json so every number
in the README is auditable against its source. No network, no side effects."""
from __future__ import annotations

import json
from pathlib import Path

from inference_buyer import airdrop_unlocked, UNLOCK_RATIO

DATA = Path(__file__).resolve().parent.parent / "data" / "tokenomics.json"


def main() -> None:
    t = json.loads(DATA.read_text())
    ga = t["genesis_airdrop"]
    print(f"source: {t['_source']}\n")
    print(f"total supply @ yr10 : {t['total_supply_year10']:,} $FLOP")
    print(f"genesis airdrop     : {ga['total']:,} $FLOP "
          f"({ga['total']/t['total_supply_year10']*100:.1f}% of supply)\n")
    print("airdrop buckets:")
    for name, b in ga["buckets"].items():
        print(f"  {name:11} up to {b['max_tokens']:>13,}  ({b['pct_supply']:.1f}% of supply)  — {b['basis']}")
    print(f"\nagent unlock rule: {UNLOCK_RATIO} testnet-$FLOP spent -> 1 airdropped $FLOP")
    for spend in (1_000, 10_000, 100_000):
        print(f"  spend {spend:>8,} -> ~{airdrop_unlocked(spend):>10,.0f} $FLOP unlocked (est.)")


if __name__ == "__main__":
    main()
