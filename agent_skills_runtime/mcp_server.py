import asyncio
import logging
from pathlib import Path
from typing import Any, Dict

from fastmcp import FastMCP

from .config import RuntimeConfig
from .logging_utils import configure_logging
from .models import SkillInvocation
from .registry import SkillRegistry
from .repository import SkillRepository
from .runtime import SkillRuntime

logger = logging.getLogger(__name__)


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
        @self._mcp.tool()
        async def list_skills() -> Dict[str, Any]:
            skills = self._registry.list_skills()
            return {
                "skills": [
                    {
                        "name": skill.name,
                        "description": skill.description,
                        "version": skill.version,
                        "metadata": {k: v for k, v in skill.metadata.items() if k != "body"},
                        "input_schema": skill.input_schema,
                        "output_schema": skill.output_schema,
                    }
                    for skill in skills
                ]
            }

        @self._mcp.tool()
        async def get_skill(skill_name: str) -> Dict[str, Any]:
            skill = self._registry.get_skill(skill_name)
            if not skill:
                return {"error": f"Skill '{skill_name}' not found"}
            return {
                "name": skill.name,
                "description": skill.description,
                "version": skill.version,
                "entrypoint": skill.entrypoint,
                "path": str(skill.path),
                "input_schema": skill.input_schema,
                "output_schema": skill.output_schema,
                "metadata": skill.metadata,
            }

        @self._mcp.tool()
        async def invoke_skill(skill_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
            skill = self._registry.get_skill(skill_name)
            if not skill:
                return {"error": f"Skill '{skill_name}' not found"}
            invocation = SkillInvocation(skill_name=skill.name, payload=payload)
            result = await asyncio.to_thread(self._runtime.invoke, skill, invocation)
            return {
                "success": result.success,
                "output": result.output,
                "error": result.error,
            }

        @self._mcp.tool()
        async def reload_skills() -> Dict[str, Any]:
            self._registry.reload()
            return {"status": "reloaded", "count": len(self._registry.list_skills())}

    async def _auto_reload(self) -> None:
        while True:
            await asyncio.sleep(self.config.reload_interval_seconds)
            self._registry.reload()

    def run(self) -> None:
        self._mcp.run()
