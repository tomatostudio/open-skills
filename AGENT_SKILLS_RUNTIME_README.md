# Agent Skills Runtime over MCP

This runtime implements Anthropic Agent Skills as a **live MCP server**, allowing maxKB to discover, inspect, and invoke skills dynamically. Skills are loaded from disk at runtime, parsed from `SKILL.md`, and executed on demand.

## Architecture Overview

- **SkillRepository**: discovers skills from a filesystem root (e.g., `~/.open-skills/assets/skills/user`).
- **SkillParser**: parses `SKILL.md` frontmatter + markdown body into a `SkillDefinition`.
- **SkillRegistry**: caches parsed skills and supports hot reload.
- **SkillRuntime**: invokes skill entrypoints with structured JSON payloads.
- **MCP Server**: exposes `list_skills`, `get_skill`, `invoke_skill`, and `reload_skills` tools.

## Skill Directory Layout

```
~/.open-skills/assets/skills/user/
  sample_skill/
    SKILL.md
    scripts/
      run.py
```

`SKILL.md` frontmatter is the source of truth and supports:

```yaml
---
name: sample-skill
description: Example skill for runtime
version: 1.0.0
entrypoint: scripts/run.py
input_schema:
  type: object
  properties:
    text:
      type: string
  required: [text]
output_schema:
  type: object
  properties:
    result:
      type: string
---
```

## Invocation Contract

The runtime calls the entrypoint with JSON via STDIN:

```json
{
  "input": {"text": "hello"},
  "context": {},
  "skill": {"name": "sample-skill", "version": "1.0.0"}
}
```

The entrypoint should print JSON to STDOUT:

```json
{"result": "HELLO"}
```

## CLI Usage

```bash
python run_agent_skills_mcp_server.py \
  --skills-dir ~/.open-skills/assets/skills/user \
  --timeout 30 \
  --reload-interval 10
```

## Environment Configuration

- `AGENT_SKILLS_DIR` (default: `~/.open-skills/assets/skills/user`)
- `AGENT_SKILLS_TIMEOUT_SECONDS` (default: `30`)
- `AGENT_SKILLS_RELOAD_INTERVAL_SECONDS` (default: `0`)
- `AGENT_SKILLS_LOG_LEVEL` (default: `INFO`)

## maxKB Integration

Point maxKB's MCP connector at the server URL. It can then:

- Call `list_skills` to discover skills
- Use `get_skill` to inspect a skill’s metadata
- Call `invoke_skill` with structured JSON payloads to execute skills

## Example Skill

See `examples/agent_skills_runtime/sample_skill` for a working skill directory.
