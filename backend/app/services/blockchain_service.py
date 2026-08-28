"""web3.py client for the local ReliefTracking smart contract. Reads the address + ABI
written by blockchain/scripts/deploy.js — run that first (see blockchain/README.md).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from web3 import Web3

DEPLOYMENT_PATH = Path(__file__).parent / "relief_tracking_deployment.json"
LOCAL_RPC_URL = "http://127.0.0.1:8545"


class BlockchainNotDeployedError(RuntimeError):
    pass


class ReliefTrackingClient:
    def __init__(self, rpc_url: str = LOCAL_RPC_URL) -> None:
        self._w3 = Web3(Web3.HTTPProvider(rpc_url))
        self._contract = None
        self._admin_account = None
        self._load_deployment()

    def _load_deployment(self) -> None:
        if not DEPLOYMENT_PATH.exists():
            return  # not deployed yet — endpoints will raise a clear error until it is
        with open(DEPLOYMENT_PATH) as f:
            deployment = json.load(f)
        self._contract = self._w3.eth.contract(address=deployment["address"], abi=deployment["abi"])
        # Hardhat's default first account is the contract deployer / admin.
        if self._w3.is_connected():
            self._admin_account = self._w3.eth.accounts[0]

    @property
    def is_ready(self) -> bool:
        return self._contract is not None and self._w3.is_connected()

    def _require_ready(self) -> None:
        if not self.is_ready:
            raise BlockchainNotDeployedError(
                "Contract not deployed or local Hardhat node not running. "
                "See blockchain/README.md: `npx hardhat node` then "
                "`npx hardhat run scripts/deploy.js --network localhost`."
            )

    def allocate(self, district: str, resource_type: str, quantity: int, recipient_org: str) -> dict:
        self._require_ready()
        tx_hash = self._contract.functions.allocate(
            district, resource_type, quantity, recipient_org
        ).transact({"from": self._admin_account})
        receipt = self._w3.eth.wait_for_transaction_receipt(tx_hash)
        event = self._contract.events.AllocationCreated().process_receipt(receipt)[0]
        return {"tx_hash": tx_hash.hex(), "allocation_id": event["args"]["id"]}

    def mark_dispatched(self, allocation_id: int) -> dict:
        self._require_ready()
        tx_hash = self._contract.functions.markDispatched(allocation_id).transact(
            {"from": self._admin_account}
        )
        self._w3.eth.wait_for_transaction_receipt(tx_hash)
        return {"tx_hash": tx_hash.hex()}

    def confirm_delivery(self, allocation_id: int) -> dict:
        self._require_ready()
        tx_hash = self._contract.functions.confirmDelivery(allocation_id).transact(
            {"from": self._admin_account}
        )
        self._w3.eth.wait_for_transaction_receipt(tx_hash)
        return {"tx_hash": tx_hash.hex()}

    def flag_discrepancy(self, allocation_id: int, reason: str) -> dict:
        self._require_ready()
        tx_hash = self._contract.functions.flagDiscrepancy(allocation_id, reason).transact(
            {"from": self._admin_account}
        )
        self._w3.eth.wait_for_transaction_receipt(tx_hash)
        return {"tx_hash": tx_hash.hex()}

    def get_ledger(self) -> list[dict[str, Any]]:
        self._require_ready()
        ids = self._contract.functions.getAllocationIds().call()
        status_names = ["Allocated", "Dispatched", "Delivered", "DiscrepancyFlagged"]
        ledger = []
        for allocation_id in ids:
            a = self._contract.functions.getAllocation(allocation_id).call()
            ledger.append(
                {
                    "id": a[0],
                    "district": a[1],
                    "resource_type": a[2],
                    "quantity": a[3],
                    "allocated_by": a[4],
                    "recipient_org": a[5],
                    "timestamp": a[6],
                    "status": status_names[a[7]],
                }
            )
        return ledger


# Module-level singleton, re-checks deployment file lazily via is_ready.
blockchain_client = ReliefTrackingClient()
