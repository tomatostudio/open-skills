import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeConfig:
    skills_dir: str
    timeout_seconds: int
    reload_interval_seconds: int
    log_level: str

    @classmethod
    def from_env(cls, skills_dir: str | None = None) -> "RuntimeConfig":
        return cls(
            skills_dir=skills_dir or os.getenv("AGENT_SKILLS_DIR", os.path.expanduser("~/.open-skills/assets/skills/user")),
            timeout_seconds=int(os.getenv("AGENT_SKILLS_TIMEOUT_SECONDS", "30")),
            reload_interval_seconds=int(os.getenv("AGENT_SKILLS_RELOAD_INTERVAL_SECONDS", "0")),
            log_level=os.getenv("AGENT_SKILLS_LOG_LEVEL", "INFO"),
        )
