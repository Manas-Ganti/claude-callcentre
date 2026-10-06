"""Every Claude Code session runs its own server process, so these tests use real processes."""
import subprocess
import time

import pytest

from conftest import NCCL_QUERY, PYTHON, ROOT, child_env, entry_files, nccl_fix

pytestmark = pytest.mark.slow


def _spawn(home, code: str) -> subprocess.Popen:
    return subprocess.Popen([PYTHON, "-c", "import server\n" + code], cwd=ROOT, env=child_env(home),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def _finish(procs, timeout=120):
    outs = []
    for p in procs:
        out, err = p.communicate(timeout=timeout)
        assert p.returncode == 0, err
        outs.append(out)
    return outs


def test_parallel_report_outcome_no_lost_updates(cc):
    eid = nccl_fix(cc)
    start = cc._read(cc.ENTRIES / f"{eid}.md")[0]["uses"]
    outs = _finish([_spawn(cc.HOME, f"print(server.report_outcome({eid!r}, True))")
                    for _ in range(20)])
    assert all(o.startswith("Recorded.") for o in outs), outs
    assert cc._read(cc.ENTRIES / f"{eid}.md")[0]["uses"] == start + 20


def test_parallel_submits(cc):
    topics = ["tokenizer padding side", "wandb run naming", "slurm array sizing", "eval seed policy",
              "checkpoint retention", "dataset shuffling buffer", "reward model batching",
              "vllm tensor parallel layout"]
    code = ("import sys\nt = sys.argv[1]\n"
            "print(server.submit(kind='convention', title=f'Convention for {t}', "
            "symptoms=[f'how should we handle {t}'], fix=f'standard approach to {t}'))")
    procs = [subprocess.Popen([PYTHON, "-c", "import server\n" + code, t], cwd=ROOT,
                              env=child_env(cc.HOME), stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True) for t in topics]
    outs = _finish(procs)
    assert all(o.startswith("Saved as") for o in outs), outs
    files = entry_files(cc)
    assert len(files) == 8
    titles = {cc._read(p)[0]["title"] for p in files}
    assert titles == {f"Convention for {t}" for t in topics}
    assert list(cc.HOME.rglob("*.tmp")) == []


def test_search_during_writes_never_raises(cc):
    eid = nccl_fix(cc)
    searchers = [_spawn(cc.HOME, f"""
import time
end = time.time() + 4
n = 0
while time.time() < end:
    out = server.search({NCCL_QUERY!r})
    assert {eid!r} in out, out
    n += 1
print(n)
""") for _ in range(4)]
    writers = [_spawn(cc.HOME, f"""
for i in range(15):
    server.report_outcome({eid!r}, True, note=f'w{w} {{i}}')
    server.submit(kind='convention', title=f'writer {w} convention {{i}}',
                  symptoms=[f'unrelated topic {w} {{i}} zebra'], fix='x', force=True)
""") for w in range(4)]
    t0 = time.time()
    _finish(writers)
    counts = [int(o) for o in _finish(searchers)]
    assert all(c > 0 for c in counts), counts
    assert time.time() - t0 < 60
    assert cc._read(cc.ENTRIES / f"{eid}.md")[0]["uses"] == 1 + 60
    assert len(entry_files(cc)) == 1 + 60
