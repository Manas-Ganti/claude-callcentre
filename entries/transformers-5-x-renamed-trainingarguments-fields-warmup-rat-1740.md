---
id: transformers-5-x-renamed-trainingarguments-fields-warmup-rat-1740
kind: fix
title: transformers 5.x renamed TrainingArguments fields (warmup_ratio) — TRL SFTConfig/GRPOConfig crash
  after queueing
domain:
- rl-training
- python-env
stack:
  transformers: 5.15.0
  trl: 1.9.2
symptoms:
- SFTConfig.__init__() fails on unexpected keyword 'warmup_ratio' with transformers 5.15.0 + trl 1.9.2
- Fixing one renamed field just reveals the next one, each after a ~20 min queue + model load
root_cause: transformers 5.x moved/renamed several TrainingArguments fields, which TRL configs inherit.
  Code written against 4.x kwargs breaks.
fix: 'Filter config kwargs against inspect.signature(cls.__init__).parameters; remap renames that keep
  the stem (warmup_ratio -> lr_warmup_ratio), drop the rest, and LOG every remap/drop on rank 0 ("dropped,
  not accepted by this version: ...") — a silently dropped knob changes training. Apply to both SFTConfig
  and GRPOConfig (GRPO would have hit it 48 h later).'
failed_attempts:
- Fixing kwargs one at a time from crash logs — one queue wait per field
verify: python training/sft.py --dry-run and training/grpo.py --dry-run construct configs without error;
  check the log for the dropped/remapped warning line.
status: verified
uses: 1
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: '2026-10-06'
outcome_notes:
- '2026-10-06 OK: Independent confirmation from git history of healthcare_RL (commits 514463a, 0ff3635),
  not re-run this session. Same ''SFTConfig.__init__() got an unexpected keyword argument warmup_ratio''.
  Same signature-filter fix, plus one refinement: split fields into ESSENTIAL (output_dir, epochs, lr,
  batch size, grad accum -> raise if missing, since a TRL default silently changes the run) and OPTIONAL
  (drop + log). Print the full accepted signature on any drop so one failure reveals the whole API. Also
  max_seq_length -> max_length rename. Warn loudly if completion_only_loss is dropped: it changes what
  is trained, and it only applies to prompt/completion rows, not a single ''messages'' list.'
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# transformers 5.x renamed TrainingArguments fields (warmup_ratio) — TRL SFTConfig/GRPOConfig crash after queueing

> [!success] fix · verified · used 1×, failed 0× · last verified 2026-10-06
> #rl-training #python-env #kind/fix #status/verified

## Symptoms
```text
SFTConfig.__init__() fails on unexpected keyword 'warmup_ratio' with transformers 5.15.0 + trl 1.9.2
Fixing one renamed field just reveals the next one, each after a ~20 min queue + model load
```

## Root cause
transformers 5.x moved/renamed several TrainingArguments fields, which TRL configs inherit. Code written against 4.x kwargs breaks.

## Fix
Filter config kwargs against inspect.signature(cls.__init__).parameters; remap renames that keep the stem (warmup_ratio -> lr_warmup_ratio), drop the rest, and LOG every remap/drop on rank 0 ("dropped, not accepted by this version: ...") — a silently dropped knob changes training. Apply to both SFTConfig and GRPOConfig (GRPO would have hit it 48 h later).

## Failed attempts
- Fixing kwargs one at a time from crash logs — one queue wait per field

## Verify
python training/sft.py --dry-run and training/grpo.py --dry-run construct configs without error; check the log for the dropped/remapped warning line.

## Stack
| | |
|---|---|
| transformers | 5.15.0 |
| trl | 1.9.2 |

## Outcome reports
- 2026-10-06 OK: Independent confirmation from git history of healthcare_RL (commits 514463a, 0ff3635), not re-run this session. Same 'SFTConfig.__init__() got an unexpected keyword argument warmup_ratio'. Same signature-filter fix, plus one refinement: split fields into ESSENTIAL (output_dir, epochs, lr, batch size, grad accum -> raise if missing, since a TRL default silently changes the run) and OPTIONAL (drop + log). Print the full accepted signature on any drop so one failure reveals the whole API. Also max_seq_length -> max_length rename. Warn loudly if completion_only_loss is dropped: it changes what is trained, and it only applies to prompt/completion rows, not a single 'messages' list.

<small>created 2026-10-06 · id `transformers-5-x-renamed-trainingarguments-fields-warmup-rat-1740`</small>

## Notes

<!-- callcentre:end -->
Source commit bdf72d2 (training/common.py ~L295-330). Exact exception text not preserved in the repo.
