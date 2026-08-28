// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title ReliefTracking
/// @notice Records every relief-resource allocation as an immutable, publicly verifiable
/// transaction, so NGOs, government, and the public can audit distribution end to end.
/// Lifecycle: Allocated -> Dispatched -> (Delivered | DiscrepancyFlagged)
contract ReliefTracking {
    enum Status {
        Allocated,
        Dispatched,
        Delivered,
        DiscrepancyFlagged
    }

    struct Allocation {
        uint256 id;
        string district;
        string resourceType; // e.g. "food_kg", "water_litres", "medical_kits", "shelter_units"
        uint256 quantity;
        address allocatedBy;
        string recipientOrg; // NGO / government body name
        uint256 timestamp;
        Status status;
    }

    address public admin;
    uint256 private nextId = 1;
    mapping(uint256 => Allocation) public allocations;
    uint256[] public allocationIds;

    event AllocationCreated(
        uint256 indexed id, string district, string resourceType, uint256 quantity, string recipientOrg
    );
    event AllocationDispatched(uint256 indexed id, uint256 timestamp);
    event DeliveryConfirmed(uint256 indexed id, uint256 timestamp);
    event DiscrepancyFlagged(uint256 indexed id, string reason, uint256 timestamp);

    modifier onlyAdmin() {
        require(msg.sender == admin, "ReliefTracking: caller is not admin");
        _;
    }

    modifier exists(uint256 id) {
        require(allocations[id].id != 0, "ReliefTracking: allocation does not exist");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    function allocate(
        string calldata district,
        string calldata resourceType,
        uint256 quantity,
        string calldata recipientOrg
    ) external onlyAdmin returns (uint256 id) {
        require(quantity > 0, "ReliefTracking: quantity must be positive");

        id = nextId++;
        allocations[id] = Allocation({
            id: id,
            district: district,
            resourceType: resourceType,
            quantity: quantity,
            allocatedBy: msg.sender,
            recipientOrg: recipientOrg,
            timestamp: block.timestamp,
            status: Status.Allocated
        });
        allocationIds.push(id);

        emit AllocationCreated(id, district, resourceType, quantity, recipientOrg);
    }

    function markDispatched(uint256 id) external onlyAdmin exists(id) {
        Allocation storage a = allocations[id];
        require(a.status == Status.Allocated, "ReliefTracking: must be Allocated first");
        a.status = Status.Dispatched;
        emit AllocationDispatched(id, block.timestamp);
    }

    function confirmDelivery(uint256 id) external onlyAdmin exists(id) {
        Allocation storage a = allocations[id];
        require(a.status == Status.Dispatched, "ReliefTracking: must be Dispatched first");
        a.status = Status.Delivered;
        emit DeliveryConfirmed(id, block.timestamp);
    }

    function flagDiscrepancy(uint256 id, string calldata reason) external onlyAdmin exists(id) {
        Allocation storage a = allocations[id];
        require(a.status == Status.Dispatched, "ReliefTracking: must be Dispatched to flag");
        a.status = Status.DiscrepancyFlagged;
        emit DiscrepancyFlagged(id, reason, block.timestamp);
    }

    function getAllocation(uint256 id) external view exists(id) returns (Allocation memory) {
        return allocations[id];
    }

    function totalAllocations() external view returns (uint256) {
        return allocationIds.length;
    }

    function getAllocationIds() external view returns (uint256[] memory) {
        return allocationIds;
    }
}
