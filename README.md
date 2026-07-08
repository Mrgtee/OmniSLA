# OmniSLA -- Decentralized SLA Adjudication Contract

OmniSLA is a trustless Service Level Agreement enforcement framework built as a GenLayer Intelligent Contract. It monitors web service endpoints through decentralized consensus, evaluates compliance using deterministic substring checks or LLM-based semantic analysis, and enforces financial penalties when providers breach their commitments.

---

## Deployment

| Field | Value |
|---|---|
| Network | GenLayer Bradbury Testnet |
| RPC | https://rpc-bradbury.genlayer.com |
| Deployer | 0x9F64879a55a0193e90d487EF4FA6D3123e71E6d7 |
| Contract | 0xd4E0184D77aCc7107033D6b363924950424F7e4D |
| Explorer | https://explorer-bradbury.genlayer.com/address/0xd4E0184D77aCc7107033D6b363924950424F7e4D |

---

## Equivalence Principle and Consensus Design

Bringing off-chain data (web service status pages) and non-deterministic logic (LLM evaluations) onto a blockchain is traditionally blocked by the oracle problem. If validators independently crawl a URL or run an LLM prompt, minor differences in responses would prevent consensus.

GenLayer solves this with the Equivalence Principle. OmniSLA uses `gl.vm.run_nondet_unsafe` to implement structured consensus:

1. **Leader Execution**: The elected Leader node executes `execute_check()` in isolation. It crawls the target URL, applies the validation strategy (substring or semantic LLM), and produces a structured JSON verdict.

2. **Validator Execution**: Each Validator independently runs `validate_check(leader_result)`. Validators perform their own web crawl and evaluation, then compare their structured verdict against the Leader's.

3. **Category Bucket Equivalence**: To handle cases where a Leader reports "Network" failure but a Validator reports "Server" failure (both indicating infrastructure problems), the contract groups categories into equivalence buckets:
   - **pass**: None
   - **infrastructure**: Network, Server
   - **quality**: Content, Semantic
   - **inconclusive**: Inconclusive

   Validators compare `condition_satisfied`, the category bucket (not the exact string), and `severity`. This makes consensus resilient to minor classification differences between nodes.

---

## Structured Verdict Format

Every `check_sla()` call returns and persists a JSON verdict:

```json
{
  "condition_satisfied": true,
  "failure_category": "None",
  "severity": "None",
  "confidence_pct": 95,
  "reason": "Target substring found in web response body",
  "evidence_summary": "Substring 'Operational' present in HTTP 200 response"
}
```

| Field | Type | Description |
|---|---|---|
| condition_satisfied | bool | Whether the SLA rule was met |
| failure_category | string | None, Network, Server, Content, Semantic, or Inconclusive |
| severity | string | None, Low, Medium, or High |
| confidence_pct | int | 0-100 confidence percentage (integer for GenVM compatibility) |
| reason | string | Short explanation (truncated to 256 chars) |
| evidence_summary | string | Evidence from crawled content (truncated to 512 chars) |

### INCONCLUSIVE Verdict

When the LLM returns malformed or unparseable output, the contract returns an INCONCLUSIVE verdict instead of a failure. INCONCLUSIVE verdicts:
- Do NOT increment `failed_checks`
- Do NOT increment `consecutive_failures`
- Do NOT count toward slashing

This prevents providers from being penalized for LLM infrastructure issues outside their control.

---

## Key Features

- **Trustless Escrow**: Both provider (collateral) and client (premium) deposit funds. The contract activates only when both thresholds are met.
- **Expiry Guard**: `check_sla()` reverts after the SLA end time, preventing stale checks.
- **Spam Prevention**: A configurable `check_interval_seconds` cooldown blocks repeated instant checks.
- **Consecutive Failure Policy**: Only `max_consecutive_failures` consecutive real failures trigger slashing. Successful checks reset the counter.
- **INCONCLUSIVE Handling**: Malformed LLM output does not penalize providers.
- **Category Bucket Equivalence**: Validators use grouped category buckets for flexible consensus (Network/Server are treated as equivalent infrastructure failures).
- **String Truncation**: `reason` (256 chars), `evidence_summary` (512 chars), and `body_str` (4096 chars) are truncated to prevent oversized on-chain storage.
- **Normalized Timestamps**: ISO datetime strings are converted to unix timestamps at construction time via `_iso_to_timestamp`, avoiding repeated runtime parsing.
- **Constructor Validation**: Rejects invalid strategies, non-HTTP URLs, non-positive amounts, identical provider/client addresses, and malformed ISO dates.

---

## Use Cases

1. **Web Service SLA Monitor**: SaaS providers lock collateral against a status page endpoint. Heartbeat checks verify the page reports operational status.

2. **Oracle and Data Feed Compliance**: Off-chain data nodes lock collateral. The contract checks oracle feeds for freshness and structural correctness.

3. **CDN and Hosting Availability**: Decentralized hosting providers lock collateral. Checks verify that index files contain expected content hashes.

4. **AI/LLM API Quality Assurance**: Third-party AI API providers lock collateral. Semantic checks verify that API responses meet quality thresholds.

5. **Decentralized Job Execution Verification**: Computation workers update task status endpoints. OmniSLA monitors completion status, releasing escrow on success and slashing on timeouts.

---

## Project Structure

```
contracts/
  OmniSLA.py           -- The Intelligent Contract (GenVM Python)
tests/
  direct/
    conftest.py        -- Test fixtures and helpers
    test_omni_sla.py   -- 24 in-memory unit tests
deploy/
  deployScript.ts      -- Deployment logic
  runDeploy.ts         -- Standalone deployment runner
gltest.config.yaml     -- GenLayer test config
pyproject.toml         -- Python project config
package.json           -- Node dependencies
.env                   -- Local deployment config (gitignored)
```

---

## Getting Started

### 1. Set Up the Python Environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Lint the Contract

```bash
genvm-lint contracts/OmniSLA.py
```

### 3. Run the Test Suite

```bash
PYTHONPATH=. pytest tests/direct/ -v
```

Expected output: 24 passed.

---

## Contract API

### Escrow Setup

| Method | Access | Description |
|---|---|---|
| `deposit_collateral()` | write, payable | Provider deposits collateral |
| `deposit_premium()` | write, payable | Client deposits premium |
| `refund()` | write | Withdraw deposits before activation |

### Monitoring and Payouts

| Method | Access | Description |
|---|---|---|
| `check_sla()` | write | Trigger a consensus-verified health check; returns verdict JSON |
| `close_sla()` | write | Provider collects payout after SLA expiry |

### Read-Only Queries

| Method | Access | Description |
|---|---|---|
| `get_status()` | view | Current lifecycle status (Created, Active, Violated, Closed) |
| `get_details()` | view | Full contract state as JSON |
