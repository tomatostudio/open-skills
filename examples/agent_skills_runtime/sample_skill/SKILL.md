---
name: sample-skill
description: Example skill for runtime execution
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

# Sample Skill

This skill uppercases the provided `text` input.
