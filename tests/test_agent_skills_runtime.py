from pathlib import Path

from agent_skills_runtime.config import RuntimeConfig
from agent_skills_runtime.mcp_server import AgentSkillsMCPServer
from agent_skills_runtime.models import SkillInvocation
from agent_skills_runtime.parser import SkillParser
from agent_skills_runtime.registry import SkillRegistry
from agent_skills_runtime.repository import SkillRepository
from agent_skills_runtime.runtime import SkillRuntime


def _write_skill(tmp_path: Path) -> Path:
    skill_dir = tmp_path / "sample_skill"
    script_dir = skill_dir / "scripts"
    script_dir.mkdir(parents=True)
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(
        """
---
name: sample-skill
description: Example skill
version: 1.0.0
entrypoint: scripts/run.py
input_schema:
  type: object
  properties:
    text:
      type: string
  required: [text]
output_schema:
  type: object
  properties:
    result:
      type: string
---
""".strip(),
        encoding="utf-8",
    )
    (script_dir / "run.py").write_text(
        """
import json
import sys

payload = json.loads(sys.stdin.read() or "{}")
text = payload.get("input", {}).get("text", "")
print(json.dumps({"result": text.upper()}))
""".strip(),
        encoding="utf-8",
    )
    return skill_dir


def test_parser_reads_frontmatter(tmp_path: Path) -> None:
    skill_dir = _write_skill(tmp_path)
    parser = SkillParser()
    definition = parser.parse(skill_dir / "SKILL.md")
    assert definition.name == "sample-skill"
    assert definition.entrypoint == "scripts/run.py"
    assert definition.input_schema["type"] == "object"


def test_repository_discovers_skills(tmp_path: Path) -> None:
    _write_skill(tmp_path)
    repo = SkillRepository(tmp_path)
    skills = repo.discover()
    assert len(skills) == 1
    assert skills[0].name == "sample-skill"


def test_runtime_invokes_skill(tmp_path: Path) -> None:
    skill_dir = _write_skill(tmp_path)
    skill = SkillParser().parse(skill_dir / "SKILL.md")
    runtime = SkillRuntime(timeout_seconds=5)
    result = runtime.invoke(skill, SkillInvocation(skill_name=skill.name, payload={"text": "hello"}))
    assert result.success is True
    assert result.output["result"] == "HELLO"


def test_mcp_server_registers_tools(tmp_path: Path) -> None:
    _write_skill(tmp_path)
    config = RuntimeConfig(skills_dir=str(tmp_path), timeout_seconds=5, reload_interval_seconds=0, log_level="INFO")
    server = AgentSkillsMCPServer(config)
    import asyncio

    tools = asyncio.run(server._mcp.get_tools())
    tool_names = {tool.name for tool in tools.values()}
    assert {"list_skills", "get_skill", "invoke_skill", "reload_skills"}.issubset(tool_names)
