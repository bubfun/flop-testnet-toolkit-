# Maximising FLOP airdrop allocation

The airdrop is scored by **measurable compute**, so allocation is won by *doing the
work the network measures* — not by presence or engagement. Priority order, highest
expected allocation first.

## 1. Miner — highest EV, do this first
Largest airdrop bucket (up to 1.2bn) *and* the majority of long-term supply (51.2%) *and*
85% of every inference fee. Barrier is a ≥16GB-VRAM GPU, which can be rented for the
testnet window at ~$0.20–0.50/hr.

- Apply: `flop.finance/apply/miner` (region, equipment, "Testnet" timeline).
- Provision: `miner/provision.sh` on a rented GPU box.
- Day one: register the miner DID, serve inference, keep uptime high (mainnet churns the
  worst 50 of 1,000 monthly). Reputation built on testnet carries into the fee stream.

## 2. Agent — the spend lane
Same bucket size (up to 1.2bn). Rule: **3 testnet-$FLOP spent on inference → 1 airdropped**.
So the play is: draw the faucet allotment, then spend all of it on *useful* inference over
the testnet. Allocation scales with total spend.

- `agent/inference_buyer.py` drains a faucet balance into sessions and tracks the estimated
  unlock. It runs `--simulate` today; the endpoint wires in when the API ships.
- PoUI slashes null work — sessions must be real inference, so the workload batch uses
  genuine prompts, not empty calls.

## 3. Validator — only if hardware is already there
Smallest bucket (305mn) and locked through the first halving. Needs 8-core / 64GB / 2TB
NVMe / 1Gbps, capped at 1,000 validators. Worth it only if you already run a box that
meets spec; otherwise the miner lane returns more per dollar.

- Apply: `flop.finance/apply/validator` (keeps the option open at no cost).

## 4. Community
Follow @flop_labs (baseline eligibility) and attend the @CryptoHayes AMA — the AMA
publishes the final Yellow Paper with the exact testnet date, scoring, and client, which
resets the specifics above.

## Timeline to act against
- **~early Sep 2026** — AMA + Yellow Paper. Re-check every number here against it.
- **Q4 2026 (~90 days)** — testnet. The whole airdrop is earned in this window.
- **Q1 2027** — mainnet.

Run `watch/testnet_watch.py` on cron so the testnet-open signal isn't missed.
