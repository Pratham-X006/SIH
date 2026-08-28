# Blockchain module — Relief Tracking

`ReliefTracking.sol` was verified to compile cleanly against real solc 0.8.24 (functions,
ABI, and bytecode all generated successfully). `npx hardhat compile`/`test` could not be run
end-to-end inside the sandboxed container this was authored in, because Hardhat downloads
the Solidity compiler binary from `binaries.soliditylang.org` at compile time, and that host
is outside this sandbox's network allowlist (confirmed error: `HH502` / `403 Host not in
allowlist`). This is a property of that build environment only.

**Run for real on your machine (or once your project folder is connected):**

```bash
npm install
npx hardhat compile        # downloads the real compiler, works on a normal machine
npx hardhat test           # runs test/ReliefTracking.test.js — 4 tests covering the full
                            # allocate -> dispatch -> deliver/flag lifecycle + access control
npx hardhat node            # starts a local chain on 127.0.0.1:8545 (keep running)
npx hardhat run scripts/deploy.js --network localhost   # in a second terminal
```

Deploying writes `backend/app/services/relief_tracking_deployment.json` (contract address +
ABI) so the FastAPI backend's `web3.py` client can talk to it immediately — no manual wiring
needed after deploy.
