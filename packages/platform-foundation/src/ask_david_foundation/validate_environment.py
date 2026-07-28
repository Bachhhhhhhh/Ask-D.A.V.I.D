"""Command-line validation for the platform's non-secret configuration."""

import argparse
from collections.abc import Sequence
from pathlib import Path

from pydantic import ValidationError

from ask_david_foundation.settings import PlatformSettings


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    """Parse an optional local configuration file without printing its contents."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Validate environment variables and print a sanitized result."""
    arguments = parse_args(argv)
    try:
        settings = PlatformSettings(_env_file=arguments.env_file)
    except ValidationError as error:
        print(f"Configuration validation failed:\n{error}")
        return 1

    print(f"Configuration is valid: {settings.safe_summary()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
