import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from fastmcp import FastMCP

from .config import RuntimeConfig
from .logging_utils import configure_logging
from .registry import SkillRegistry
from .repository import SkillRepository
from .runtime import SkillRuntime

logger = logging.getLogger(__name__)


def _normalize_script_args(args: Union[List[str], str, None]) -> Union[Optional[List[str]], Dict[str, str]]:
    if args is None:
        return None
    if isinstance(args, list):
        return [str(arg) for arg in args]
    if isinstance(args, str):
        try:
            parsed = json.loads(args)
        except json.JSONDecodeError as exc:
            return {"error": f"Invalid args JSON string: {exc}"}
        if not isinstance(parsed, list):
            return {"error": "Invalid args JSON string: expected a JSON list"}
        return [str(arg) for arg in parsed]
    return {"error": "Invalid args: expected a list of strings or JSON list string"}


class AgentSkillsMCPServer:
    def __init__(self, config: RuntimeConfig) -> None:
        self.config = config
        configure_logging(config.log_level)
        self._mcp = FastMCP("Agent-Skills")
        self._repository = SkillRepository(Path(config.skills_dir))
        self._registry = SkillRegistry(self._repository)
        self._runtime = SkillRuntime(timeout_seconds=config.timeout_seconds)
        self._register_tools()

        if config.reload_interval_seconds > 0:
            asyncio.create_task(self._auto_reload())

    def _register_tools(self) -> None:
        @self._mcp.tool(description="List all available skills with their metadata")
        async def list_skills() -> Dict[str, Any]:
            skills = self._registry.list_skills()
            return {
                "skills": [
                    {
                        "name": skill.name,
                        "description": skill.description,
                        "license": skill.license,
                        "has_scripts": bool(skill.scripts),
                    }
                    for skill in skills
                ]
            }

        @self._mcp.tool(description="Describe a specific skill and its metadata")
        async def describe_skill(skill_name: str) -> Dict[str, Any]:
            skill = self._registry.get_skill(skill_name)
            if not skill:
                return {"error": f"Skill '{skill_name}' not found"}
            return {
                "name": skill.name,
                "description": skill.description,
                "path": str(skill.path),
                "license": skill.license,
                "metadata": skill.metadata,
                "has_scripts": bool(skill.scripts),
            }

        @self._mcp.tool(description="Load the full markdown body of a skill")
        async def load_skill_body(skill_name: str) -> Dict[str, Any]:
            skill = self._registry.get_skill(skill_name)
            if not skill:
                return {"error": f"Skill '{skill_name}' not found"}
            return {"name": skill.name, "body_markdown": skill.body_markdown}

        @self._mcp.tool(description="List the resources bundled with a skill")
        async def list_skill_resources(skill_name: str) -> Dict[str, Any]:
            skill = self._registry.get_skill(skill_name)
            if not skill:
                return {"error": f"Skill '{skill_name}' not found"}
            return {
                "name": skill.name,
                "references": skill.references,
                "scripts": skill.scripts,
                "assets": skill.assets,
            }

        @self._mcp.tool(description="Run a script bundled with a skill")
        async def run_skill_script(
            skill_name: str,
            script_name: str,
            args: Union[List[str], str, None] = None,
        ) -> Dict[str, Any]:
            skill = self._registry.get_skill(skill_name)
            if not skill:
                return {"error": f"Skill '{skill_name}' not found"}
            normalized_args = _normalize_script_args(args)
            if isinstance(normalized_args, dict):
                return normalized_args
            result = await asyncio.to_thread(self._runtime.run_script, skill, script_name, normalized_args)
            return {"success": result.success, "output": result.output, "error": result.error}

        @self._mcp.tool(description="Reload all skills from disk to pick up any changes")
        async def reload_skills() -> Dict[str, Any]:
            self._registry.reload()
            return {"status": "reloaded", "count": len(self._registry.list_skills())}

    async def _auto_reload(self) -> None:
        while True:
            await asyncio.sleep(self.config.reload_interval_seconds)
            self._registry.reload()

    def run(self, transport: str | None = None, **transport_kwargs: Any) -> None:
        self._mcp.run(transport=transport, **transport_kwargs)
