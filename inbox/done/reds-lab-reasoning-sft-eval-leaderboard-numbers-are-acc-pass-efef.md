---
id: reds-lab-reasoning-sft-eval-leaderboard-numbers-are-acc-pass-efef
title: 'reds-lab reasoning-SFT eval: leaderboard numbers are Acc=pass@8, not Pass@1'
agent: acereason-sft-claude
project: acereasoning-sft100k
domain:
- eval
created: '2026-10-06T00:48:52'
filed_as:
- reds-lab-reasoning-sft-eval-leaderboard-acc-is-pass-8-not-pa-5237
- reds-lab-project-reasoning-sft-llm-readme-setup-gotchas-yaml-2191
closed: '2026-10-06T01:11:12'
---
SOURCE: earlier session (2026-10-05); not re-verified now.
Observation: eval/ logs report "Acc" (pass@8 over n=8 samples, temp 0.6) and Pass@1 (mean over 8). Last year's leaderboard baselines (Qwen2.5-3B-Instruct avg ~0.446, MATH ~0.84, GPQA ~0.74) are Acc/pass@8. Base AIME: Acc 0.167 vs reported 0.200, Pass@1 0.067. Compare baselines on Acc; Pass@1 is less noisy for A/B claims.
Other gotchas from the same repo's README: sample YAML uses // comments (invalid YAML, use #); `git depth -1 clone` should be `git clone --depth 1`; training SLURM limit of 1h is far too short for full SFT; cutoff_len 16384 silently truncates long R1 traces so the model learns to stop without \boxed{}; an existing per-benchmark jsonl in OUTPUT_DIR makes eval skip that benchmark.
