# Equivalence Principles & Non-Deterministic Execution

GenLayer allows Intelligent Contracts to perform non-deterministic operations (like querying LLMs or fetching web pages). Because these operations are non-deterministic, different validators might obtain slightly different results. To resolve this and achieve consensus, GenLayer uses the **Equivalence Principle**.

## Basic Concept

All non-deterministic execution must be:
1. **Isolated**: Contained within an argument-free local function.
2. **Evaluated via Equivalence**: Passed to a method on `gl.eq_principle` or `gl.vm` that determines how validators verify the proposed output.
3. **Storage Read-Only**: The non-deterministic block can read parameters passed to it (or lexical closures) but cannot modify the contract's persistent storage.

---

## 1. Strict Equality (`gl.eq_principle.strict_eq`)

Use this when validators must arrive at the exact same output. Recommended for boolean checks, exact numeric values, or deterministic computations wrapped in nondet blocks.

```python
def check_web_status():
    response = gl.nondet.web.get("https://status.example.com")
    return "All Systems Operational" in response

# Validators must obtain the exact same boolean (True/False)
is_up = gl.eq_principle.strict_eq(check_web_status)
```

---

## 2. Prompt Non-Comparative (`gl.eq_principle.prompt_non_comparative`)

Use this for subjective/open-ended LLM text generation. Instead of comparing validator outputs character-by-character (which would fail consensus due to LLM variability), each validator independently verifies if the leader's output satisfies the specified `criteria`.

### API Signature
```python
gl.eq_principle.prompt_non_comparative(
    prompt_fn: Callable[[], str],
    task: str,
    criteria: str
) -> str
```

### Example
```python
class ContentContract(gl.Contract):
    summary: str

    @gl.public.write
    def generate_summary(self, article_text: str):
        def get_prompt() -> str:
            return f"Summarize the following article in 1 sentence:\n{article_text}"

        self.summary = gl.eq_principle.prompt_non_comparative(
            get_prompt,
            task="Summarize article in 1 sentence",
            criteria="The output must be a single, grammatically correct sentence summarizing the article."
        )
```

---

## 3. Custom Validation (`gl.vm.run_nondet_unsafe`)

For advanced scenarios, you can define a custom validation function. The leader executes first, and validators run a verification function (`validator_fn`) that receives the leader's output (`leaders_res`) and returns `True` if it is equivalent, or `False` if it should be rejected.

### Example: LLM Structured JSON Output Verification
```python
import json

class MarketContract(gl.Contract):
    @gl.public.write
    def predict_winner(self) -> str:
        # 1. Leader function runs prompt and returns JSON
        def leader_fn():
            prompt = "Who won the match? Return JSON: {'winner': str, 'confidence': float}"
            return gl.nondet.exec_prompt(prompt, response_format="json")

        # 2. Validator function checks if leader's result is valid and agrees with validator's LLM
        def validator_fn(leaders_res) -> bool:
            # Check if leader returned successfully
            if not isinstance(leaders_res, gl.vm.Return):
                return False
            
            # Validator runs the same prompt
            my_res = leader_fn()
            
            # Compare structural logic, not exact string matches
            leader_winner = leaders_res.calldata.get("winner")
            my_winner = my_res.get("winner")
            return leader_winner == my_winner

        # 3. Execute with run_nondet_unsafe
        winner_info = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        return winner_info["winner"]
```

---

## Critical Rules for Non-Deterministic Functions

1. **No Storage Writes**: Never attempt to modify `self.some_storage_var = ...` inside a non-deterministic block. Storage writes are only permitted in the main contract transaction thread.
2. **Always Use JSON Response Format for LLMs**: When executing prompts via `gl.nondet.exec_prompt`, pass `response_format="json"`. Structured JSON is much easier to validate programmatically than raw natural language strings.
3. **Avoid Strict Equality on Raw LLM Text**: Never run `strict_eq` on a function returning raw LLM output, as validators running different model instances (Greyboxing) will output slightly different sentences, leading to failed consensus.
