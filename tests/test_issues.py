import datetime as dt
import re

import pytest

from conftest import entry_files, ids, nccl_fix, saved_id

SYMS = ["ray actor died unexpectedly: RayActorError in rollout worker during weight sync"]
QUERY = "RayActorError rollout worker died during weight sync"


def _entry(cc, eid):
    return cc._read(cc.ENTRIES / f"{eid}.md")[0]


@pytest.fixture
def issue(cc):
    return cc, saved_id(cc.open_issue(title="Ray rollout worker dies during weight sync",
                                      symptoms=SYMS, domain=["rl-training"]))


def _summary(cc, eid, query=QUERY):
    out = cc.search(query)
    lines = out.splitlines()
    i = next(n for n, l in enumerate(lines) if l.startswith(f"- [{eid}]"))
    return lines[i] + "\n" + lines[i + 2]


def test_open_issue_created_and_searchable(issue):
    cc, iid = issue
    e = _entry(cc, iid)
    assert e["kind"] == "open_issue" and e["status"] == "open"
    assert "OPEN (unclaimed, 0 attempts logged)" in _summary(cc, iid)


def test_claim_conflict_and_extend(issue, monkeypatch):
    cc, iid = issue
    assert cc.claim_issue(iid, "agent-a").startswith("Claimed")
    first = _entry(cc, iid)["claim_expires"]
    out = cc.claim_issue(iid, "agent-b")
    assert "agent-a" in out and not out.startswith("Claimed")
    assert _entry(cc, iid)["claimed_by"] == "agent-a"
    assert "claimed by agent-a" in _summary(cc, iid)
    later = cc._now() + dt.timedelta(minutes=30)
    monkeypatch.setattr(cc, "_now", lambda: later)
    assert cc.claim_issue(iid, "agent-a").startswith("Claimed")
    assert _entry(cc, iid)["claim_expires"] > first


def test_lease_expiry(issue, monkeypatch):
    cc, iid = issue
    cc.claim_issue(iid, "agent-a", lease_minutes=60)
    later = cc._now() + dt.timedelta(minutes=61)
    monkeypatch.setattr(cc, "_now", lambda: later)
    assert cc.claim_issue(iid, "agent-b").startswith("Claimed")
    assert _entry(cc, iid)["claimed_by"] == "agent-b"


def test_log_attempt(issue):
    cc, iid = issue
    cc.log_attempt(iid, "raise ray heartbeat timeout", "still dies", agent="agent-a")
    out = cc.log_attempt(iid, "pin ray 2.9", "no change", agent="agent-b")
    assert "2 attempts" in out
    attempts = _entry(cc, iid)["attempts"]
    assert attempts == [f"[{cc._today()} agent-a] raise ray heartbeat timeout → still dies",
                        f"[{cc._today()} agent-b] pin ray 2.9 → no change"]
    assert "OPEN (unclaimed, 2 attempts logged)" in _summary(cc, iid)


def test_resolve_issue(issue):
    cc, iid = issue
    cc.claim_issue(iid, "agent-a")
    cc.log_attempt(iid, "raise ray heartbeat timeout", "still dies", agent="agent-a")
    out = cc.resolve_issue(iid, fix="Sync weights via NCCL broadcast instead of ray.put",
                           root_cause="object store spill", agent="agent-a")
    assert iid in out
    assert [p.stem for p in entry_files(cc)] == [iid]
    e = _entry(cc, iid)
    assert e["kind"] == "fix" and e["status"] == "verified" and e["uses"] == 1
    assert e["id"] == iid and e["resolved_by"] == "agent-a"
    assert len(e["failed_attempts"]) == 1 and "heartbeat" in e["failed_attempts"][0]
    assert "attempts" not in e and "claimed_by" not in e
    line = _summary(cc, iid)
    assert "(fix; verified" in line and "Sync weights via NCCL broadcast" in line
    assert ids(cc.search(QUERY, kind="open_issue")) == []


@pytest.mark.parametrize("call", [
    lambda cc, i: cc.claim_issue(i, "agent-a"),
    lambda cc, i: cc.log_attempt(i, "x", "y"),
    lambda cc, i: cc.resolve_issue(i, fix="z"),
])
def test_issue_tools_refuse_non_issues(cc, call):
    eid = nccl_fix(cc)
    p = cc.ENTRIES / f"{eid}.md"
    before = p.read_bytes(), p.stat().st_mtime_ns
    assert call(cc, eid) == "Not an open issue."
    assert (p.read_bytes(), p.stat().st_mtime_ns) == before


def test_open_issue_duplicate_guard(issue):
    cc, iid = issue
    out = cc.open_issue(title="Ray rollout worker dies during weight sync", symptoms=SYMS)
    assert out.startswith("Not saved") and iid in out
    assert len(entry_files(cc)) == 1
    forced = saved_id(cc.open_issue(title="Ray rollout worker dies during weight sync",
                                    symptoms=SYMS, force=True))
    assert forced != iid and len(entry_files(cc)) == 2
    assert re.fullmatch(r"[a-z0-9-]+-[0-9a-f]{4}", forced)


def test_expired_claim_shows_unclaimed_without_file_change(issue, monkeypatch):
    cc, iid = issue
    cc.claim_issue(iid, "agent-a", lease_minutes=60)
    assert "(open_issue; claimed" in _summary(cc, iid)
    assert "claimed by agent-a" in _summary(cc, iid)
    p = cc.ENTRIES / f"{iid}.md"
    before = p.stat().st_mtime_ns
    later = cc._now() + dt.timedelta(minutes=61)
    monkeypatch.setattr(cc, "_now", lambda: later)
    summary = _summary(cc, iid)
    assert "(open_issue; open" in summary
    assert "OPEN (unclaimed, 0 attempts logged)" in summary
    assert p.stat().st_mtime_ns == before  # search is read-only
