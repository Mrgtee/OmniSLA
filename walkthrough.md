# OmniSLA Deployment & Testing Walkthrough

We have successfully implemented, tested, and deployed the **OmniSLA** contract primitive on the public **GenLayer Bradbury Testnet**!

## 🚀 Deployment Details

*   **Active Network**: Genlayer Bradbury Testnet (`testnet-bradbury`)
*   **RPC Node**: `https://rpc-bradbury.genlayer.com`
*   **Explorer**: [GenLayer Bradbury Explorer](https://explorer-bradbury.genlayer.com/)
*   **Deployer Address**: `0x9F64879a55a0193e90d487EF4FA6D3123e71E6d7`
*   **Deployed Contract Address**: `0x34f5DC661505Ab3A73f9035c869F29aC3D5f89b2`
*   **Explorer Contract Link**: [0x34f5DC661505Ab3A73f9035c869F29aC3D5f89b2](https://explorer-bradbury.genlayer.com/address/0x34f5DC661505Ab3A73f9035c869F29aC3D5f89b2)

---

## 🛠️ Deployment Configuration (Passed Arguments)

The contract was deployed with the following parameters configured via `.env`:
*   **Provider Address**: `0x` (Can be funded/used for testing)
*   **Client Address**: `0x`
*   **Target SLA URL**: `https://status.openai.com`
*   **Collateral Required**: `1000` Wei
*   **Premium Required**: `500` Wei
*   **Validation Strategy**: `contains`
*   **Validation Rule**: `Operational`
*   **Max Allowed Violations**: `3`
*   **SLA End Time ISO**: `2026-12-31T23:59:59Z`

---

## 📁 Repository Commit History (Local)

The clean repository in `/home/gtee/antigravity/gtee/OmniSLA` is fully configured and committed:
1. `85bb1bd` - `feat: initial commit with OmniSLA contract and test suite`
2. `ca2e374` - `chore: update deployScript.ts for OmniSLA`
3. `654b5f5` - `chore: add standalone runDeploy.ts script`

---

## 🧪 Validation & Test Suite

All tests passed successfully in direct mode inside the clean workspace:
```bash
PYTHONPATH=. pytest tests/direct/
# Result: 8 passed in 0.36s
```
Contract linting succeeded:
```bash
genvm-lint contracts/OmniSLA.py
# Result: ✓ Lint passed (3 checks)
```
