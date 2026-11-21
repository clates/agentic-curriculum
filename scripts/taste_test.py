#!/usr/bin/env python3
"""Run one prompt across several models: outputs, cost, latency, side-by-side HTML.

See src/llm/taste_test.py for options. Loads the key from the environment (OPENROUTER_API_KEY).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from llm.taste_test import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
