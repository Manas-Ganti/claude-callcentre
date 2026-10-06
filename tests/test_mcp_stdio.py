import asyncio
import os

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from conftest import PYTHON, SERVER

TOOLS = {"search", "get", "submit", "report_outcome", "open_issue", "claim_issue", "log_attempt",
         "resolve_issue", "report"}


def _text(result) -> str:
    is_error = getattr(result, "is_error", None)  # mcp 2.x
    if is_error is None:
        is_error = result.isError  # mcp 1.x
    assert not is_error, result
    return "".join(c.text for c in result.content if getattr(c, "type", "") == "text")


def test_stdio_round_trip(tmp_path):
    params = StdioServerParameters(command=PYTHON, args=[str(SERVER)],
                                   env={"CALLCENTRE_HOME": str(tmp_path), "PATH": os.environ["PATH"]})

    async def main():
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                init = await session.initialize()
                assert "search" in init.instructions and "report_outcome" in init.instructions

                tools = (await session.list_tools()).tools
                assert {t.name for t in tools} == TOOLS and len(tools) == len(TOOLS)
                assert all(t.description and t.description.strip() for t in tools)

                saved = _text(await session.call_tool("submit", {
                    "kind": "fix", "title": "FSDP checkpoint load hangs on resume",
                    "symptoms": ["resume from step_1200 hangs in load_state_dict",
                                 "py-spy shows all ranks in dist.barrier"],
                    "fix": "Use FULL_STATE_DICT with rank0_only and broadcast",
                    "stack": {"torch": "2.5.1", "accelerate": "1.2"},
                    "domain": ["rl-training"], "verified_now": True}))
                assert saved.startswith("Saved as"), saved
                eid = saved.split()[2]

                found = _text(await session.call_tool("search", {
                    "query": "load_state_dict hangs on resume, all ranks in dist.barrier"}))
                assert f"[{eid}]" in found

                full = _text(await session.call_tool("get", {"id": eid}))
                assert "resume from step_1200 hangs in load_state_dict" in full
                assert "py-spy shows all ranks in dist.barrier" in full
                assert "torch: 2.5.1" in full and "accelerate: '1.2'" in full

                queued = _text(await session.call_tool("report", {
                    "title": "vLLM 0.6 ignores max_model_len from config",
                    "details": "had to pass --max-model-len on the CLI\nconfig value silently ignored",
                    "agent": "stdio-test", "domain": ["infra"]}))
                assert queued.startswith("Queued"), queued

        assert (tmp_path / "entries" / f"{eid}.md").exists()
        assert len(list((tmp_path / "inbox").glob("*.md"))) == 1

    asyncio.run(main())
