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


def run_in(home, stdin, *args) -> str:
    r = subprocess.run([PYTHON, str(SERVER), *args], env=child_env(home), input=stdin,
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return r.stdout


def test_report_and_curate_via_cli(seeded):
    cc, nccl, ev = seeded
    out = run_in(cc.HOME, "pip install flash-attn fails\nneeds --no-build-isolation\n",
                 "report", "flash-attn", "build", "fails", "--agent", "bash-bot",
                 "--domain", "env,infra")
    assert out.startswith("Queued"), out
    rid = out.split()[1]
    item, details = cc._read(cc._inbox() / f"{rid}.md")
    assert item["title"] == "flash-attn build fails" and item["agent"] == "bash-bot"
    assert item["domain"] == ["env", "infra"] and "--no-build-isolation" in details
    review = run(cc.HOME, "review")
    assert f"[{rid}] flash-attn build fails  (bash-bot" in review
    assert run(cc.HOME, "file", rid, nccl).startswith("Closed")
    assert run(cc.HOME, "retag", ev, "eval,rl-training").strip() == f"{ev} domain = ['eval', 'rl-training']."
    assert run(cc.HOME, "dismiss", rid, "dup").strip() == f"no unique inbox item for id {rid!r}"


def test_report_requires_details_on_stdin(cc):
    assert run_in(cc.HOME, "", "report", "empty").strip() == "title and details are required."


def test_curator_commands_with_missing_args_print_usage(cc):
    for args in (["merge", "a"], ["file", "a"], ["dismiss", "a"], ["retag", "a"]):
        assert run(cc.HOME, *args).startswith("usage: server.py"), args
