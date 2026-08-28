const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const ReliefTracking = await hre.ethers.getContractFactory("ReliefTracking");
  const contract = await ReliefTracking.deploy();
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  console.log("ReliefTracking deployed to:", address);

  // Write address + ABI so the Python backend (web3.py) can pick it up without hardhat.
  const artifact = await hre.artifacts.readArtifact("ReliefTracking");
  const outDir = path.join(__dirname, "..", "..", "backend", "app", "services");
  const outPath = path.join(outDir, "relief_tracking_deployment.json");
  fs.writeFileSync(
    outPath,
    JSON.stringify({ address, abi: artifact.abi }, null, 2)
  );
  console.log("Wrote deployment info for backend at:", outPath);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
