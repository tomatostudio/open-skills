import logging
import subprocess
from pathlib import Path
from typing import Optional, Sequence

from .models import SkillDefinition, SkillResult

logger = logging.getLogger(__name__)


class SkillRuntime:
    def __init__(self, timeout_seconds: int = 30) -> None:
        self.timeout_seconds = timeout_seconds

    def run_script(self, skill: SkillDefinition, script_name: str, args: Optional[Sequence[str]] = None) -> SkillResult:
        if not skill.scripts:
            return SkillResult(success=False, output={}, error="Skill has no scripts to execute")

        # Normalize script name and find matching script
        normalized_script = Path(script_name.replace("\\", "/")).as_posix()
        available_scripts = {Path(script.replace("\\", "/")).as_posix() for script in skill.scripts}
        
        # Try exact match first
        matched_script = None
        if normalized_script in available_scripts:
            matched_script = normalized_script
        else:
            # Try finding script by filename only
            script_filename = Path(normalized_script).name
            for available_script in available_scripts:
                if Path(available_script).name == script_filename:
                    matched_script = available_script
                    break
        
        if not matched_script:
            return SkillResult(success=False, output={}, error=f"Script '{script_name}' not found for skill")

        script_path = (skill.path / matched_script).resolve()
        if not script_path.exists():
            return SkillResult(success=False, output={}, error=f"Script not found: {script_path}")

        command = self._build_command(script_path)
        if args:
            command.extend(args)

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                timeout=self.timeout_seconds,
                check=False,
                cwd=str(skill.path),
            )
        except subprocess.TimeoutExpired:
            return SkillResult(success=False, output={}, error="Skill script execution timed out")

        stdout = result.stdout.decode("utf-8", errors="replace")
        stderr = result.stderr.decode("utf-8", errors="replace")
        output = {
            "stdout": stdout,
            "stderr": stderr,
            "returncode": result.returncode,
        }
        if result.returncode != 0:
            error_message = stderr or "Skill script execution failed"
            return SkillResult(success=False, output=output, error=error_message)
        return SkillResult(success=True, output=output)

    def _build_command(self, entrypoint: Path) -> list[str]:
        if entrypoint.suffix == ".py":
            return ["python", str(entrypoint)]
        return [str(entrypoint)]
