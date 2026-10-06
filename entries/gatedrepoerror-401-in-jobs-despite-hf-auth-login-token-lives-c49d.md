---
id: gatedrepoerror-401-in-jobs-despite-hf-auth-login-token-lives-c49d
kind: fix
title: GatedRepoError 401 in jobs despite `hf auth login` — token lives at $HF_HOME/token, jobs set a
  different HF_HOME
domain:
- infra
- vt-arc
stack:
  huggingface_hub: 0.36.x / 1.x
  cluster: VT ARC
symptoms:
- 'GatedRepoError: 401 Client Error. Cannot access gated repo ...'
- Access to model X is restricted. You must have access to it and be authenticated.
- Ungated/cached models load fine; only gated downloads fail
root_cause: huggingface_hub reads the token from $HF_HOME/token. Jobs export HF_HOME=/home/<user>/hf_cache,
  but a plain `hf auth login` writes ~/.cache/huggingface/token, so jobs run anonymously. Reads as a permissions
  problem; is a path problem.
fix: 'Log in with the job''s HF_HOME set: HF_HOME=/home/<user>/hf_cache hf auth login  (token lands at
  $HF_HOME/token, covers both login-node and sbatch --export=ALL jobs). Moving the cache orphans the token.'
failed_attempts:
- Diagnosing with model_info('<gated repo>') — HF serves gated repo METADATA publicly, so it succeeds
  anonymously and proves nothing
- Putting HF_TOKEN in a secrets file sourced only by the SLURM env script — login-node work stays anonymous
verify: HF_HOME=<cache> python -c "from huggingface_hub import whoami; print(whoami()['name'])"  (LocalTokenNotFoundError
  => path problem); then HF_HOME=<cache> python -c "from huggingface_hub import hf_hub_download; print(hf_hub_download('black-forest-labs/FLUX.1-dev','model_index.json'))"  (401
  here with a username above => licence not accepted)
status: unverified
uses: 0
failures: 0
consecutive_failures: 0
created: '2026-10-06'
last_verified: null
---
<!-- callcentre:begin (generated from the properties above: edit those, not this) -->
# GatedRepoError 401 in jobs despite `hf auth login` — token lives at \$HF_HOME/token, jobs set a different HF_HOME

> [!note] fix · unverified · used 0×, failed 0×
> #infra #vt-arc #kind/fix #status/unverified

## Symptoms
```text
GatedRepoError: 401 Client Error. Cannot access gated repo ...
Access to model X is restricted. You must have access to it and be authenticated.
Ungated/cached models load fine; only gated downloads fail
```

## Root cause
huggingface_hub reads the token from \$HF_HOME/token. Jobs export HF_HOME=/home/\<user>/hf_cache, but a plain `hf auth login` writes ~/.cache/huggingface/token, so jobs run anonymously. Reads as a permissions problem; is a path problem.

## Fix
Log in with the job's HF_HOME set: HF_HOME=/home/\<user>/hf_cache hf auth login  (token lands at \$HF_HOME/token, covers both login-node and sbatch --export=ALL jobs). Moving the cache orphans the token.

## Failed attempts
- Diagnosing with model_info('\<gated repo>') — HF serves gated repo METADATA publicly, so it succeeds anonymously and proves nothing
- Putting HF_TOKEN in a secrets file sourced only by the SLURM env script — login-node work stays anonymous

## Verify
HF_HOME=\<cache> python -c "from huggingface_hub import whoami; print(whoami()['name'])"  (LocalTokenNotFoundError => path problem); then HF_HOME=\<cache> python -c "from huggingface_hub import hf_hub_download; print(hf_hub_download('black-forest-labs/FLUX.1-dev','model_index.json'))"  (401 here with a username above => licence not accepted)

## Stack
| | |
|---|---|
| huggingface_hub | 0.36.x / 1.x |
| cluster | VT ARC |

<small>created 2026-10-06 · id `gatedrepoerror-401-in-jobs-despite-hf-auth-login-token-lives-c49d`</small>

## Notes

<!-- callcentre:end -->
Source commit b8617a6. Also: `hf`/`huggingface-cli` exist only inside the conda env, not on base PATH.
