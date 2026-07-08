import { readFileSync } from "fs";
import path from "path";
import dotenv from "dotenv";
import { createClient } from "genlayer-js";
import { privateKeyToAccount } from "viem/accounts";
import { testnetBradbury } from "genlayer-js/chains";
import {
  TransactionHash,
  TransactionStatus,
  GenLayerClient,
  DecodedDeployData,
  GenLayerChain,
} from "genlayer-js/types";
import { localnet } from "genlayer-js/chains";

dotenv.config();

export default async function main(client: GenLayerClient<any>) {
  const filePath = path.resolve(process.cwd(), "contracts/OmniSLA.py");

  // Determine active client (override if PRIVATE_KEY is configured in .env)
  let activeClient = client;
  if (process.env.PRIVATE_KEY && process.env.PRIVATE_KEY.startsWith("0x") && process.env.PRIVATE_KEY.length > 2) {
    const account = privateKeyToAccount(process.env.PRIVATE_KEY as `0x${string}`);
    activeClient = createClient({
      chain: testnetBradbury,
      account: account,
    });
    console.log(`Using custom deployment account from .env: ${activeClient.account.address}`);
  } else {
    console.log(`Using default CLI account for deployment: ${activeClient.account.address}`);
  }

  try {
    const contractCode = new Uint8Array(readFileSync(filePath));

    await activeClient.initializeConsensusSmartContract();

    const providerAddr = process.env.PROVIDER_ADDRESS || activeClient.account.address;
    const clientAddr = process.env.CLIENT_ADDRESS || activeClient.account.address;
    const targetUrl = process.env.TARGET_URL || "https://status.openai.com";
    const collateral = BigInt(process.env.COLLATERAL_REQUIRED || "1000");
    const premium = BigInt(process.env.PREMIUM_REQUIRED || "500");
    const strategy = process.env.VALIDATION_STRATEGY || "contains";
    const rule = process.env.VALIDATION_RULE || "Operational";
    const maxViolations = Number(process.env.MAX_ALLOWED_VIOLATIONS || "3");
    const endTimeIso = process.env.SLA_END_TIME_ISO || "2026-12-31T23:59:59Z";

    console.log(`Deploying OmniSLA with arguments:`);
    console.log(`  Provider: ${providerAddr}`);
    console.log(`  Client: ${clientAddr}`);
    console.log(`  Target URL: ${targetUrl}`);
    console.log(`  Collateral Required: ${collateral}`);
    console.log(`  Premium Required: ${premium}`);
    console.log(`  Validation Strategy: ${strategy}`);
    console.log(`  Validation Rule: ${rule}`);
    console.log(`  Max Allowed Violations: ${maxViolations}`);
    console.log(`  SLA End Time ISO: ${endTimeIso}`);

    const deployTransaction = await activeClient.deployContract({
      code: contractCode,
      args: [
        providerAddr,
        clientAddr,
        targetUrl,
        collateral,
        premium,
        strategy,
        rule,
        maxViolations,
        endTimeIso
      ],
    });

    const receipt = await activeClient.waitForTransactionReceipt({
      hash: deployTransaction as TransactionHash,
      status: TransactionStatus.ACCEPTED,
      retries: 200,
    });

    if (
      receipt.status !== 5 &&
      receipt.status !== 6 &&
      receipt.statusName !== "ACCEPTED" &&
      receipt.statusName !== "FINALIZED"
    ) {
      throw new Error(`Deployment failed. Receipt: ${JSON.stringify(receipt)}`);
    }

    const deployedContractAddress =
      (activeClient.chain as GenLayerChain).id === localnet.id
        ? receipt.data.contract_address
        : (receipt.txDataDecoded as DecodedDeployData)?.contractAddress;

    console.log(`Contract deployed at address: ${deployedContractAddress}`);
  } catch (error) {
    throw new Error(`Error during deployment: ${error}`);
  }
}


