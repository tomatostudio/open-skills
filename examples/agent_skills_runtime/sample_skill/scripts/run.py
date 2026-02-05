import json
import sys


def main() -> None:
    payload = json.loads(sys.stdin.read() or "{}")
    text = payload.get("input", {}).get("text", "")
    result = {"result": text.upper()}
    print(json.dumps(result))


if __name__ == "__main__":
    main()
