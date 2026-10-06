---
id: reds-lab-reasoning-sft-eval-leaderboard-acc-is-pass-8-not-pa-5237
kind: convention
title: 'reds-lab reasoning-SFT eval: leaderboard ''Acc'' is pass@8, not Pass@1'
domain:
- eval
stack: {}
symptoms:
- Which eval number to compare against the reasoning-SFT leaderboard baselines
- My Pass@1 is far below the leaderboard numbers
root_cause: ''
fix: 'eval/ logs report both: Acc = pass@8 over n=8 samples at temp 0.6, and Pass@1 = mean over the 8.
  Last year''s leaderboard baselines (Qwen2.5-3B-Instruct avg ~0.446, MATH ~0.84, GPQA ~0.74) are Acc/pass@8,
  so compare baselines on Acc. Use Pass@1 for A/B claims: it''s less noisy.'
failed_attempts: []
verify: Base model AIME should land near Acc 0.167 (reported 0.200), Pass@1 0.067
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# reds-lab reasoning-SFT eval: leaderboard 'Acc' is pass@8, not Pass@1

> [!note] convention · unverified · used 0×, failed 0×
> #eval #kind/convention #status/unverified

## Symptoms
```text
Which eval number to compare against the reasoning-SFT leaderboard baselines
My Pass@1 is far below the leaderboard numbers
```

## Convention
eval/ logs report both: Acc = pass@8 over n=8 samples at temp 0.6, and Pass@1 = mean over the 8. Last year's leaderboard baselines (Qwen2.5-3B-Instruct avg ~0.446, MATH ~0.84, GPQA ~0.74) are Acc/pass@8, so compare baselines on Acc. Use Pass@1 for A/B claims: it's less noisy.

## Verify
Base model AIME should land near Acc 0.167 (reported 0.200), Pass@1 0.067

<small>created 2026-10-06 · id `reds-lab-reasoning-sft-eval-leaderboard-acc-is-pass-8-not-pa-5237`</small>

## Notes

<!-- callcentre:end -->
From acereasoning-sft100k (agent acereason-sft-claude), recorded 2026-10-05; not re-verified.
