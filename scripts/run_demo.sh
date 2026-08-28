#!/usr/bin/env bash
# One-command demo bring-up (Section 77). Starts the backend + local blockchain in the
# background, deploys the contract, seeds synthetic data, trains the model, and runs the
# full scenario walkthrough. Intended for git-bash/WSL/macOS/Linux.
#
# Usage: bash scripts/run_demo.sh
# Stop everything afterward with: kill $(cat .demo_pids)

set -euo pipefail
cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"
PYTHON="${SETU_PYTHON:-python}"
PID_FILE="$REPO_ROOT/.demo_pids"
: > "$PID_FILE"

cleanup_on_error() {
  echo "Something failed — leaving already-started processes running so you can inspect logs."
  echo "Stop them with: kill \$(cat $PID_FILE)"
}
trap cleanup_on_error ERR

echo "== Starting local Hardhat blockchain =="
(cd blockchain && npx hardhat node > ../.hardhat_node.log 2>&1 &)
sleep 3
HARDHAT_PID=$(pgrep -f "hardhat node" | head -1 || true)
[ -n "$HARDHAT_PID" ] && echo "$HARDHAT_PID" >> "$PID_FILE"

echo "== Deploying ReliefTracking contract =="
(cd blockchain && npx hardhat run scripts/deploy.js --network localhost)

echo "== Starting backend (FastAPI) =="
(cd backend && "$PYTHON" -m uvicorn app.main:app --port 8000 > ../.backend.log 2>&1 &)
sleep 2
BACKEND_PID=$(pgrep -f "uvicorn app.main:app" | head -1 || true)
[ -n "$BACKEND_PID" ] && echo "$BACKEND_PID" >> "$PID_FILE"

echo "== Waiting for backend to respond =="
for i in $(seq 1 20); do
  if curl -sf http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo "Backend is up."
    break
  fi
  sleep 1
done

echo "== Preparing demo data + model =="
"$PYTHON" scripts/prepare_demo.py || echo "(prepare_demo.py reported warnings — continuing anyway)"

echo "== Running full demo scenario =="
"$PYTHON" scripts/run_demo_scenario.py

echo ""
echo "Backend running at http://127.0.0.1:8000 (docs at /docs)."
echo "Run the dashboard yourself in another terminal: cd dashboard && streamlit run app.py"
echo "Stop background services with: kill \$(cat $PID_FILE)"
