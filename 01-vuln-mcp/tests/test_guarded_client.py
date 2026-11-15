import asyncio
import json
from pathlib import Path

import pytest

from mcp_security_lab.guarded_client import main


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("changed", [False, True])
def test_live_metadata_gate(tmp_path, capsys, changed):
    baseline = json.loads(
        (PROJECT_ROOT / "review" / "approved_tools.json")
        .read_text(encoding="utf-8")
    )

    if changed:
        tool = baseline["servers"]["documents"]["tools"][0]
        tool["description"] += " Deliberate test mismatch."

    temporary_baseline = tmp_path / "approved_tools.json"
    temporary_baseline.write_text(
        json.dumps(baseline),
        encoding="utf-8",
    )

    exit_code = asyncio.run(
        asyncio.wait_for(
            main(baseline_path=temporary_baseline),
            timeout=30,
        )
    )
    output = capsys.readouterr().out

    if changed:
        assert exit_code == 1
        assert "BLOCKED: live tool definitions differ from approval." in output
        assert "APPROVED:" not in output
    else:
        assert exit_code == 0
        assert "APPROVED: requesting welcome document." in output
        assert "Welcome to Cedarbridge Labs." in output