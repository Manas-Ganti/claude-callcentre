"""Agent inbox (`report`) and the curator's CLI-side operations."""
from conftest import EVAL, NCCL, NCCL_QUERY, entry_files, eval_fix, ids, nccl_fix, saved_id


def _entry(cc, eid):
    return cc._read(cc.ENTRIES / f"{eid}.md")[0]


def _report(cc, title="vLLM 0.6 ignores max_model_len from config", **kw):
    out = cc.report(title, kw.pop("details", "had to pass --max-model-len on the CLI"),
                    agent=kw.pop("agent", "agent-a"), **kw)
    assert out.startswith("Queued"), out
    return out.split()[1]


def test_report_goes_to_inbox_not_search(cc):
    rid = _report(cc, project="grpo-sweep", domain=["infra"])
    item, details = cc._read(cc._inbox() / f"{rid}.md")
    assert item["agent"] == "agent-a" and item["project"] == "grpo-sweep"
    assert item["domain"] == ["infra"] and details == "had to pass --max-model-len on the CLI"
    assert entry_files(cc) == []
    assert ids(cc.search("vLLM ignores max_model_len config")) == []


def test_report_requires_title_and_details(cc):
    assert "required" in cc.report("  ", "x")
    assert "required" in cc.report("title", "  \n")
    assert not cc._inbox().exists()


def test_report_ids_never_collide(cc):
    a, b = _report(cc), _report(cc)
    assert a != b and len(list(cc._inbox().glob("*.md"))) == 2


def test_file_inbox_item(cc):
    rid = _report(cc)
    eid = saved_id(cc.submit(kind="convention", title="Pass max-model-len to vLLM on the CLI",
                             symptoms=["vLLM ignores max_model_len set in config"],
                             fix="pass --max-model-len explicitly"))
    assert cc._file_inbox(rid, [eid[:20]]).startswith("Closed")
    assert not (cc._inbox() / f"{rid}.md").exists()
    done, details = cc._read(cc._inbox() / "done" / f"{rid}.md")
    assert done["filed_as"] == [eid] and done["closed"] and details


def test_file_rejects_unknown_entry_and_leaves_item(cc):
    rid = _report(cc)
    assert cc._file_inbox(rid, ["nope-0000"]).startswith("Not filed")
    assert (cc._inbox() / f"{rid}.md").exists()


def test_dismiss_inbox_item(cc):
    rid = _report(cc)
    assert "reason" in cc._dismiss_inbox(rid, " ")
    assert cc._dismiss_inbox(rid, "already covered by docs").startswith("Closed")
    assert cc._read(cc._inbox() / "done" / f"{rid}.md")[0]["dismissed"] == "already covered by docs"
    assert "no unique inbox item" in cc._dismiss_inbox(rid, "again")


def test_retag(cc):
    eid = nccl_fix(cc)
    assert "infra" in cc._retag(eid, ["infra", "nccl"])
    assert _entry(cc, eid)["domain"] == ["infra", "nccl"]
    assert "invalid id" in cc._retag("../x", ["a"])


def _second_nccl(cc):
    return saved_id(cc.submit(kind="fix", force=True,
        title="NCCL watchdog timeout in GRPO rollout on multiple nodes",
        symptoms=["Watchdog caught collective operation timeout OpType=ALLREDUCE",
                  "hangs at first rollout on 4 nodes"],
        fix="Set NCCL_SOCKET_IFNAME=ib0", failed_attempts=["raising NCCL_TIMEOUT alone"],
        root_cause="vLLM grabs the default process group", stack={"vllm": "0.6.3"},
        domain=["nccl"], notes="seen on the H200 partition", verified_now=True))


def test_merge(cc):
    keep, drop = nccl_fix(cc), _second_nccl(cc)
    cc.report_outcome(drop, True, note="worked on tc-gpu020")
    assert cc._merge(keep, drop) == f"Merged {drop} into {keep}."
    assert [p.stem for p in entry_files(cc)] == [keep]
    e, notes = cc._read(cc.ENTRIES / f"{keep}.md")
    assert e["domain"] == ["rl-training", "infra", "nccl"]
    assert e["symptoms"][:2] == NCCL["symptoms"][:2] and len(e["symptoms"]) == 4
    assert e["failed_attempts"] == ["raising NCCL_TIMEOUT alone"]
    assert e["root_cause"] == "vLLM grabs the default process group"
    assert e["stack"] == {"vllm": "0.6.3"}
    assert e["uses"] == 1 + 2 and e["status"] == "verified" and e["merged_from"] == [drop]
    assert e["fix"] == NCCL["fix"]
    assert "Set NCCL_SOCKET_IFNAME=ib0" in notes and "seen on the H200 partition" in notes
    assert len(e["outcome_notes"]) == 1
    assert ids(cc.search(NCCL_QUERY)) == [keep]


def test_merged_id_still_resolves(cc):
    keep, drop = nccl_fix(cc), _second_nccl(cc)
    cc._merge(keep, drop)
    assert f"id: {keep}" in cc.get(drop)
    assert keep in cc.report_outcome(drop, True)
    assert _entry(cc, keep)["uses"] == 1 + 1 + 1


def test_merge_open_issue_into_fix(cc):
    keep = nccl_fix(cc)
    iid = saved_id(cc.open_issue(title="Rollout hang on 8 nodes", symptoms=["hang at rollout"]))
    cc.log_attempt(iid, "bump timeout", "still hangs")
    cc._merge(keep, iid)
    assert any("bump timeout" in a for a in _entry(cc, keep)["failed_attempts"])


def test_merge_refusals(cc):
    keep = nccl_fix(cc)
    iid = saved_id(cc.open_issue(title="Rollout hang on 8 nodes", symptoms=["hang at rollout"]))
    assert "itself" in cc._merge(keep, keep[:12])
    assert "keep must be" in cc._merge(iid, keep)
    assert "no unique entry" in cc._merge(keep, "missing-0000")
    assert len(entry_files(cc)) == 2


def test_review_empty(cc):
    assert cc._review() == "Nothing to review."


def test_review_sections(cc):
    nccl, ev = nccl_fix(cc), eval_fix(cc)
    second = _second_nccl(cc)
    loose = saved_id(cc.submit(kind="fix", title="Wandb offline sync drops runs",
                               symptoms=["wandb sync skipped 3 runs"], fix="sync with --include-offline"))
    stale = saved_id(cc.submit(kind="fix", title="Old flash-attn wheel crash", domain=["env"],
                               symptoms=["undefined symbol in flash_attn_2_cuda"], fix="pin 2.5.8"))
    cc.report_outcome(stale, False); cc.report_outcome(stale, False)
    iid = saved_id(cc.open_issue(title="Reward NaN after step 400", symptoms=["loss is nan"],
                                 domain=["rl-training"]))
    rid = _report(cc, project="grpo-sweep")
    (cc.ENTRIES / "broken-0000.md").write_text("---\nkey: [unclosed\n---\n")
    out = cc._review()
    sec = {b.split("\n")[0]: b for b in out.split("\n\n")}
    assert f"[{rid}]" in sec["## Inbox (1)"] and "grpo-sweep" in sec["## Inbox (1)"]
    assert f"{nccl} ~ {second}" in sec["## Possible duplicates (1)"]
    assert "broken-0000.md" in sec["## Unparseable files (1)"]
    assert loose in sec["## Untagged (no domain) (1)"]
    assert stale in sec["## Stale (1)"]
    assert loose in sec["## Unverified (1)"] and ev not in sec["## Unverified (1)"]
    assert iid in sec["## Open issues (1)"] and "OPEN (unclaimed" in sec["## Open issues (1)"]
    assert out.splitlines()[-1].startswith("Domains in use: rl-training (3)")
