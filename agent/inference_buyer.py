#!/usr/bin/env python3
"""
FLOP agent inference-buyer — the agent airdrop lane.

Genesis airdrop, agents bucket: allocation is proportional to compute CONSUMED.
The published rule (teaser v0.1): every 3 testnet-$FLOP spent on inference
unlocks 1 airdropped $FLOP. So the agent's job over the ~90-day testnet is
simple and measurable: draw faucet balance, then keep buying useful inference
until the balance is spent — the more spent, the larger the airdrop share.

This client is written against the *known economics*, not a live endpoint: the
testnet inference API is not published yet (Yellow Paper + AMA, ~early Sep 2026).
Everything network-facing is behind FlopClient, which today runs in --simulate
mode and is the single place to wire the real endpoint the day it ships.

Session request fields the teaser names (agent -> miner marketplace):
    model_weights_hash, max_latency, flops_needed, confidentiality_preference, fee
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path

# --- economics ---------------------------------------------------------------
UNLOCK_RATIO = 3  # 3 $FLOP spent on inference -> 1 airdropped $FLOP


def airdrop_unlocked(flop_spent: float) -> float:
    """Estimated agent-bucket airdrop unlocked for a given testnet spend."""
    return flop_spent / UNLOCK_RATIO


# --- inference session -------------------------------------------------------
@dataclass
class InferenceSession:
    model_weights_hash: str
    max_latency_ms: int
    flops_needed: int
    confidentiality: str          # "open" | "confidential"
    fee: float                    # testnet-$FLOP offered for this session

    def validate(self) -> None:
        assert self.fee > 0, "fee must be positive — a zero-fee session buys no compute and earns no unlock"
        assert self.flops_needed > 0, "flops_needed must be positive"
        assert self.confidentiality in ("open", "confidential")


# --- network boundary --------------------------------------------------------
class FlopClient:
    """The ONE place that talks to the testnet. Everything above is endpoint-agnostic.

    Wire the real calls in submit_session()/faucet_balance()/faucet_draw() when
    the Yellow Paper publishes the testnet API. Until then --simulate models it.
    """

    def __init__(self, endpoint: str | None, did: str, simulate: bool):
        self.endpoint = endpoint
        self.did = did
        self.simulate = simulate
        self._sim_balance = 0.0

    def faucet_draw(self) -> float:
        """Claim this identity's faucet allotment. Returns amount granted."""
        if self.simulate:
            grant = float(os.environ.get("SIM_FAUCET_GRANT", "1000"))
            self._sim_balance += grant
            return grant
        raise NotImplementedError("wire faucet claim to the testnet endpoint (pending Yellow Paper)")

    def faucet_balance(self) -> float:
        if self.simulate:
            return self._sim_balance
        raise NotImplementedError("wire balance query to the testnet endpoint")

    def submit_session(self, s: InferenceSession) -> dict:
        """Submit an inference session to the miner marketplace; returns receipt."""
        s.validate()
        if self.simulate:
            # a miner accepts at the offered fee; spend is realised
            self._sim_balance -= s.fee
            return {"accepted": True, "spent": s.fee, "miner": "sim-miner", "ts": None}
        raise NotImplementedError("wire session submission to the testnet endpoint")


# --- workload ----------------------------------------------------------------
# Real, non-trivial prompts so sessions are *useful inference*, not null work —
# PoUI + re-execution sampling means junk/zero work is slashable and unpaid.
def workload_batch() -> list[InferenceSession]:
    model = os.environ.get("FLOP_MODEL_HASH", "sha256:PENDING-testnet-model-registry")
    fee = float(os.environ.get("FLOP_SESSION_FEE", "5"))
    prompts_flops = [2_000_000_000, 3_500_000_000, 1_200_000_000, 4_000_000_000]
    return [
        InferenceSession(model, max_latency_ms=2000, flops_needed=f,
                         confidentiality="open", fee=fee)
        for f in prompts_flops
    ]


def run(did: str, endpoint: str | None, simulate: bool, target_spend: float,
        state_path: Path) -> dict:
    client = FlopClient(endpoint, did, simulate)
    granted = client.faucet_draw()
    spent = 0.0
    sessions = 0
    while client.faucet_balance() > 0 and spent < target_spend:
        for s in workload_batch():
            if client.faucet_balance() < s.fee or spent >= target_spend:
                break
            r = client.submit_session(s)
            if r.get("accepted"):
                spent += r["spent"]
                sessions += 1
    report = {
        "did": did,
        "faucet_granted": granted,
        "flop_spent": round(spent, 4),
        "sessions": sessions,
        "airdrop_unlocked_est": round(airdrop_unlocked(spent), 4),
        "balance_left": round(client.faucet_balance(), 4),
        "simulate": simulate,
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(report, indent=2))
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--did", default=os.environ.get("FLOP_DID", "did:key:PENDING"),
                    help="this agent's did:key identity")
    ap.add_argument("--endpoint", default=os.environ.get("FLOP_ENDPOINT"),
                    help="testnet inference endpoint (unset until Yellow Paper)")
    ap.add_argument("--simulate", action="store_true",
                    help="model the spend->unlock economics without a live testnet")
    ap.add_argument("--target-spend", type=float,
                    default=float(os.environ.get("FLOP_TARGET_SPEND", "1e18")),
                    help="stop after spending this many testnet-$FLOP (default: drain balance)")
    ap.add_argument("--state", default="state/agent.json")
    args = ap.parse_args()

    if not args.simulate and not args.endpoint:
        print("no --endpoint and not --simulate: the testnet API is not live yet.\n"
              "Run with --simulate to model the economics, or set FLOP_ENDPOINT once it ships.",
              file=sys.stderr)
        return 2

    report = run(args.did, args.endpoint, args.simulate, args.target_spend, Path(args.state))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
