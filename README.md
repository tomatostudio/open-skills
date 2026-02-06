# Agent Skills Runtime over MCP

This runtime implements Anthropic Agent Skills as a **live MCP server**, allowing maxKB to discover, inspect, and load skills dynamically. Skills are loaded from disk at runtime, parsed from `SKILL.md`, and either used as instructional context or (optionally) executed via bundled scripts.

## Architecture Overview

- **SkillRepository**: discovers skills from a filesystem root (e.g., `~/.open-skills/assets/skills/user`).
- **SkillParser**: parses `SKILL.md` frontmatter + markdown body into a `SkillDefinition`.
- **SkillRegistry**: caches parsed skills and supports hot reload.
- **SkillRuntime**: runs optional scripts bundled with a skill.
- **MCP Server**: exposes `list_skills`, `describe_skill`, `load_skill_body`, `list_skill_resources`, `run_skill_script`, and `reload_skills` tools.

## Skill Directory Layout

```
~/.open-skills/assets/skills/user/
  sample_skill/
    SKILL.md
    scripts/
      run.py
```

`SKILL.md` frontmatter is the source of truth and supports **only**:

```yaml
---
name: sample-skill
description: Example skill for runtime
license: MIT
---
```

The markdown body contains the procedural guidance that the agent loads on demand.

## Instructional vs Script-backed Skills

Skills are instruction-first. The default mode is to load the skill metadata and body to guide the agent. Scripts are optional accelerators stored under `scripts/`.

If scripts exist, the MCP server exposes `run_skill_script` for explicit execution. Scripts are treated as black-box executables with no schema inference.

## Progressive Disclosure Model

- Metadata (name + description + license) is always loaded.
- The `SKILL.md` body is loaded only after a skill is selected.
- `scripts/` are executed only when explicitly requested.

## CLI Usage

```bash
python run_agent_skills_mcp_server.py \
  --skills-dir ~/.open-skills/assets/skills/user \
  --timeout 30 \
  --reload-interval 10 \
  --transport streamable-http \
  --host 127.0.0.1 \
  --port 8000 \
  --path /mcp
```

By default the server runs with `stdio` transport (no HTTP address). To expose HTTP, use `--transport streamable-http` (or `http`/`sse`) and then connect to:

```
http://<host>:<port><path>
```

## Environment Configuration

- `AGENT_SKILLS_DIR` (default: `~/.open-skills/assets/skills/user`)
- `AGENT_SKILLS_TIMEOUT_SECONDS` (default: `30`)
- `AGENT_SKILLS_RELOAD_INTERVAL_SECONDS` (default: `0`)
- `AGENT_SKILLS_LOG_LEVEL` (default: `INFO`)

## maxKB Integration

Point maxKB's MCP connector at the server URL. It can then:

- Call `list_skills` to discover skills
- Use `describe_skill` to inspect a skill’s metadata
- Call `load_skill_body` to fetch the instructional content
- Call `list_skill_resources` to enumerate bundled resources
- Call `run_skill_script` to execute a specific script when present

## Example Skill

See `examples/agent_skills_runtime/sample_skill` for a working skill directory.
