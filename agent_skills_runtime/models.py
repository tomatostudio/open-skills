from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class SkillDefinition:
    name: str
    description: str
    version: str
    path: Path
    entrypoint: Optional[str] = None
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillInvocation:
    skill_name: str
    payload: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillResult:
    success: bool
    output: Dict[str, Any]
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
