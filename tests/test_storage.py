import os
import re

from conftest import NCCL, NCCL_QUERY, entry_files, eval_fix, ids, nccl_fix, saved_id


def test_submit_writes_one_file_that_round_trips(cc):
    eid = nccl_fix(cc)
    files = entry_files(cc)
    assert [p.name for p in files] == [f"{eid}.md"]
    assert files[0].read_text().startswith("---\n")
    e, notes = cc._read(files[0])
    assert e["id"] == eid
    assert e["kind"] == "fix"
    assert e["title"] == NCCL["title"]
    assert e["fix"] == NCCL["fix"]
    assert e["domain"] == NCCL["domain"]
    assert e["symptoms"] == NCCL["symptoms"][:2]
    assert e["status"] == "verified"
    assert e["uses"] == 1
    assert notes == ""


def test_id_format(cc):
    eid = saved_id(cc.submit(kind="convention", title="  Run lm-eval: the RIGHT way (v2)!! ",
                             symptoms=["how do I run gsm8k evals"], fix="use the wrapper"))
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*-[0-9a-f]{4}", eid)
    assert eid.startswith("run-lm-eval-the-right-way-v2-")
    assert re.fullmatch(r"[a-z0-9-]+-[0-9a-f]{4}", nccl_fix(cc))


def test_get_rejects_unsafe_ids(cc, monkeypatch):
    nccl_fix(cc)
    read = []
    orig = cc._read
    monkeypatch.setattr(cc, "_read", lambda p: (read.append(p), orig(p))[1])
    for bad in ("../../etc/passwd", "/etc/passwd", "a/b", "..", "UPPER"):
        assert cc.get(bad).startswith("invalid id"), bad
    assert read == []


def test_get_accepts_unique_prefix_and_rejects_ambiguous(cc):
    eid = nccl_fix(cc)
    eval_fix(cc)
    out = cc.get("grpo-multi")
    assert f"id: {eid}" in out
    assert NCCL["fix"] in out
    cc.submit(**NCCL, force=True)  # second grpo-multi-* entry
    assert "no unique entry" in cc.get("grpo-multi")
    assert "no unique entry" in cc.get("does-not-exist")


def test_get_omits_empty_and_internal_fields(cc):
    eid = nccl_fix(cc)
    cc.report_outcome(eid, False)
    out = cc.get(eid)
    for key in ("root_cause:", "failed_attempts:", "verify:", "stack:",
                "consecutive_failures:", "claim_expires:"):
        assert key not in out, key
    assert "fix:" in out and "symptoms:" in out


def test_generic_slurm_lines_dropped_but_rest_verbatim(cc):
    eid = nccl_fix(cc)
    e, _ = cc._read(cc.ENTRIES / f"{eid}.md")
    assert not any("CANCELLED AT" in s for s in e["symptoms"])
    assert e["symptoms"] == NCCL["symptoms"][:2]
    assert "48812345" in e["symptoms"][1] and "tc-gpu017" in e["symptoms"][1]


def test_all_generic_symptoms_kept(cc):
    only = ["slurmstepd: error: *** JOB 1234567 ON tc-gpu002 CANCELLED AT 2026-10-04T11:00:01 DUE TO TIME LIMIT ***",
            "srun: error: tc-gpu002: task 0: Exited with exit code 1"]
    eid = saved_id(cc.submit(kind="fix", title="Job killed at time limit", symptoms=only,
                             fix="request a longer --time"))
    e, _ = cc._read(cc.ENTRIES / f"{eid}.md")
    assert e["symptoms"] == only


def test_writes_leave_no_tmp_files(cc):
    eid = nccl_fix(cc)
    cc.report_outcome(eid, True, note="ok")
    cc.report_outcome(eid, False)
    iid = saved_id(cc.open_issue(title="Reward NaN after step 400", symptoms=["loss is nan"]))
    cc.claim_issue(iid, "a")
    cc.log_attempt(iid, "lower lr", "still nan", agent="a")
    cc.resolve_issue(iid, fix="clip grads", agent="a")
    assert list(cc.HOME.rglob("*.tmp")) == []


def test_hand_edit_is_picked_up_without_reindex(cc):
    eid = nccl_fix(cc)
    assert "Launch vLLM engine" in cc.search(NCCL_QUERY)
    p = cc.ENTRIES / f"{eid}.md"
    st = p.stat()
    p.write_text(p.read_text().replace("Launch vLLM engine before DDP init",
                                       "Set NCCL_ASYNC_ERROR_HANDLING and relaunch"))
    os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns + 5_000_000_000))
    out = cc.search(NCCL_QUERY)
    assert "Set NCCL_ASYNC_ERROR_HANDLING" in out
    assert "Launch vLLM engine" not in out


def test_deleted_file_leaves_search(cc):
    eid = nccl_fix(cc)
    assert ids(cc.search(NCCL_QUERY)) == [eid]
    (cc.ENTRIES / f"{eid}.md").unlink()
    assert ids(cc.search(NCCL_QUERY)) == []


def test_malformed_file_is_skipped(cc):
    eid = nccl_fix(cc)
    (cc.ENTRIES / "broken-0000.md").write_text("---\nkey: [unclosed\n---\n")
    assert ids(cc.search(NCCL_QUERY)) == [eid]
    assert ids(cc.search(NCCL_QUERY)) == [eid]  # stays usable on the next sync too


def test_deleting_index_loses_nothing(cc):
    n, e = nccl_fix(cc), eval_fix(cc)
    before = (ids(cc.search(NCCL_QUERY)), ids(cc.search("GRPO reward gsm8k accuracy")))
    assert before[0] == [n] and e in before[1]
    for p in cc.HOME.glob(".index.db*"):
        p.unlink()
    after = (ids(cc.search(NCCL_QUERY)), ids(cc.search("GRPO reward gsm8k accuracy")))
    assert after == before
    assert cc.INDEX_DB.exists()


def test_hand_written_entry_without_status_is_searchable(cc):
    cc.ENTRIES.mkdir(parents=True, exist_ok=True)
    (cc.ENTRIES / "hand-written-0001.md").write_text(
        "---\nid: hand-written-0001\nkind: fix\ntitle: Tokenizer pads on the wrong side\n"
        "symptoms:\n- generations are garbage after left padding in batched rollout\n"
        "fix: set tokenizer.padding_side = 'left' before generate\n---\n")
    out = cc.search("garbage generations with left padding in batched rollout")
    assert ids(out) == ["hand-written-0001"], out
    assert "(fix; unverified" in out and "None" not in out
