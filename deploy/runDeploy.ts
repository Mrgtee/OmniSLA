import { createClient } from "genlayer-js";
import { testnetBradbury } from "genlayer-js/chains";
import { privateKeyToAccount } from "viem/accounts";
import dotenv from "dotenv";
import main from "./deployScript.js";

dotenv.config();

const privateKey = process.env.PRIVATE_KEY;
if (!privateKey || privateKey === "0x") {
  console.error("Error: PRIVATE_KEY not found or empty in .env");
  process.exit(1);
}

try {
  const account = privateKeyToAccount(privateKey as `0x${string}`);
  const client = createClient({
    chain: testnetBradbury,
    account: account,
  });

  console.log(`Starting deployment using address: ${account.address}`);

  main(client)
    .then(() => {
      console.log("Deployment execution finished.");
      process.exit(0);
    })
    .catch((err) => {
      console.error("Error running deployment main function:", err);
      process.exit(1);
    });
} catch (e) {
  console.error("Failed to parse private key or initialize client:", e);
  process.exit(1);
}
