# GenLayer CLI & Development Workflow Reference

The GenLayer CLI and associated tools manage the local development environment, contract linting, and deployment.

## Installation

Install the GenLayer CLI globally:
```bash
npm install -g genlayer
```

---

## 1. Local Network Management

GenLayer uses Docker to spin up a local validator node and simulator (GenLayer Studio).

### Initialize Configuration
Create configuration files, local validator configurations, and directory structure in an empty project:
```bash
genlayer init
```

### Start Localnet
Launches the validator services and simulator container:
```bash
genlayer up
```
*Note: This command runs in the foreground or sets up Docker containers. Once running, the local simulator is accessible, usually at `http://localhost:4000/api` or via the web console.*

### Stop Localnet
Stop and remove all running GenLayer containers and services:
```bash
genlayer stop
```

---

## 2. Contract Deployment

Deploy Intelligent Contracts to a specific RPC node (default is localnet).

### Basic Deployment
```bash
genlayer deploy --contract contracts/my_contract.py
```

### Deployment with Constructor Arguments
Arguments are space-separated:
```bash
genlayer deploy --contract contracts/my_contract.py --args "My Token Name" 100000 true
```

### Custom RPC Target
Deploy to a testnet or custom local node:
```bash
genlayer deploy --contract contracts/my_contract.py --rpc https://testnet.genlayer.com/api
```

---

## 3. Account Management

Interact with keys and balances for deployment and testing.

### List Accounts
Show local validator and dev accounts:
```bash
genlayer account list
```

### Create New Account
Generate a new private key and address:
```bash
genlayer account create
```

---

## 4. Contract Linting (`genvm-lint`)

Before deploying any contract, compile and lint it. The `genvm-lint` tool analyzes the contract for security risks, forbidden Python imports, and incorrect storage annotation types.

Run the linter on a specific contract file:
```bash
genvm-lint contracts/my_contract.py
```

It is highly recommended to run this command before deployment to ensure your contract complies with GenVM's restricted Python subset.
