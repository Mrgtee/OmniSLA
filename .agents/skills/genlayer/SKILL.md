---
name: genlayer-intelligent-contracts
description: Use when you want to write, test, or deploy GenLayer Intelligent Contracts. Also use when you want to understand GenLayer storage types, equivalence principles, CLI commands, and deployment scripts.
---
# GenLayer Intelligent Contracts Skill

This skill provides comprehensive instructions, references, and examples for developing GenLayer Intelligent Contracts. GenLayer is an AI-native blockchain where contracts are written in Python and executed inside GenVM, utilizing LLM prompts and web queries validated through the Equivalence Principle.

## Prerequisites & Setup

1. **Python 3.12+**: Ensure Python is installed.
2. **Node.js 18+ & npm**: Required for CLI and frontend tools.
3. **Docker**: Required for running the local GenLayer simulator.
4. **GenLayer CLI**: Install globally using:
   ```bash
   npm install -g genlayer
   ```
5. **Project Initialization**:
   ```bash
   genlayer init
   genlayer up
   ```

## Writing Intelligent Contracts

Intelligent Contracts inherit from `gl.Contract` and use specific decorators:
- `@gl.public.view` for read-only methods.
- `@gl.public.write` for state-modifying methods.

### Persistent Storage
Standard Python types like `list` and `dict` are NOT allowed for persistent storage. You must use:
- `gl.u256` or other sized types instead of standard `int`.
- `gl.DynArray[T]` instead of `list`.
- `gl.TreeMap[K, V]` instead of `dict`.
- All persistent storage fields must be statically declared at the class level.

### Equivalence Principle
Non-deterministic operations (e.g., `gl.nondet.exec_prompt`, `gl.nondet.web.get`) must run inside an isolated, argument-free local function and be executed via:
- `gl.eq_principle.strict_eq(func)`: For exact matches.
- `gl.eq_principle.prompt_non_comparative(...)`: For semantic matches on LLM responses.
- `gl.vm.run_nondet_unsafe(...)`: For custom validator-based comparison.

For detailed guidelines and API references, read the files in the `references/` directory. For code snippets, see the `examples/` directory.
