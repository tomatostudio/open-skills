#!/usr/bin/env python3
import argparse

from agent_skills_runtime import AgentSkillsMCPServer, RuntimeConfig


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Agent Skills MCP server.")
    parser.add_argument("--skills-dir", default=None, help="Directory containing skill folders")
    parser.add_argument("--timeout", type=int, default=None, help="Skill execution timeout in seconds")
    parser.add_argument("--reload-interval", type=int, default=None, help="Auto-reload interval in seconds")
    args = parser.parse_args()

    config = RuntimeConfig.from_env(skills_dir=args.skills_dir)
    if args.timeout is not None:
        config = RuntimeConfig(
            skills_dir=config.skills_dir,
            timeout_seconds=args.timeout,
            reload_interval_seconds=config.reload_interval_seconds,
            log_level=config.log_level,
        )
    if args.reload_interval is not None:
        config = RuntimeConfig(
            skills_dir=config.skills_dir,
            timeout_seconds=config.timeout_seconds,
            reload_interval_seconds=args.reload_interval,
            log_level=config.log_level,
        )

    server = AgentSkillsMCPServer(config)
    server.run()


if __name__ == "__main__":
    main()
