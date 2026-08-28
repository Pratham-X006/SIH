# Blockchain Architecture — SETU

## Why blockchain exists here at all

Relief distribution during a flood involves multiple **independent organizations** — a
district administration, one or more NGOs, one or more warehouse operators — none of which
fully trusts another party's private database. If a warehouse's own system says "we sent
5,000kg" and the only record of that is the warehouse's own mutable database, an NGO or
auditor has no independent way to confirm that record hasn't been edited after the fact.
That is a genuine multi-party trust problem, and a shared, tamper-evident, jointly-witnessed
log measurably helps it. **This is the only reason blockchain is used in SETU.**

## Why NOT PostgreSQL for everything

PostgreSQL (this build: SQLite, see `LIMITATIONS.md`) remains the system of record for
everything that is *not* a multi-party trust problem: user accounts, inventory levels,
GIS/impact numbers, ML predictions, priority scores. Putting those on-chain would be
technically unjustified — they're single-party-authoritative data with no cross-org dispute
to resolve, and a blockchain is slower and more expensive to write to than a normal database
for no corresponding benefit. Concretely in this codebase: `backend/app/db/models.py` (the
operational database) holds full allocation records including quantities recommended vs.
dispatched vs. received and the reasoning behind an allocation choice; only the allocation
**lifecycle events** (`allocate`, `dispatch`, `confirm_delivery`, `flag_discrepancy`) are
also written to the chain, via `backend/app/services/blockchain_service.py`.

## What's on-chain vs. off-chain

**On-chain** (`blockchain/contracts/ReliefTracking.sol`): allocation id, district, resource
type, quantity, allocating address, recipient org name, timestamp, and a status enum
(Allocated/Dispatched/Delivered/DiscrepancyFlagged). No personal/beneficiary data, no GIS
geometry, no model internals.

**Off-chain** (SQLite/PostgreSQL): everything else — the allocation's full reasoning string,
distance/accessibility figures, the requirement calculation that justified the quantity, the
discrepancy record (expected/received/difference/resolution), user accounts, and the audit
log. `backend/app/db/models.py::BlockchainTransaction` is a fast-query mirror of on-chain
events (tx hash + event type + timestamp) so the audit API doesn't need to hit the chain RPC
for every dashboard list view — the chain itself remains the source of truth for those events.

## Why quantity comparison happens off-chain, not on-chain

The contract does not compare dispatched vs. received quantities — it only records whichever
assertion the backend tells it to record (`confirmDelivery` or `flagDiscrepancy`). The
comparison (`backend/app/api/routes/deliveries.py::confirm_delivery`) happens in the backend
*before* calling the chain, because **blockchain does not verify that input data is true** —
it only guarantees that whatever was written cannot be silently altered afterward. Concretely:
if a warehouse dispatches 5,000kg and a relief centre confirms receiving 4,250kg, the backend
computes the 750kg difference, creates a `Discrepancy` row, and calls `flagDiscrepancy` with
that reason — the chain records "a discrepancy was flagged, by whom, when," not an
independent verification that either number is correct.

## Platform: local Hardhat (Solidity), and why

The frozen implementation spec (`docs/SETU_Frozen_Implementation_Spec.md`, Phase 11) set up
a timeboxed decision gate between Hyperledger Fabric (architecturally closer to a
permissioned, identity-bound, government-consortium fit — see the masterplan's comparison
table) and a Solidity/Hardhat fallback. **This codebase already contains the Hardhat
fallback, fully implemented and tested** (`blockchain/test/ReliefTracking.test.js`, 4 passing
tests) — Fabric was not attempted in this build. This is the honest state to present: Fabric
remains the documented target for a production, multi-organization-governed deployment (see
"Production path" below); what's actually running is a real Solidity contract on a real
local chain.

## Current network: local Hardhat node, single admin key

`blockchain/hardhat.config.js` configures a `localhost` network at `http://127.0.0.1:8545`
(via `npx hardhat node`). The contract's `onlyAdmin` modifier means a single Ethereum account
(Hardhat's default first account) is authorized to call every state-changing function —
there is no on-chain distinction yet between a District Admin, an NGO, and a Warehouse
identity. Off-chain RBAC (JWT + role checks in `backend/app/auth/deps.py`) governs who can
trigger which *API call*, but that authorization is not yet mirrored on-chain per-organization.

## Production path (not built, documented as the target)

A permissioned/consortium network — Hyperledger Fabric (each org runs its own peer, MSP-based
identity, channel-scoped visibility) or a private/permissioned EVM deployment with
per-organization signing keys — is the architecturally correct target once real government/
NGO/warehouse organizations are actual participants, because at that point participant
identity, data-sensitivity, and governance genuinely matter in a way a single admin key on a
local chain cannot represent. This is future production scope, not implemented here.

## Verified in this session

- `npx hardhat test` → 4/4 passing (allocate→dispatch→deliver lifecycle, discrepancy
  flagging, non-admin rejection, skip-order rejection).
- `npx hardhat node` + `npx hardhat run scripts/deploy.js --network localhost` → real
  deployment, contract address written to `backend/app/services/relief_tracking_deployment.json`.
- A full scenario run against the live chain produced 6 real on-chain transactions
  (2× allocate, 2× dispatch, 1× confirm_delivery, 1× flag_discrepancy), confirmed via
  `GET /api/audit/blockchain/transactions` returning real tx hashes.
