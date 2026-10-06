from conftest import NCCL, entry_files, nccl_fix, saved_id


def _entry(cc, eid):
    return cc._read(cc.ENTRIES / f"{eid}.md")[0]


def _unverified(cc):
    return saved_id(cc.submit(**NCCL))


def test_unverified_submit(cc):
    e = _entry(cc, _unverified(cc))
    assert e["status"] == "unverified"
    assert e["uses"] == 0
    assert e["last_verified"] is None


def test_success_verifies(cc):
    eid = _unverified(cc)
    cc.report_outcome(eid, False)
    assert _entry(cc, eid)["consecutive_failures"] == 1
    cc.report_outcome(eid, True)
    e = _entry(cc, eid)
    assert e["status"] == "verified"
    assert e["uses"] == 1
    assert e["last_verified"] == cc._today()
    assert e["consecutive_failures"] == 0


def test_two_consecutive_failures_go_stale_and_recover(cc):
    eid = nccl_fix(cc)
    cc.report_outcome(eid, False)
    assert _entry(cc, eid)["status"] == "verified"
    out = cc.report_outcome(eid, False)
    assert "stale" in out
    assert _entry(cc, eid)["status"] == "stale"
    cc.report_outcome(eid, True)
    e = _entry(cc, eid)
    assert e["status"] == "verified" and e["failures"] == 2 and e["consecutive_failures"] == 0


def test_interleaved_failures_never_stale(cc):
    eid = nccl_fix(cc)
    for _ in range(5):
        cc.report_outcome(eid, False)
        cc.report_outcome(eid, True)
        assert _entry(cc, eid)["status"] == "verified"
    assert _entry(cc, eid)["failures"] == 5


def test_outcome_notes_capped_at_ten(cc):
    eid = nccl_fix(cc)
    for i in range(13):
        cc.report_outcome(eid, True, note=f"note {i}")
    notes = _entry(cc, eid)["outcome_notes"]
    assert len(notes) == 10
    assert notes[0].endswith("note 3") and notes[-1].endswith("note 12")
    assert notes[-1].startswith(f"{cc._today()} OK:")


def test_duplicate_guard(cc):
    eid = nccl_fix(cc)
    out = cc.submit(**NCCL)
    assert out.startswith("Not saved") and eid in out
    assert len(entry_files(cc)) == 1
    forced = saved_id(cc.submit(**NCCL, force=True))
    assert forced != eid
    assert len(entry_files(cc)) == 2
    assert _entry(cc, eid)["status"] == "verified"  # original not overwritten


def test_different_entry_not_flagged(cc):
    nccl_fix(cc)
    out = cc.submit(kind="fix", title="CUDA OOM in vLLM rollout with long completions",
                    symptoms=["torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 2.00 GiB"],
                    fix="lower gpu_memory_utilization to 0.6", domain=["rl-training"])
    assert out.startswith("Saved as"), out
    assert len(entry_files(cc)) == 2


def test_input_validation(cc):
    assert "open_issue" in cc.submit(kind="open_issue", title="x y", symptoms=["boom"], fix="f")
    assert "required" in cc.submit(kind="fix", title="x y", symptoms=["boom"], fix="   ")
    assert "required" in cc.submit(kind="fix", title="x y", symptoms=[], fix="do it")
    assert not cc.ENTRIES.exists() or entry_files(cc) == []


def test_report_outcome_on_open_issue_refused(cc):
    iid = saved_id(cc.open_issue(title="Reward NaN after step 400", symptoms=["loss is nan"]))
    before = (cc.ENTRIES / f"{iid}.md").read_text()
    out = cc.report_outcome(iid, True)
    assert "log_attempt" in out and "resolve_issue" in out
    assert (cc.ENTRIES / f"{iid}.md").read_text() == before
