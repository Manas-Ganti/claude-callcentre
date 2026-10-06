---
id: 20-structured-output-truncation-from-inter-token-whitespace-ded5
kind: fix
title: '~20% structured-output truncation from inter-token whitespace runaway: set disable_any_whitespace
  with backend named explicitly'
domain:
- rl-training
- eval
- structured-output
stack:
  vllm: '0.28'
  structured_output_backend: xgrammar
  model: Qwen-family 7B + LoRA
symptoms:
- ~20% of generations truncated with finish_reason 'length' even though string length and array bounds
  were enforced by pattern
- 'Worst case: 18,299 chars after a single array entry, mostly newlines between JSON tokens'
- 'Output began ''{\n  "kind": ...'': tokens spent on pretty-printing'
- 'ValueError when passing disable_any_whitespace with the default ''auto'' backend: only supported for
  xgrammar and guidance'
root_cause: A JSON grammar allows arbitrary whitespace BETWEEN tokens, so a low-entropy policy (here after
  SFT at 2e-5 took entropy 0.895 -> 0.40) can loop on newlines legally until max_tokens. disable_any_whitespace
  is rejected unless the backend is named explicitly.
fix: 'structured_outputs_config={"backend": "xgrammar", "disable_any_whitespace": True} (pass as a dict,
  and check that LLM.__init__ accepts it, since the config class has moved between releases). Render SFT
  targets with compact separators ('','', '':'') to match. Optionally use a config ladder: try [{backend:
  xgrammar, disable_any_whitespace: True}, {backend: xgrammar}, {}] and print which rung was accepted.
  Then confirm in output that whitespace is actually gone.'
failed_attempts:
- Raising max_tokens
- 'Bounding strings/arrays alone: whitespace sits between tokens, outside any field'
- An earlier attempt at disable_any_whitespace was judged ineffective ('engine accepted it and model still
  emitted spaces') and was dropped. Likely it was silently falling back to a lower rung or the default
  backend. Log the rung that was accepted and grep the outputs.
verify: 'Run a short smoke (here: scripts/gpu_smoke.py --lora <adapter>) and assert no generation contains
  ''\n'' or '': '' outside string values, and that the finish_reason==''length'' count is ~0.'
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# ~20% structured-output truncation from inter-token whitespace runaway: set disable_any_whitespace with backend named explicitly

> [!note] fix · unverified · used 0×, failed 0×
> #rl-training #eval #structured-output #kind/fix #status/unverified

## Symptoms
```text
~20% of generations truncated with finish_reason 'length' even though string length and array bounds were enforced by pattern
Worst case: 18,299 chars after a single array entry, mostly newlines between JSON tokens
Output began '{\n  "kind": ...': tokens spent on pretty-printing
ValueError when passing disable_any_whitespace with the default 'auto' backend: only supported for xgrammar and guidance
```

## Root cause
A JSON grammar allows arbitrary whitespace BETWEEN tokens, so a low-entropy policy (here after SFT at 2e-5 took entropy 0.895 -> 0.40) can loop on newlines legally until max_tokens. disable_any_whitespace is rejected unless the backend is named explicitly.

## Fix
structured_outputs_config={"backend": "xgrammar", "disable_any_whitespace": True} (pass as a dict, and check that LLM.__init__ accepts it, since the config class has moved between releases). Render SFT targets with compact separators (',', ':') to match. Optionally use a config ladder: try [{backend: xgrammar, disable_any_whitespace: True}, {backend: xgrammar}, {}] and print which rung was accepted. Then confirm in output that whitespace is actually gone.

## Failed attempts
- Raising max_tokens
- Bounding strings/arrays alone: whitespace sits between tokens, outside any field
- An earlier attempt at disable_any_whitespace was judged ineffective ('engine accepted it and model still emitted spaces') and was dropped. Likely it was silently falling back to a lower rung or the default backend. Log the rung that was accepted and grep the outputs.

## Verify
Run a short smoke (here: scripts/gpu_smoke.py --lora \<adapter>) and assert no generation contains '\\n' or ': ' outside string values, and that the finish_reason=='length' count is ~0.

## Stack
| | |
|---|---|
| vllm | 0.28 |
| structured_output_backend | xgrammar |
| model | Qwen-family 7B + LoRA |

<small>created 2026-10-06 · id `20-structured-output-truncation-from-inter-token-whitespace-ded5`</small>

## Notes

<!-- callcentre:end -->
Sourced from healthcare_RL git history (e87542a, 7890f6e, c6d1ef3, 345be17), not reproduced this session. The final commit lands the fix but its effect on the truncation rate isn't recorded as measured. Treat it as unverified.
