---
id: sft-targets-for-a-grammar-constrained-policy-must-byte-match-ea9a
kind: convention
title: SFT targets for a grammar-constrained policy must BYTE-match what the decoder emits (key order,
  value types, separators)
domain:
- rl-training
- sft
- structured-output
stack:
  trl: '>=0.11 (SFTTrainer, prompt/completion rows)'
  vllm: '0.28'
  structured_output_backend: xgrammar
  model: Qwen-family 7B LoRA
symptoms:
- SFT'd 7B scored worse than the base model (mean R -0.764 vs -0.689), was 3x slower, rambled, and drifted
  into Chinese/Norwegian/emoji mid-string
- 'Training targets {"kind":..,"prediction":..,"reasoning":..} but the decoder forced {"kind": .., "reasoning":
  ..}: json.dumps(sort_keys=True) gave alphabetical order, while the grammar emits schema DECLARATION
  order'
- A key-order-only reuse guard later passed a stale SFT set after a float->string value change, and then
  a separator change
root_cause: A grammar-constrained decoder forces properties in schema declaration order, with its own
  value formats and whitespace. Any deviation in the SFT targets puts every token after the first divergence
  off-distribution. The mismatch happened three times in one repo (key order, value type, separators),
  and each guard only caught the previous variant.
fix: Have one render_wire(action) function used by both SFT target building and the parser tests, with
  key order pinned to the schema's declaration order and separators matching what the decoder can emit
  (compact (',',':') if disable_any_whitespace is on). Before reusing a cached SFT set, re-render every
  target and require a BYTE-identical match, plus validate against the live JSON schema. On mismatch,
  rebuild. Don't rely on checks that only cover key order.
failed_attempts:
- 'json.dumps(sort_keys=True) for targets: alphabetical order != decoder order'
- 'Reuse guard checking key order only: passed a set whose probability values had changed float->string'
- 'Schema-validation guard: passes a set whose separators differ (still valid JSON)'
verify: 'For every row in the cached SFT jsonl: assert row[''completion''] == render_wire(parse(row[''completion''])),
  and jsonschema.validate against the live action schema.'
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# SFT targets for a grammar-constrained policy must BYTE-match what the decoder emits (key order, value types, separators)

> [!note] convention · unverified · used 0×, failed 0×
> #rl-training #sft #structured-output #kind/convention #status/unverified

## Symptoms
```text
SFT'd 7B scored worse than the base model (mean R -0.764 vs -0.689), was 3x slower, rambled, and drifted into Chinese/Norwegian/emoji mid-string
Training targets {"kind":..,"prediction":..,"reasoning":..} but the decoder forced {"kind": .., "reasoning": ..}: json.dumps(sort_keys=True) gave alphabetical order, while the grammar emits schema DECLARATION order
A key-order-only reuse guard later passed a stale SFT set after a float->string value change, and then a separator change
```

## Root cause
A grammar-constrained decoder forces properties in schema declaration order, with its own value formats and whitespace. Any deviation in the SFT targets puts every token after the first divergence off-distribution. The mismatch happened three times in one repo (key order, value type, separators), and each guard only caught the previous variant.

## Convention
Have one render_wire(action) function used by both SFT target building and the parser tests, with key order pinned to the schema's declaration order and separators matching what the decoder can emit (compact (',',':') if disable_any_whitespace is on). Before reusing a cached SFT set, re-render every target and require a BYTE-identical match, plus validate against the live JSON schema. On mismatch, rebuild. Don't rely on checks that only cover key order.

## Failed attempts
- json.dumps(sort_keys=True) for targets: alphabetical order != decoder order
- Reuse guard checking key order only: passed a set whose probability values had changed float->string
- Schema-validation guard: passes a set whose separators differ (still valid JSON)

## Verify
For every row in the cached SFT jsonl: assert row['completion'] == render_wire(parse(row['completion'])), and jsonschema.validate against the live action schema.

## Stack
| | |
|---|---|
| trl | >=0.11 (SFTTrainer, prompt/completion rows) |
| vllm | 0.28 |
| structured_output_backend | xgrammar |
| model | Qwen-family 7B LoRA |

<small>created 2026-10-06 · id `sft-targets-for-a-grammar-constrained-policy-must-byte-match-ea9a`</small>

## Notes

<!-- callcentre:end -->
Sourced from healthcare_RL git history (c6d1ef3, 7a9b96f, 1e1d325, 345be17), not reproduced this session. Also bump a grammar fingerprint in the SFT set metadata whenever the schema changes.
