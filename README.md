# flop-testnet-toolkit

Tools to participate in the [FLOP](https://flop.finance) testnet across the three
reward-bearing lanes — **miner**, **agent**, **validator** — sized to the published
tokenomics so effort goes where the allocation actually is.

> Status: pre-testnet. FLOP's testnet opens **Q4 2026 (~90 days)**, mainnet Q1 2027.
> The testnet API and miner client are not public yet — they land with the Yellow Paper
> and the @CryptoHayes AMA (~early Sep 2026). Everything here is built against the *known
> economics* and structured so wiring the real endpoint is a one-file change.

## Where the allocation is

Genesis airdrop = **3.5bn $FLOP (20.4% of supply)**, split by *economic work done on the
testnet* — not by chat activity, follower count, or engagement:

| Lane | Airdrop | Basis | Long-term upside |
|------|--------:|-------|------------------|
| **Miner** | up to 1.2bn (7.0%) | compute **delivered** | 51.2% of supply + 85% of every inference fee, liquid |
| **Agent** | up to 1.2bn (7.0%) | compute **consumed** — *3 $FLOP spent on inference → 1 airdropped* | demand-side subsidy bucket |
| **Validator** | 305.5mn (1.8%) | stake for the mainnet set | locked through first halving |
| Reserve | 794.5mn (4.6%) | ecosystem incentives | — |

Numbers are captured in [`data/tokenomics.json`](data/tokenomics.json) with their source and
the provisional-draft caveat. `python3 agent/economics_demo.py` reprints the airdrop math from
that file so any claim here is auditable.

**Takeaway:** the miner lane is the largest surface (biggest airdrop bucket *and* the majority
of long-term supply *and* the fee stream). The agent lane rewards spending your faucet balance
on real inference. Both reward *measurable compute*, so this toolkit is about being ready to
deliver and consume it on day one.

## Contents

- [`miner/`](miner/) — runbook + `provision.sh` that verifies a ≥16GB-VRAM GPU and stages a
  drop-in slot for the miner client.
- [`agent/inference_buyer.py`](agent/inference_buyer.py) — the agent lane: draw faucet balance,
  spend it on useful inference sessions, track spend → estimated airdrop unlock. Runs today in
  `--simulate`; wire `FlopClient` to the live endpoint when it ships.
- [`watch/testnet_watch.py`](watch/testnet_watch.py) — cron-able watcher that alerts the moment
  the faucet/testnet/miner-client goes live.
- [`data/tokenomics.json`](data/tokenomics.json) — the provisional numbers, with source.
- [`strategy.md`](strategy.md) — how to prioritise the lanes for maximum allocation.

## Quick start

```bash
# see the airdrop economics printed from the captured tokenomics
python3 agent/economics_demo.py

# model the agent spend->unlock lane end to end (no testnet needed yet)
python3 agent/inference_buyer.py --simulate --did did:key:demo

# verify a GPU host is miner-ready
bash miner/provision.sh

# watch for the testnet going live (cron: */3 * * * *)
python3 watch/testnet_watch.py
```

## Caveats

Figures are from a **v0.1 draft** teaser and are explicitly provisional. Nothing here is
financial advice. This repo does not automate sybil behaviour — FLOP's PoUI consensus slashes
null/dishonest work, so the only thing that pays is real compute delivered or consumed.

MIT licensed.
