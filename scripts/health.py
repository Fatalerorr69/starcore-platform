#!/usr/bin/env python3
"""
STARCORE Health — runtime API health check.

Pings the /health endpoint of a running STARCORE API instance and reports
the database and overall status. Exits 0 when status is "ok", 1 otherwise.

Usage:
    uv run python scripts/health.py
    uv run python scripts/health.py --url http://myserver:8000
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request


def main() -> int:
    parser = argparse.ArgumentParser(description="STARCORE runtime API health check")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the STARCORE API (default: http://localhost:8000)",
    )
    args = parser.parse_args()

    url = f"{args.url.rstrip('/')}/health"
    print(f"Checking {url} ...")

    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            body: dict = json.loads(resp.read())
        status = body.get("status", "unknown")
        print(f"Status:   {status}")
        print(f"Database: {body.get('database', 'unknown')}")
        return 0 if status == "ok" else 1
    except urllib.error.URLError as exc:
        print(f"UNREACHABLE: {exc.reason}")
        return 1
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
