import pytest

from conftest import EVAL_QUERY, NCCL_QUERY, eval_fix, ids, nccl_fix, saved_id


@pytest.fixture
def seeded(cc):
    return cc, nccl_fix(cc), eval_fix(cc)


NO_MATCH = "No matches."

# (query, expectation) where expectation is "nccl" / "eval" (returned, not WEAK), "none", or "weak"
CASES = [
    (NCCL_QUERY, "nccl"),
    ("torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 2.00 GiB\n"
     "slurmstepd: error: *** JOB 499 ON tc-gpu002 CANCELLED AT 2026-10-04T11:00:01 ***", "none"),
    ("slurmstepd: error: *** JOB 1234567 ON tc-gpu002 CANCELLED AT 2026-10-04T11:00:01 DUE TO TIME LIMIT ***",
     "none"),
    (EVAL_QUERY, "eval"),
    ("training job failed with an error", "weak"),
]


@pytest.mark.parametrize("query,expect", CASES)
def test_matching_table(seeded, query, expect):
    cc, nccl, ev = seeded
    out = cc.search(query)
    hits = ids(out)
    if expect == "none":
        assert hits == [] and out.startswith(NO_MATCH), out
    elif expect == "weak":
        lines = [l for l in out.splitlines() if l.startswith("- [")]
        assert all("WEAK" in l for l in lines), out
    else:
        want = {"nccl": nccl, "eval": ev}[expect]
        assert want in hits, out
        line = next(l for l in out.splitlines() if l.startswith(f"- [{want}]"))
        assert "WEAK" not in line, out


@pytest.mark.parametrize("q", ["", "   ", "\n\t \n"])
def test_whitespace_query(cc, q):
    assert cc.search(q) == "Query has no searchable terms."


@pytest.mark.parametrize("raw,gone", [
    ("job 48812345 failed", "48812345"),
    ("node tc-gpu017 down", "tc-gpu017"),
    ("[rank3]: Watchdog caught", "[rank3]"),
    ("2026-09-20T10:32:01 started", "2026"),
    ("at 10:32:01.123 started", "10:32"),
    ("segfault at 0x7f3a9c00beef", "0x7f3a"),
    ("ran for 1800043 milliseconds", "1800043"),
    ("tried to allocate 2.00 GiB", "2.00"),
])
def test_normalize_removes_noise(cc, raw, gone):
    assert gone not in cc._normalize(raw)


def test_normalize_paths_and_kept_tokens(cc):
    assert cc._normalize('File "/long/path/to/grpo_trainer.py", line 412') .split()[:2] == \
        ['File', '"grpo_trainer.py",']
    assert "grpo_trainer.py" in cc._normalize("/long/path/to/grpo_trainer.py")
    assert "/long/path" not in cc._normalize("/long/path/to/grpo_trainer.py")
    kept = cc._normalize("2 nodes x 4 H200 and A100 in bf16 vs fp16 on gsm8k")
    for tok in ("H200", "A100", "bf16", "fp16", "gsm8k"):
        assert tok in kept, kept


def test_domain_filter(seeded):
    cc, _, ev = seeded
    assert ev in ids(cc.search(EVAL_QUERY))
    assert ev not in ids(cc.search(EVAL_QUERY, domain="infra"))


def test_kind_filter(seeded):
    cc, nccl, _ = seeded
    iid = saved_id(cc.open_issue(title="NCCL watchdog timeout on 8 nodes", force=True,
                                 symptoms=["Watchdog caught collective operation timeout OpType=ALLREDUCE"]))
    both = ids(cc.search(NCCL_QUERY))
    assert nccl in both and iid in both
    assert ids(cc.search(NCCL_QUERY, kind="open_issue")) == [iid]
    assert ids(cc.search(NCCL_QUERY, kind="fix")) == [nccl]


def test_stale_hidden_by_default(seeded):
    cc, nccl, _ = seeded
    cc.report_outcome(nccl, False)
    cc.report_outcome(nccl, False)
    assert nccl not in ids(cc.search(NCCL_QUERY))
    out = cc.search(NCCL_QUERY, include_stale=True)
    assert nccl in ids(out) and "stale" in out


def _many(cc, n):
    for i in range(n):
        cc.submit(kind="convention", title=f"Checkpoint sharding convention variant {chr(97 + i)}",
                  symptoms=[f"where do checkpoint shards go for project {chr(97 + i)}"],
                  fix=f"save shards under /scratch/ckpt/{chr(97 + i)}", force=True)


@pytest.mark.parametrize("limit,expected", [(0, 1), (-5, 1), (1, 1), (3, 3), (10, 10), (50, 10)])
def test_limit_clamped(cc, limit, expected):
    _many(cc, 12)
    assert len(ids(cc.search("checkpoint sharding convention", limit=limit))) == expected


def test_default_limit_and_compact_output(cc):
    _many(cc, 8)
    out = cc.search("checkpoint sharding convention")
    assert len(ids(out)) == 5
    assert len(out) < 2000, len(out)
