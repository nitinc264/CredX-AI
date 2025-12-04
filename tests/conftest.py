import sys
import pathlib

# Ensure the repository root (one level above tests/) is on sys.path so imports like
# import matching_engine work reliably across terminals and CI.
ROOT = pathlib.Path(__file__).resolve().parents[1]
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)
