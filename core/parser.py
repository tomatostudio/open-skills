import logging
from pathlib import Path
from typing import Any, Dict, Tuple

from .models import SkillDefinition

logger = logging.getLogger(__name__)


class SkillParser:
    def __init__(self, strict_frontmatter: bool = False) -> None:
        self.strict_frontmatter = strict_frontmatter

    def parse(self, skill_md_path: Path) -> SkillDefinition:
        content = skill_md_path.read_text(encoding="utf-8")
        metadata, body = self._parse_frontmatter(content)

        metadata = self._normalize_metadata(metadata, skill_md_path)
        name = metadata["name"]
        description = metadata["description"]
        license_value = metadata.get("license")

        references = self._collect_resources(skill_md_path.parent / "references")
        scripts = self._collect_resources(skill_md_path.parent / "scripts")
        assets = self._collect_resources(skill_md_path.parent / "assets")

        return SkillDefinition(
            name=name,
            description=description,
            path=skill_md_path.parent,
            body_markdown=body.strip(),
            references=references,
            scripts=scripts,
            assets=assets,
            license=license_value,
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
        started = False

        for line in lines:
            if line.strip() == "---":
                if not started:
                    started = True
                    in_frontmatter = True
                    continue
                if in_frontmatter:
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

    def _normalize_metadata(self, metadata: Dict[str, Any], skill_md_path: Path) -> Dict[str, Any]:
        allowed_fields = {"name", "description", "license"}
        extra_fields = set(metadata.keys()) - allowed_fields
        if extra_fields:
            message = f"Unsupported SKILL.md frontmatter fields: {', '.join(sorted(extra_fields))}"
            if self.strict_frontmatter:
                raise ValueError(message)
            logger.warning("%s; ignoring extra fields.", message)
            for field in extra_fields:
                metadata.pop(field, None)

        name = metadata.get("name")
        description = metadata.get("description")
        if not name or not description:
            raise ValueError(f"SKILL.md missing required frontmatter fields at {skill_md_path}")
        return metadata

    def _collect_resources(self, directory: Path) -> list[str]:
        if not directory.exists():
            return []
        resources: list[str] = []
        for path in directory.rglob("*"):
            if path.is_file():
                resources.append(path.relative_to(directory.parent).as_posix())
        return sorted(resources)
