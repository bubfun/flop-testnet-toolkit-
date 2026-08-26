# FLOP miner lane — runbook

The miner bucket is the largest single reward surface in FLOP: **up to 1.2bn $FLOP
of the genesis airdrop (7.0% of supply), proportional to compute delivered over the
~90-day testnet** — *and*, on mainnet, **51.2% of total supply** in block rewards plus
**85% of every inference fee, paid liquid with no lockup**. If you run one lane, run
this one.

## What a miner does
Serves inference. Agents post sessions (model-weights hash, max latency, FLOPs, fee);
a miner accepts, runs the inference inside a **TEE**, and returns a **TOPLOC** work
certificate. Consensus is **Proof-of-Useful-Inference**: validators re-execute a random
sample and slash dishonest or null work. So the reward is for *real* served compute, not
uptime alone.

## Hardware
Minimum: **a single GPU with ≥16GB VRAM** — a consumer card qualifies (listed alongside
A100/H100/H200/B200/GB200). Testnet is the cheap window to build reputation before the
mainnet fee stream turns on.

Rent, don't buy, for the testnet: RunPod / Vast.ai / Lambda spot instances with a 16–24GB
card run roughly **$0.20–0.50/hr**. A full 90-day testnet at $0.35/hr ≈ **$755** if run
continuously; in practice you size runtime to the reward curve once the AMA publishes it.

## Readiness steps (do now, before testnet)
1. `flop.finance/apply/miner` — submit the interest form (region, equipment, count,
   "Testnet" timeline). No cost, no wallet, whitelists you for testnet access.
2. Provision a GPU box and run `provision.sh` — it verifies CUDA + ≥16GB VRAM and stages
   a drop-in slot for the miner client.
3. Watch for the client release (`../watch/testnet_watch.py`).
4. On release: drop the FLOP miner binary/image in, register your miner DID, point it at
   the testnet, and keep uptime high (mainnet churns the worst 50 of 1,000 monthly).

## What is NOT known yet (pending Yellow Paper + AMA, ~early Sep 2026)
- The miner client itself (binary/container, registration flow).
- Exact reward curve and how "compute delivered" is normalised across GPU classes.
- TEE attestation requirements per GPU model.

`provision.sh` sets up everything that is knowable now so day-one is a drop-in.
