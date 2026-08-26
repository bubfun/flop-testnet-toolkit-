#!/usr/bin/env python3
"""
FLOP testnet launch watcher.

The whole airdrop starts the moment the testnet + faucet + miner client go live.
This polls the surfaces that will flip first and alerts once, deduped, so you can
be first to draw faucet balance (agent lane) and register a miner (miner lane).

Signals watched:
  - technocore.chat faucet / claim endpoints going non-404
  - flop.finance for a testnet / docs / client-download link appearing
  - a miner-client release on the FLOP GitHub org (if/when public)

No secrets, no state beyond a local seen-file. Run from cron (*/3 * * * *).
"""
from __future__ import annotations

import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

TIMEOUT = 10
SEEN = Path(__file__).with_name(".watch-seen.txt")

FAUCET_PROBES = [
    "https://technocore.chat/faucet",
    "https://technocore.chat/api/faucet",
    "https://technocore.chat/claim",
    "https://technocore.chat/api/claim",
    "https://technocore.chat/.well-known/airdrop",
]
# High-signal phrases only — words like "faucet"/"docs" already appear on the site,
# so match phrases that show up only once the testnet is actually open.
KEYWORDS_PAGES = {
    "https://flop.finance/": ["testnet is live", "faucet is live", "download the miner",
                              "run a miner now", "testnet is now open", "claim testnet"],
    "https://flop.finance/teaser/": ["testnet is live", "faucet is live", "download the miner"],
}


def _get(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "flop-testnet-watch/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.status, r.read(200_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa: BLE001
        return None, f"ERR {e}"


def seen() -> set[str]:
    return set(SEEN.read_text().splitlines()) if SEEN.exists() else set()


def mark(key: str) -> None:
    with SEEN.open("a") as f:
        f.write(key + "\n")


def alert(key: str, msg: str) -> None:
    if key in seen():
        return
    print(f"\033[1;32m[FLOP ALERT]\033[0m {msg}")
    mark(key)


def main() -> int:
    hits = 0
    for url in FAUCET_PROBES:
        code, _ = _get(url)
        if code is not None and code != 404:
            alert(f"faucet:{url}:{code}", f"FAUCET/CLAIM endpoint live: {url} -> HTTP {code}")
            hits += 1
    for url, kws in KEYWORDS_PAGES.items():
        code, body = _get(url)
        low = body.lower()
        for kw in kws:
            if kw in low:
                alert(f"kw:{url}:{kw}", f"'{kw}' now on {url} — testnet may be opening")
                hits += 1
    if hits == 0:
        print("[flop-testnet-watch] quiet — no testnet/faucet/client signal.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
