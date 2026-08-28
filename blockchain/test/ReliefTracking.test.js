const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("ReliefTracking", function () {
  let contract, admin, other;

  beforeEach(async function () {
    [admin, other] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("ReliefTracking");
    contract = await Factory.deploy();
    await contract.waitForDeployment();
  });

  it("allocates, dispatches, and confirms delivery through the full lifecycle", async function () {
    await expect(contract.allocate("Wayanad", "food_kg", 500, "Kerala SDMA"))
      .to.emit(contract, "AllocationCreated")
      .withArgs(1n, "Wayanad", "food_kg", 500n, "Kerala SDMA");

    let allocation = await contract.getAllocation(1);
    expect(allocation.status).to.equal(0); // Allocated

    await contract.markDispatched(1);
    allocation = await contract.getAllocation(1);
    expect(allocation.status).to.equal(1); // Dispatched

    await contract.confirmDelivery(1);
    allocation = await contract.getAllocation(1);
    expect(allocation.status).to.equal(2); // Delivered

    expect(await contract.totalAllocations()).to.equal(1);
  });

  it("supports flagging a discrepancy instead of confirming delivery", async function () {
    await contract.allocate("Barpeta", "water_litres", 2000, "Assam SDRF");
    await contract.markDispatched(1);
    await expect(contract.flagDiscrepancy(1, "Quantity mismatch at delivery point"))
      .to.emit(contract, "DiscrepancyFlagged");

    const allocation = await contract.getAllocation(1);
    expect(allocation.status).to.equal(3); // DiscrepancyFlagged
  });

  it("rejects allocation calls from non-admin accounts", async function () {
    await expect(
      contract.connect(other).allocate("Idukki", "medical_kits", 10, "Red Cross")
    ).to.be.revertedWith("ReliefTracking: caller is not admin");
  });

  it("rejects skipping the lifecycle order", async function () {
    await contract.allocate("Cuttack", "shelter_units", 100, "Odisha SDMA");
    await expect(contract.confirmDelivery(1)).to.be.revertedWith(
      "ReliefTracking: must be Dispatched first"
    );
  });
});
