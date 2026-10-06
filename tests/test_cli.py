import subprocess

import pytest

from conftest import NCCL_QUERY, PYTHON, SERVER, child_env, eval_fix, nccl_fix, saved_id


def run(home, *args) -> str:
    r = subprocess.run([PYTHON, str(SERVER), *args], env=child_env(home),
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return r.stdout


@pytest.fixture
def seeded(cc):
    return cc, nccl_fix(cc), eval_fix(cc)


def test_search(seeded):
    cc, nccl, _ = seeded
    out = run(cc.HOME, "search", *NCCL_QUERY.split())
    assert f"[{nccl}]" in out


def test_search_no_match(cc):
    assert run(cc.HOME, "search", "test").startswith("No matches.")


def test_get(seeded):
    cc, nccl, _ = seeded
    out = run(cc.HOME, "get", nccl)
    assert f"id: {nccl}" in out and "Launch vLLM engine" in out


def test_open(seeded):
    cc, _, _ = seeded
    assert run(cc.HOME, "open").strip() == "No open issues."
    iid = saved_id(cc.open_issue(title="Reward NaN after step 400", symptoms=["loss is nan"]))
    assert run(cc.HOME, "open").strip() == f"- [{iid}] Reward NaN after step 400"


def test_reindex(seeded):
    cc, _, _ = seeded
    assert run(cc.HOME, "reindex").strip() == "indexed 2 entries"


@pytest.mark.parametrize("args", [["bogus"], ["help", "me"]])
def test_unknown_command(cc, args):
    assert run(cc.HOME, *args).startswith("usage: server.py")
