"""The human (Obsidian) view: rendered entry bodies and the generated INDEX.md."""
import subprocess

from conftest import (NCCL, PYTHON, SERVER, child_env, entry_files, eval_fix, nccl_fix, saved_id)


def _text(cc, eid):
    return (cc.ENTRIES / f"{eid}.md").read_text()


def _body(text):
    return text.split("\n---\n", 1)[1]


def test_entry_body_is_rendered_from_frontmatter(cc):
    eid = nccl_fix(cc)
    body = _body(_text(cc, eid))
    assert body.startswith(cc._BEGIN) and body.rstrip().endswith(cc._END)
    assert f"# {NCCL['title']}" in body
    assert "> [!success] fix · verified · used 1×, failed 0× · last verified" in body
    assert "#rl-training #infra #kind/fix #status/verified" in body
    assert "## Symptoms\n```text\n" + NCCL["symptoms"][0] in body
    assert "## Fix\nLaunch vLLM engine before DDP init" in body
    for absent in ("## Root cause", "## Failed attempts", "## Verify", "## Stack", "## Notes"):
        assert absent not in body
    assert f"id `{eid}`" in body


def test_generated_view_is_not_data(cc):
    eid = saved_id(cc.submit(kind="fix", title="Tokenizer pads on the wrong side",
                             symptoms=["garbage generations after left padding"],
                             fix="set padding_side='left'", notes="seen twice in October"))
    e, notes = cc._read(cc.ENTRIES / f"{eid}.md")
    assert notes == "seen twice in October"
    assert "## Notes\n\n" + cc._END + "\nseen twice in October\n" in _text(cc, eid)
    for _ in range(3):
        cc.report_outcome(eid, True)
    text = _text(cc, eid)
    assert text.count(cc._BEGIN) == 1 and text.count("seen twice in October") == 1
    assert "used 3×" in text
    out = cc.get(eid)
    assert "callcentre:begin" not in out and "## Symptoms" not in out
    assert out.endswith("notes:\nseen twice in October")


def test_obsidian_syntax_is_neutralised_outside_code(cc):
    eid = saved_id(cc.submit(
        kind="fix", title="source activate <env> keeps base python",
        symptoms=["python is $HOME/miniconda3/bin/python, not <env>"],
        fix='export PY="$CONDA_ENV/bin/python" and call `"$PY" -c "import <mod>"` #important',
        domain=["vt arc", "2024"], stack={"conda": "24.1 | miniforge"}))
    body = _body(_text(cc, eid))
    assert "# source activate \\<env> keeps base python" in body
    assert 'export PY="\\$CONDA_ENV/bin/python" and call `"$PY" -c "import <mod>"` \\#important' in body
    assert "python is $HOME/miniconda3/bin/python, not <env>" in body  # verbatim inside the fence
    assert "#vt-arc #t-2024 " in body
    assert "| conda | 24.1 / miniforge |" in body


def test_symptom_with_backticks_gets_longer_fence(cc):
    eid = saved_id(cc.submit(kind="fix", title="Fence in symptom",
                             symptoms=["log shows ```python\nboom```"], fix="x"))
    assert "````text\nlog shows ```python" in _text(cc, eid)


def test_open_issue_and_resolved_views(cc):
    iid = saved_id(cc.open_issue(title="Reward NaN after step 400", symptoms=["loss is nan"],
                                 repro="run grpo.sh for 400 steps"))
    cc.claim_issue(iid, "agent-a")
    cc.log_attempt(iid, "lower lr", "still nan", agent="agent-a")
    body = _body(_text(cc, iid))
    assert "> [!bug] open issue · claimed · 1 attempts logged · claimed by agent-a until" in body
    assert "## Repro\nrun grpo.sh for 400 steps" in body
    assert "## Attempts so far\n- [" in body and "lower lr → still nan" in body
    cc.resolve_issue(iid, fix="clip grads at 1.0", agent="agent-a")
    body = _body(_text(cc, iid))
    assert "> [!success] fix · verified" in body
    assert "## Failed attempts\n- [" in body and "resolved by agent-a" in body


def test_index_note(cc):
    nccl, ev = nccl_fix(cc), eval_fix(cc)
    iid = saved_id(cc.open_issue(title="Reward NaN after step 400", symptoms=["loss is nan"]))
    cc.log_attempt(iid, "lower lr", "still nan")
    loose = saved_id(cc.submit(kind="convention", title="Name wandb runs by sweep",
                               symptoms=["which wandb run name"], fix="sweep-id/seed"))
    rid = cc.report("vLLM ignores max_model_len", "pass it on the CLI").split()[1]
    idx = (cc.HOME / "INDEX.md").read_text()
    assert idx.startswith("---\ntags: [callcentre/index]\n---\n# Call centre")
    assert "> 3 entries · 1 open issues · 1 inbox items awaiting curation" in idx
    assert f"## Open issues (1)\n- 🔴 [[{iid}|Reward NaN after step 400]] · 1 attempts" in idx
    rl = idx.split("## rl-training (2)\n", 1)[1].split("\n\n", 1)[0]
    assert f"[[{ev}|Eval accuracy drops while GRPO reward rises]] · used 1×" in rl and nccl in rl
    assert f"## infra (1)\n- ✅ [[{nccl}|" in idx and f"## eval (1)\n- ✅ [[{ev}|" in idx
    assert f"## untagged (1)\n- 🆕 [[{loose}|Name wandb runs by sweep]]" in idx
    assert idx.index("## rl-training") < idx.index("## eval") < idx.index("## untagged")
    assert f"## Inbox (1)\n- [[{rid}|vLLM ignores max_model_len]]" in idx


def test_index_follows_merges_and_inbox_and_avoids_churn(cc):
    nccl, ev = nccl_fix(cc), eval_fix(cc)
    rid = cc.report("vLLM ignores max_model_len", "pass it on the CLI").split()[1]
    cc._merge(nccl, ev)
    cc._dismiss_inbox(rid, "covered")
    idx_path = cc.HOME / "INDEX.md"
    idx = idx_path.read_text()
    assert ev not in idx and "## Inbox" not in idx and "0 inbox items" in idx
    before = idx_path.stat().st_mtime_ns
    assert cc.submit(**NCCL).startswith("Not saved")  # locked, but nothing changed
    assert idx_path.stat().st_mtime_ns == before


def test_index_note_title_sanitised(cc):
    eid = saved_id(cc.submit(kind="fix", title="a|b [x] #y", symptoms=["s"], fix="f"))
    assert f"[[{eid}|a b  x   y]]" in (cc.HOME / "INDEX.md").read_text()


def test_render_upgrades_legacy_files(cc):
    cc.ENTRIES.mkdir(parents=True)
    legacy = ("---\nid: legacy-0001\nkind: fix\ntitle: Old style entry\nsymptoms:\n- boom\n"
              "fix: do the thing\nstatus: verified\nuses: 2\nfailures: 0\n---\nhand notes here\n")
    (cc.ENTRIES / "legacy-0001.md").write_text(legacy)
    (cc.ENTRIES / "broken-0002.md").write_text("---\nkey: [unclosed\n---\n")
    before = cc._read(cc.ENTRIES / "legacy-0001.md")
    r = subprocess.run([PYTHON, str(SERVER), "render"], env=child_env(cc.HOME),
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0 and r.stdout.strip() == \
        "rendered 1 entries; skipped unparseable: broken-0002.md"
    assert cc._read(cc.ENTRIES / "legacy-0001.md") == before
    text = (cc.ENTRIES / "legacy-0001.md").read_text()
    assert "# Old style entry" in text and text.endswith(f"{cc._END}\nhand notes here\n")
    assert "[[legacy-0001|Old style entry]] · used 2×" in (cc.HOME / "INDEX.md").read_text()
    assert len(entry_files(cc)) == 2


LEGACY = ("---\nid: legacy-0001\nkind: fix\ntitle: Old style entry\nsymptoms:\n- boom\n"
          "fix: do the thing\nstatus: unverified\nuses: 0\nfailures: 0\n---\nhand notes\n")


def test_render_missing_only_touches_outdated_files(cc):
    nccl = nccl_fix(cc)
    (cc.ENTRIES / "legacy-0001.md").write_text(LEGACY)
    current = cc.ENTRIES / f"{nccl}.md"
    before = current.stat().st_mtime_ns
    assert cc._render_missing() == 1
    assert "# Old style entry" in (cc.ENTRIES / "legacy-0001.md").read_text()
    assert cc._read(cc.ENTRIES / "legacy-0001.md")[1] == "hand notes"
    assert current.stat().st_mtime_ns == before
    assert cc._render_missing() == 0


def test_render_missing_on_empty_home(cc):
    assert cc._render_missing() == 0
