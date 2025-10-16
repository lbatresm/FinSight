#conftest.py
import os
import pytest
import sys
from pathlib import Path

# Add project root directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))