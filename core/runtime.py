import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Optional

from .models import SkillDefinition, SkillInvocation, SkillResult

logger = logging.getLogger(__name__)


class SkillRuntime:
    def __init__(self, timeout_seconds: int = 30) -> None:
        self.timeout_seconds = timeout_seconds

    def invoke(self, skill: SkillDefinition, invocation: SkillInvocation) -> SkillResult:
        if not skill.entrypoint:
            return SkillResult(success=True, output={"body": skill.metadata.get("body", "")})

        entrypoint_path = (skill.path / skill.entrypoint).resolve()
        if not entrypoint_path.exists():
            return SkillResult(success=False, output={}, error=f"Entrypoint not found: {entrypoint_path}")

        command = self._build_command(entrypoint_path)
        payload = {
            "input": invocation.payload,
            "context": invocation.context,
            "skill": {
                "name": skill.name,
                "version": skill.version,
            },
        }

        try:
            result = subprocess.run(
                command,
                input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                capture_output=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return SkillResult(success=False, output={}, error="Skill invocation timed out")

        if result.returncode != 0:
            error_message = result.stderr.decode("utf-8", errors="replace")
            return SkillResult(success=False, output={}, error=error_message or "Skill execution failed")

        stdout = result.stdout.decode("utf-8", errors="replace")
        try:
            output = json.loads(stdout) if stdout.strip() else {}
        except json.JSONDecodeError:
            output = {"raw": stdout}
        return SkillResult(success=True, output=output)

    def _build_command(self, entrypoint: Path) -> list[str]:
        if entrypoint.suffix == ".py":
            return ["python", str(entrypoint)]
        return [str(entrypoint)]
