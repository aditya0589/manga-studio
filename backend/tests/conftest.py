import os
import pytest

# Ensure automated test suite uses deterministic mock engine per Section 16 specification
os.environ["TESTING"] = "1"
