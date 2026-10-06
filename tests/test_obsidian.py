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
    rl = idx.split("## [[domains/rl-training|rl-training]] (2)\n", 1)[1].split("\n\n", 1)[0]
    assert f"[[{ev}|Eval accuracy drops while GRPO reward rises]] · used 1×" in rl and nccl in rl
    assert f"## [[domains/infra|infra]] (1)\n- ✅ [[{nccl}|" in idx
    assert f"## [[domains/eval|eval]] (1)\n- ✅ [[{ev}|" in idx
    assert f"## [[domains/untagged|untagged]] (1)\n- 🆕 [[{loose}|Name wandb runs by sweep]]" in idx
    assert idx.index("|rl-training]]") < idx.index("|eval]]") < idx.index("|untagged]]")
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


def test_domain_hub_notes(cc):
    nccl, ev = nccl_fix(cc), eval_fix(cc)
    iid = saved_id(cc.open_issue(title="Reward NaN after step 400", symptoms=["loss is nan"],
                                 domain=["rl-training"]))
    hubs = cc.HOME / "domains"
    assert sorted(p.stem for p in hubs.glob("*.md")) == ["eval", "infra", "rl-training"]
    rl = (hubs / "rl-training.md").read_text()
    assert rl.startswith("---\ntags: [callcentre/domain]\n---\n# rl-training")
    assert "> #rl-training #callcentre/domain" in rl  # hub takes its domain's graph colour
    assert f"## Open issues (1)\n- 🔴 [[{iid}|" in rl
    assert f"## Entries (2)\n" in rl and nccl in rl and ev in rl
    cc._retag(ev, ["eval"])
    cc._retag(nccl, ["rl-training"])
    assert sorted(p.stem for p in hubs.glob("*.md")) == ["eval", "rl-training"]  # infra hub removed
    assert ev not in (hubs / "rl-training.md").read_text()


def _graph(cc, cfg=None):
    import json
    (cc.HOME / ".obsidian").mkdir(parents=True, exist_ok=True)
    (cc.HOME / ".obsidian" / "graph.json").write_text(json.dumps(cfg or {"search": "", "colorGroups": []}))


def _read_graph(cc):
    import json
    return json.loads((cc.HOME / ".obsidian" / "graph.json").read_text())


def test_graph_colour_groups(cc):
    _graph(cc)
    nccl_fix(cc), eval_fix(cc)
    saved_id(cc.open_issue(title="Reward NaN after step 400", symptoms=["loss is nan"],
                           domain=["rl-training"]))
    g = _read_graph(cc)
    queries = [x["query"] for x in g["colorGroups"]]
    # open issues first; then domains with >= 2 notes, rarest first (infra/eval have 1: no group)
    assert queries == ["tag:#kind/open_issue", "tag:#rl-training"]
    assert g["colorGroups"][0]["color"] == {"a": 1, "rgb": cc._OPEN_COLOR}
    assert g["search"] == cc.GRAPH_FILTER


def test_graph_merge_respects_user_choices(cc):
    mine = {"query": "path:projects", "color": {"a": 1, "rgb": 1}}
    _graph(cc, {"search": "-tag:#eval", "colorGroups": [
        mine, {"query": "tag:#rl-training", "color": {"a": 1, "rgb": 123}}], "scale": 2})
    nccl_fix(cc), eval_fix(cc)
    g = _read_graph(cc)
    assert g["search"] == "-tag:#eval" and g["scale"] == 2
    assert {"query": "tag:#rl-training", "color": {"a": 1, "rgb": 123}} in g["colorGroups"]
    assert g["colorGroups"][-1] == mine
    before = (cc.HOME / ".obsidian" / "graph.json").stat().st_mtime_ns
    cc.report_outcome(ids_of(cc)[0], True)
    assert (cc.HOME / ".obsidian" / "graph.json").stat().st_mtime_ns == before  # unchanged: no write


def ids_of(cc):
    return [p.stem for p in entry_files(cc)]


def test_graph_untouched_without_obsidian(cc):
    nccl_fix(cc)
    assert not (cc.HOME / ".obsidian").exists()


def test_graph_stable_colours_and_overflow(cc):
    cfg = cc._graph_config({}, {f"d{i:02d}": 2 + i for i in range(20)})
    groups = cfg["colorGroups"][1:]
    assert len(groups) == len(cc._PALETTE)  # extra domains stay uncoloured
    assert len({g["color"]["rgb"] for g in groups}) == len(groups)
    again = cc._graph_config(cfg, {**{f"d{i:02d}": 2 + i for i in range(20)}, "d00": 99})
    assert {g["query"]: g["color"] for g in again["colorGroups"]}["tag:#d19"] == \
        {g["query"]: g["color"] for g in groups}["tag:#d19"]
