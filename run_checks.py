"""
Run the main code quality checks and test suite.

The script runs Ruff, Mypy, and Pytest in sequence and reports any
checks that fail.
"""

import subprocess
import sys
from typing import List, Tuple


def run_step(description: str, command: List[str]) -> bool:
    """Run one check and return whether it completed successfully."""
    print(f"\n{description}")
    print(f"Command: {' '.join(command)}")

    result = subprocess.run(command)

    if result.returncode != 0:
        print(f"FAILED: {description}")
        return False

    print(f"PASSED: {description}")
    return True


def main() -> None:
    """Run all code quality checks and tests."""
    steps: List[Tuple[str, List[str]]] = [
        (
            "Ruff formatting check",
            ["uv", "run", "ruff", "format", "--check", "."],
        ),
        (
            "Ruff linting check",
            ["uv", "run", "ruff", "check", "."],
        ),
        (
            "Mypy type checking",
            ["uv", "run", "mypy", "winery_adventures", "tests"],
        ),
        (
            "Pytest test suite and coverage",
            ["uv", "run", "pytest"],
        ),
    ]

    failed_steps: List[str] = []

    for description, command in steps:
        if not run_step(description, command):
            failed_steps.append(description)

    print("\nQuality checks summary")

    if not failed_steps:
        print("All checks passed.")
        sys.exit(0)

    print(f"{len(failed_steps)} check(s) failed:")
    for step in failed_steps:
        print(f"- {step}")

    sys.exit(1)


if __name__ == "__main__":
    main()
