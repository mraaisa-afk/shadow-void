#!/usr/bin/env python3
"""Command-line entry point for the safe ShadowVoid runner.

The project previously contained a second, divergent implementation here.  A
single entry point avoids fixes landing in one copy while the other continues to
execute obsolete behavior.
"""

from core import main


if __name__ == "__main__":
    raise SystemExit(main())
