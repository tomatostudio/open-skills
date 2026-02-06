import logging
import threading
from typing import Dict, List, Optional

from .models import SkillDefinition
from .repository import SkillRepository

logger = logging.getLogger(__name__)


class SkillRegistry:
    def __init__(self, repository: SkillRepository) -> None:
        self._repository = repository
        self._lock = threading.RLock()
        self._skills: Dict[str, SkillDefinition] = {}
        self.reload()

    def reload(self) -> None:
        with self._lock:
            self._skills = self._repository.as_map()
            logger.info("Loaded %d skills", len(self._skills))

    def list_skills(self) -> List[SkillDefinition]:
        with self._lock:
            return list(self._skills.values())

    def get_skill(self, name: str) -> Optional[SkillDefinition]:
        with self._lock:
            return self._skills.get(name)
