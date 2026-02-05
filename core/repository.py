import logging
from pathlib import Path
from typing import Dict, Iterable, List

from .models import SkillDefinition
from .parser import SkillParser

logger = logging.getLogger(__name__)


class SkillRepository:
    def __init__(self, skills_dir: Path, parser: SkillParser | None = None) -> None:
        self.skills_dir = skills_dir
        self.parser = parser or SkillParser()

    def discover(self) -> List[SkillDefinition]:
        skills: List[SkillDefinition] = []
        for skill_md in self._find_skill_md_files():
            try:
                skills.append(self.parser.parse(skill_md))
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to parse skill at %s: %s", skill_md, exc)
        return skills

    def _find_skill_md_files(self) -> Iterable[Path]:
        if not self.skills_dir.exists():
            logger.warning("Skills directory does not exist: %s", self.skills_dir)
            return []
        return list(self.skills_dir.rglob("SKILL.md"))

    def as_map(self) -> Dict[str, SkillDefinition]:
        return {skill.name: skill for skill in self.discover()}
