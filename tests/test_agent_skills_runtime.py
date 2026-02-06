from pathlib import Path

from core.config import RuntimeConfig
from core.mcp_server import AgentSkillsMCPServer, _normalize_script_args
from core.parser import SkillParser
from core.repository import SkillRepository
from core.runtime import SkillRuntime


def _write_instructional_skill(tmp_path: Path) -> Path:
    skill_dir = tmp_path / "guidance_skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        """
---
name: guidance-skill
description: Example guidance-only skill
license: MIT
entrypoint: scripts/run.py
input_schema:
  type: object
  properties:
    text:
      type: string
---
Use this skill to demonstrate guidance-first behavior.
""".strip(),
        encoding="utf-8",
    )
    return skill_dir


def _write_script_skill(tmp_path: Path) -> Path:
    skill_dir = tmp_path / "script_skill"
    script_dir = skill_dir / "scripts"
    script_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        """
---
name: script-skill
description: Example script-backed skill
---
Run the bundled script for automation.
""".strip(),
        encoding="utf-8",
    )
    (script_dir / "run.py").write_text(
        """
import sys

print(" ".join(sys.argv[1:]))
""".strip(),
        encoding="utf-8",
    )
    return skill_dir


def test_parser_reads_frontmatter(tmp_path: Path) -> None:
    skill_dir = _write_instructional_skill(tmp_path)
    parser = SkillParser()
    definition = parser.parse(skill_dir / "SKILL.md")
    assert definition.name == "guidance-skill"
    assert definition.license == "MIT"
    assert definition.body_markdown.startswith("Use this skill")
    assert "entrypoint" not in definition.metadata


def test_repository_discovers_skills(tmp_path: Path) -> None:
    _write_instructional_skill(tmp_path)
    repo = SkillRepository(tmp_path)
    skills = repo.discover()
    assert len(skills) == 1
    assert skills[0].name == "guidance-skill"


def test_runtime_runs_script(tmp_path: Path) -> None:
    skill_dir = _write_script_skill(tmp_path)
    skill = SkillParser().parse(skill_dir / "SKILL.md")
    runtime = SkillRuntime(timeout_seconds=5)
    result = runtime.run_script(skill, "scripts/run.py", ["hello", "world"])
    assert result.success is True
    assert result.output["stdout"].strip() == "hello world"


def test_runtime_accepts_windows_style_script_path(tmp_path: Path) -> None:
    skill_dir = _write_script_skill(tmp_path)
    skill = SkillParser().parse(skill_dir / "SKILL.md")
    runtime = SkillRuntime(timeout_seconds=5)
    result = runtime.run_script(skill, "scripts\\run.py", ["hello"])
    assert result.success is True
    assert result.output["stdout"].strip() == "hello"


def test_mcp_server_registers_tools(tmp_path: Path) -> None:
    _write_instructional_skill(tmp_path)
    config = RuntimeConfig(skills_dir=str(tmp_path), timeout_seconds=5, reload_interval_seconds=0, log_level="INFO")
    server = AgentSkillsMCPServer(config)
    import asyncio

    tools = asyncio.run(server._mcp.get_tools())
    tool_names = {tool.name for tool in tools.values()}
    assert {"list_skills", "describe_skill", "load_skill_body", "list_skill_resources", "run_skill_script"}.issubset(
        tool_names
    )


def test_run_skill_script_accepts_json_args(tmp_path: Path) -> None:
    _write_script_skill(tmp_path)
    args = _normalize_script_args("[\"hello\", \"world\"]")
    assert args == ["hello", "world"]
