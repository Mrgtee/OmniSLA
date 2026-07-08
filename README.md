# OmniSLA (Decentralized SLA Heartbeat Monitor)

OmniSLA is a decentralized, trustless Service Level Agreement (SLA) monitoring framework built as an Intelligent Contract on **GenLayer**. It programmatically enforces service quality agreements between a **Service Provider** and a **Client** by locking funds in escrow and evaluating endpoints using consensus-verified web crawls and LLM evaluations.

## 🚀 Key Features

*   **Trustless Escrow**: The client deposits the premium and the provider deposits the collateral. The contract activates automatically only when both parties have fully funded their shares.
*   **Flexible Heartbeat Monitoring**:
    *   `contains`: A fast, deterministic substring check on the target website's response.
    *   `semantic`: A cognitive, LLM-driven check that evaluates unstructured HTML or JSON output against natural language criteria.
*   **Decentralized Equivalence Consensus**: All heartbeat evaluations run through GenVM's equivalence principle consensus, ensuring no single validator can manipulate or falsify validation results.
*   **Programmatic Slasher**: If violations exceed the maximum allowed threshold, the contract automatically slashes the provider and transfers all collateral and premium to the client.
*   **Normal Closure**: Once the SLA duration expires without violating the conditions, the provider can close the contract to receive their collateral back along with the client's premium payment.

---

## 📁 Project Structure

```text
contracts/
  OmniSLA.py           # The OmniSLA Intelligent Contract (GenVM Python)
tests/
  direct/
    conftest.py        # Test runner and direct VM configuration
    test_omni_sla.py   # In-memory unit test suite for OmniSLA
gltest.config.yaml     # GenLayer test network config
pyproject.toml         # Python environment config
tsconfig.json          # TypeScript project config
package.json           # Node project dependencies
```

---

## 🛠️ Getting Started

### 1. Set Up the Python Environment
Create a virtual environment and install the required dependencies (requires Python >= 3.12):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Lint the Contract
Use the GenVM static analyzer to verify that the contract complies with all GenLayer security and non-deterministic rule constraints:

```bash
genvm-lint contracts/OmniSLA.py
```

### 3. Run the Test Suite
Run the fast, in-memory direct mode tests containing mocks for web requests and LLM evaluations:

```bash
PYTHONPATH=. pytest tests/direct/
```

---

## 📝 Contract API Details

### Escrow Setup
*   `deposit_collateral()`: Payable function for the provider to fund their collateral.
*   `deposit_premium()`: Payable function for the client to fund the service premium.
*   `refund()`: Allows either party to withdraw their deposits before the SLA is activated.

### Heartbeat & Payouts
*   `check_sla()`: Triggers the web search and validation checks. Can be called by anyone or cron triggers.
*   `close_sla()`: Allows the provider to collect their payout once the SLA end time has expired.
