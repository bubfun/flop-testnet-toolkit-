#!/usr/bin/env bash
# Provision a GPU host for the FLOP testnet miner lane.
# Sets up everything knowable before the miner client ships (Yellow Paper, ~early Sep 2026),
# so bringing the miner online on testnet day is a drop-in.
set -euo pipefail

MIN_VRAM_MB=16000
STAGE_DIR="${FLOP_MINER_HOME:-$HOME/flop-miner}"

say() { printf '\033[1;33m[flop-miner]\033[0m %s\n' "$*"; }
die() { printf '\033[1;31m[flop-miner] ERROR:\033[0m %s\n' "$*" >&2; exit 1; }

say "1/4 checking GPU + VRAM (need >= ${MIN_VRAM_MB} MB)"
command -v nvidia-smi >/dev/null 2>&1 || die "nvidia-smi not found — install the NVIDIA driver / run on a GPU host."
mapfile -t VRAM < <(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits)
[ "${#VRAM[@]}" -gt 0 ] || die "no GPU reported by nvidia-smi."
ok=0
for i in "${!VRAM[@]}"; do
  v="${VRAM[$i]//[[:space:]]/}"
  say "   GPU $i: ${v} MB VRAM"
  [ "$v" -ge "$MIN_VRAM_MB" ] && ok=1
done
[ "$ok" -eq 1 ] || die "no GPU meets the ${MIN_VRAM_MB} MB minimum. Rent a >=16GB card (RunPod/Vast/Lambda)."

say "2/4 checking CUDA runtime"
if command -v nvcc >/dev/null 2>&1; then nvcc --version | tail -1; else say "   nvcc absent (driver-only is fine for most inference runtimes; note it)"; fi

say "3/4 base dependencies"
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update -y >/dev/null && sudo apt-get install -y python3 python3-pip python3-venv git jq curl >/dev/null
fi
python3 -m venv "$STAGE_DIR/venv"
# shellcheck disable=SC1091
source "$STAGE_DIR/venv/bin/activate"
pip install -q --upgrade pip

say "4/4 staging drop-in slot at $STAGE_DIR"
mkdir -p "$STAGE_DIR"/{bin,logs,identity}
cat > "$STAGE_DIR/RUN_WHEN_CLIENT_SHIPS.md" <<'EOF'
# Drop-in checklist (fill once the FLOP miner client is released)
1. Place the miner binary/container in ./bin (or `docker pull` the published image).
2. Generate/register your miner DID (keep the private key in ./identity, chmod 600, never commit).
3. export FLOP_TESTNET_ENDPOINT=<from docs>   # published with the client
4. Start the miner pointed at the endpoint; confirm it appears in the miner set.
5. Keep uptime high — mainnet replaces the worst 50 of 1,000 miners monthly on availability.
EOF

say "DONE. GPU meets spec and the host is staged."
say "Next: run ../watch/testnet_watch.py to catch the client release, then follow"
say "      $STAGE_DIR/RUN_WHEN_CLIENT_SHIPS.md"
