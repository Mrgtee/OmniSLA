import { getProvider, getAccountFromEnvOrDefault } from "@genlayer/cli";

async function main() {
  console.log("Initializing GenLayer client...");
  
  // Retrieve network provider based on config or env settings
  const provider = getProvider();
  
  // Get deployer account credentials
  const account = getAccountFromEnvOrDefault();
  console.log(`Deploying from account: ${account.address}`);

  // Deploy SimpleStorage contract with constructor argument (e.g., initial value 100)
  const initialValue = 100n;
  const contractPath = "contracts/simple_storage.py";
  
  console.log(`Deploying contract ${contractPath}...`);
  const deployResult = await provider.deployContract(
    account, 
    contractPath, 
    [initialValue]
  );
  
  console.log(`Contract deployed successfully!`);
  console.log(`Contract Address: ${deployResult.contractAddress}`);
  console.log(`Transaction Hash: ${deployResult.transactionHash}`);
}

main().catch((error) => {
  console.error("Deployment failed:", error);
  process.exit(1);
});
