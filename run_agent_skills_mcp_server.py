#!/usr/bin/env python3
import argparse

from agent_skills_runtime import AgentSkillsMCPServer, RuntimeConfig


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Agent Skills MCP server.")
    parser.add_argument("--skills-dir", default=None, help="Directory containing skill folders")
    parser.add_argument("--timeout", type=int, default=None, help="Skill execution timeout in seconds")
    parser.add_argument("--reload-interval", type=int, default=None, help="Auto-reload interval in seconds")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "sse", "streamable-http"],
        default="stdio",
        help="MCP transport (default: stdio)",
    )
    parser.add_argument("--host", default=None, help="HTTP host to bind to (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=None, help="HTTP port to bind to (default: 8000)")
    parser.add_argument("--path", default=None, help="HTTP path to serve MCP (default: /mcp)")
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
    transport_kwargs = {}
    if args.transport in {"http", "sse", "streamable-http"}:
        if args.host:
            transport_kwargs["host"] = args.host
        if args.port:
            transport_kwargs["port"] = args.port
        if args.path:
            transport_kwargs["path"] = args.path
    server.run(transport=args.transport, **transport_kwargs)


if __name__ == "__main__":
    main()
