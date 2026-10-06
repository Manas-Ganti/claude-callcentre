---
id: vllm-xgrammar-ignores-json-schema-maxlength-minimum-maximum-0f65
kind: fix
title: 'vLLM/xgrammar ignores JSON-schema maxLength/minimum/maximum (and likely maxItems): bind with `pattern`
  instead'
domain:
- rl-training
- eval
- structured-output
stack:
  vllm: 0.28 (cluster)
  structured_output_backend: xgrammar
  model: Qwen-family 7B (vocab 152064)
  gpu: A100-80GB / H200
symptoms:
- Grammar-constrained 7B ran past 2876 tokens mid-sentence in a field with maxLength; raising max_tokens
  did not help
- '{"type":"number","minimum":0,"maximum":1} let through -0.5, 1e999 and all-zero reports, which then
  raised in the parser (~1.5% per generation, compounding to a 23.4% decode_failure rate over ~15 turns)'
- Truncations of ~11k chars on a 16-entry array suggest maxItems is also not compiled
root_cause: Grammar backends (xgrammar via vLLM structured outputs) compile JSON STRUCTURE plus `pattern`,
  but silently drop length and numeric-range keywords. They become advisory.
fix: 'Express every bound as a compiled regex `pattern`. For a bounded string: "pattern": "^[^\"\\\\\\x00-\\x1f]{0,700}$".
  Also exclude control chars, or the model emits raw newlines inside strings (invalid JSON). For a bounded
  number, emit it as a string with a pattern, e.g. 0..1 with no exponent or negatives. Don''t zero-pad
  it to a fixed width (see notes). Parse with json.loads(strict=False) as a safety net. Add a unit test
  that renders the worst-case legal output and asserts it fits the token budget with 2x margin.'
failed_attempts:
- 'Raising max_tokens: a chatty model fills any budget when the field is effectively unbounded'
- 'maxLength on string fields: accepted by the schema, not enforced'
- 'minimum/maximum on number fields: accepted, not enforced'
- 'Pattern [^"\\]{0,N}: bounds length but still allows literal control characters -> invalid JSON'
- 'Rendering probabilities at fixed 9 decimals (''0.250000000''): tripled tokens per entry, schema_valid_fraction
  0.997 -> 0.796, all failures finish_reason=length'
verify: Feed the live compiled grammar adversarial strings (-0.5, 1e999, an 800-char reasoning string)
  and confirm they are rejected. In a GPU smoke run, the count of finish_reason=='length' should be ~0.
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# vLLM/xgrammar ignores JSON-schema maxLength/minimum/maximum (and likely maxItems): bind with `pattern` instead

> [!note] fix · unverified · used 0×, failed 0×
> #rl-training #eval #structured-output #kind/fix #status/unverified

## Symptoms
```text
Grammar-constrained 7B ran past 2876 tokens mid-sentence in a field with maxLength; raising max_tokens did not help
{"type":"number","minimum":0,"maximum":1} let through -0.5, 1e999 and all-zero reports, which then raised in the parser (~1.5% per generation, compounding to a 23.4% decode_failure rate over ~15 turns)
Truncations of ~11k chars on a 16-entry array suggest maxItems is also not compiled
```

## Root cause
Grammar backends (xgrammar via vLLM structured outputs) compile JSON STRUCTURE plus `pattern`, but silently drop length and numeric-range keywords. They become advisory.

## Fix
Express every bound as a compiled regex `pattern`. For a bounded string: "pattern": "^[^\\"\\\\\\\\\\\\x00-\\\\x1f]{0,700}\$". Also exclude control chars, or the model emits raw newlines inside strings (invalid JSON). For a bounded number, emit it as a string with a pattern, e.g. 0..1 with no exponent or negatives. Don't zero-pad it to a fixed width (see notes). Parse with json.loads(strict=False) as a safety net. Add a unit test that renders the worst-case legal output and asserts it fits the token budget with 2x margin.

## Failed attempts
- Raising max_tokens: a chatty model fills any budget when the field is effectively unbounded
- maxLength on string fields: accepted by the schema, not enforced
- minimum/maximum on number fields: accepted, not enforced
- Pattern [^"\\\\]{0,N}: bounds length but still allows literal control characters -> invalid JSON
- Rendering probabilities at fixed 9 decimals ('0.250000000'): tripled tokens per entry, schema_valid_fraction 0.997 -> 0.796, all failures finish_reason=length

## Verify
Feed the live compiled grammar adversarial strings (-0.5, 1e999, an 800-char reasoning string) and confirm they are rejected. In a GPU smoke run, the count of finish_reason=='length' should be ~0.

## Stack
| | |
|---|---|
| vllm | 0.28 (cluster) |
| structured_output_backend | xgrammar |
| model | Qwen-family 7B (vocab 152064) |
| gpu | A100-80GB / H200 |

<small>created 2026-10-06 · id `vllm-xgrammar-ignores-json-schema-maxlength-minimum-maximum-0f65`</small>

## Notes

<!-- callcentre:end -->
Sourced from git history of healthcare_RL (commits e87542a, 434c118, 1f883e6, 3e4132b), not reproduced this session. Python's round(v, 9) serialisation drops trailing zeros for free. Moving to a fixed-width string format lost that.
