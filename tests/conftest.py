import os
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SERVER = ROOT / "server.py"

NCCL = dict(kind="fix",
    title="GRPO multi-node NCCL watchdog timeout during vLLM generation",
    symptoms=[
        "[rank3]: Watchdog caught collective operation timeout: WorkNCCL(SeqNum=883, OpType=ALLREDUCE) ran for 1800043 milliseconds",
        "job 48812345 on tc-gpu017, 2 nodes x 4 H200, hangs at first rollout",
        "slurmstepd: error: *** JOB 48812345 ON tc-gpu017 CANCELLED AT 2026-09-20T10:32:01 ***"],
    fix="Launch vLLM engine before DDP init; raise c10d store timeout",
    domain=["rl-training", "infra"])

EVAL = dict(kind="fix",
    title="Eval accuracy drops while GRPO reward rises",
    symptoms=["reward rises steadily but gsm8k accuracy falls after a few hundred steps"],
    fix="Use the training chat template in the eval harness",
    root_cause="chat template mismatch between training and lm-eval",
    domain=["rl-training", "eval"])

NCCL_QUERY = ("job 49900001 on tc-dgx003 (4 nodes) hung. rank0: Watchdog caught collective "
              "operation timeout, OpType=ALLREDUCE, ran for 1800012 milliseconds")
EVAL_QUERY = "GRPO reward keeps going up but gsm8k accuracy is dropping"


@pytest.fixture
def cc(tmp_path, monkeypatch):
    monkeypatch.setenv("CALLCENTRE_HOME", str(tmp_path))
    import server
    monkeypatch.setattr(server, "HOME", tmp_path)
    monkeypatch.setattr(server, "ENTRIES", tmp_path / "entries")
    monkeypatch.setattr(server, "INDEX_DB", tmp_path / ".index.db")
    monkeypatch.setattr(server, "LOCK_FILE", tmp_path / ".lock")
    return server


def _saved_id(msg: str) -> str:
    m = re.match(r"(?:Saved as|Opened) ([a-z0-9-]+)", msg)
    assert m, msg
    return m.group(1)


def nccl_fix(cc) -> str:
    return _saved_id(cc.submit(**NCCL, verified_now=True))


def eval_fix(cc) -> str:
    return _saved_id(cc.submit(**EVAL, verified_now=True))


def saved_id(msg: str) -> str:
    return _saved_id(msg)


def ids(result_text: str) -> list[str]:
    return re.findall(r"^- \[([a-z0-9-]+)\]", result_text, re.M)


def entry_files(cc) -> list[Path]:
    return sorted(cc.ENTRIES.glob("*.md"))


def child_env(home) -> dict:
    return {**os.environ, "CALLCENTRE_HOME": str(home)}


PYTHON = sys.executable
