import json
import logging
from pathlib import Path
from typing import Any, Dict, Tuple

from .models import SkillDefinition

logger = logging.getLogger(__name__)


class SkillParser:
    def parse(self, skill_md_path: Path) -> SkillDefinition:
        content = skill_md_path.read_text(encoding="utf-8")
        metadata, body = self._parse_frontmatter(content)

        name = metadata.get("name", skill_md_path.parent.name)
        description = metadata.get("description", "")
        version = metadata.get("version", "1.0.0")
        entrypoint = metadata.get("entrypoint")
        input_schema = self._read_schema(metadata.get("input_schema"))
        output_schema = self._read_schema(metadata.get("output_schema"))

        metadata["body"] = body.strip()

        return SkillDefinition(
            name=name,
            description=description,
            version=version,
            path=skill_md_path.parent,
            entrypoint=entrypoint,
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            metadata=metadata,
        )

    def _parse_frontmatter(self, content: str) -> Tuple[Dict[str, Any], str]:
        lines = content.splitlines()
        if not lines or lines[0].strip() != "---":
            return {}, content

        frontmatter_lines = []
        body_lines = []
        in_frontmatter = False
        closed = False

        for line in lines:
            if line.strip() == "---":
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                closed = True
                in_frontmatter = False
                continue
            if in_frontmatter:
                frontmatter_lines.append(line)
            else:
                body_lines.append(line)

        frontmatter = "\n".join(frontmatter_lines)
        metadata = self._load_yaml(frontmatter) if closed else self._parse_simple_kv(frontmatter_lines)
        return metadata, "\n".join(body_lines)

    def _parse_simple_kv(self, lines: list[str]) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {}
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()
        return metadata

    def _load_yaml(self, content: str) -> Dict[str, Any]:
        try:
            import yaml  # type: ignore
        except ModuleNotFoundError:
            logger.warning("PyYAML not installed; falling back to simple frontmatter parsing.")
            return self._parse_simple_kv(content.splitlines())
        return yaml.safe_load(content) or {}

    def _read_schema(self, value: Any) -> Dict[str, Any]:
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return {}
        return {}
