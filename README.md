# OmniSLA -- Decentralized SLA Adjudication Contract

OmniSLA is a trustless Service Level Agreement enforcement framework built as a GenLayer Intelligent Contract. It programmatically monitors web service endpoints through decentralized consensus, evaluates compliance using deterministic substring checks or LLM-based semantic analysis, and enforces financial penalties when providers breach their commitments.

---

## Deployment

| Field | Value |
|---|---|
| Network | GenLayer Bradbury Testnet |
| RPC | https://rpc-bradbury.genlayer.com |
| Deployer | 0x9F64879a55a0193e90d487EF4FA6D3123e71E6d7 |
| Contract | 0xd840f9b16Dc0E513F4ab9E4724887b9c3C1D415C |
| Explorer | https://explorer-bradbury.genlayer.com/address/0xd840f9b16Dc0E513F4ab9E4724887b9c3C1D415C |

---

## Equivalence Principle and Consensus Design

Bringing off-chain data (web service status pages) and non-deterministic logic (LLM evaluations) onto a blockchain is traditionally blocked by the oracle problem. If validators independently crawl a URL or run an LLM prompt, minor differences in responses would prevent consensus.

GenLayer solves this with the Equivalence Principle. OmniSLA uses `gl.vm.run_nondet_unsafe` to implement structured consensus:

1. **Leader Execution**: The elected Leader node executes `execute_check()` in isolation. It crawls the target URL, applies the validation strategy (substring or semantic LLM), and produces a structured JSON verdict.

2. **Validator Execution**: Each Validator independently runs `validate_check(leader_result)`. Validators perform their own web crawl and evaluation, then compare their structured verdict against the Leader's.

3. **Deterministic Comparison**: To reach consensus despite natural LLM variability, validators compare only the deterministic fields:
   - `condition_satisfied` -- whether the service is compliant
   - `failure_category` -- Network, Server, Content, Semantic, or None
   - `severity` -- None, Low, Medium, or High

   The `reason`, `evidence_summary`, and `confidence_pct` fields are informational and are not compared. This ensures consensus is achievable as long as validators agree on the factual outcome, regardless of minor phrasing differences.

---

## Structured Verdict Format

Every `check_sla()` call returns (and persists) a JSON verdict with this schema:

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
| failure_category | string | None, Network, Server, Content, or Semantic |
| severity | string | None, Low, Medium, or High |
| confidence_pct | int | 0-100, confidence in the verdict (integer to avoid GenVM float encoding issues) |
| reason | string | Short explanation of the decision |
| evidence_summary | string | Summary of evidence from the crawled content |

---

## Key Features

- **Trustless Escrow**: Both provider (collateral) and client (premium) deposit funds. The contract activates only when both thresholds are met.
- **Spam Prevention**: A configurable `check_interval_seconds` cooldown blocks repeated instant checks.
- **Consecutive Failure Policy**: Providers are not slashed on transient errors. Only `max_consecutive_failures` consecutive failures in a row trigger slashing.
- **Structured Adjudication**: Verdicts contain category, severity, confidence, and evidence instead of bare booleans.
- **Check Counters**: `total_checks`, `successful_checks`, and `failed_checks` provide a full audit trail.
- **Prompt Injection Defense**: The semantic LLM prompt is hardened with explicit system instructions to treat webpage content as passive data and reject embedded override attempts.
- **Constructor Validation**: Rejects invalid strategies, non-HTTP URLs, non-positive amounts, identical provider/client addresses, and malformed ISO dates at deployment time.

---

## Use Cases

1. **Web Service SLA Monitor**: SaaS providers lock collateral against a status page endpoint. Heartbeat checks verify the page reports operational status. Consecutive violations trigger automatic slashing.

2. **Oracle and Data Feed Compliance**: Off-chain data nodes lock collateral. The contract checks oracle feeds for freshness and structural correctness.

3. **CDN and Hosting Availability**: Decentralized hosting providers lock collateral. Checks verify that index files contain expected content hashes or script patterns.

4. **AI/LLM API Quality Assurance**: Third-party AI API providers lock collateral. Semantic checks verify that API responses meet quality thresholds (response format, latency, correctness).

5. **Decentralized Job Execution Verification**: Computation workers update task status endpoints. OmniSLA monitors completion status, releasing escrow on success and slashing on timeouts.

---

## Project Structure

```
contracts/
  OmniSLA.py           -- The Intelligent Contract (GenVM Python)
tests/
  direct/
    conftest.py        -- Test fixtures and helpers
    test_omni_sla.py   -- 21 in-memory unit tests
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

Expected output: 21 passed.

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
| `check_sla()` | write | Trigger a consensus-verified health check, returns verdict JSON |
| `close_sla()` | write | Provider collects payout after SLA expiry |

### Read-Only Queries

| Method | Access | Description |
|---|---|---|
| `get_status()` | view | Current lifecycle status (Created, Active, Violated, Closed) |
| `get_details()` | view | Full contract state as JSON |
