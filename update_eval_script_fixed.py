import re

# Read the original script
with open('evaluate_v11_tsplib_complete_fixed_optimized.py', 'r') as f:
    content = f.read()

# Add timeout imports at the top
import_section = '''#!/usr/bin/env python3
"""
Complete TSPLIB Phase 2 evaluation for v11 algorithm with ALL required instances.
Based on Vera's notification: att532, a280, d198, lin318, pr439.
Uses OPTIMIZED v11 algorithm with O(n²) edge centrality.
"""

import sys
import os
import time
import numpy as np
from pathlib import Path
import statistics
import signal
from typing import Dict, List, Tuple

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tsplib_parser import TSPLIBParser
from solutions.tsp_v19_optimized_fixed_v11_optimized import ChristofidesHybridStructuralOptimizedV11 as V11Solver

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Algorithm timed out")

def run_with_timeout(func, timeout_seconds):
    """Run a function with timeout."""
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
    try:
        result = func()
        signal.alarm(0)
        return result
    except TimeoutException:
        return None
    finally:
        signal.alarm(0)
'''

# Replace the import section
content = re.sub(r'^#!/usr/bin/env python3.*?from solutions\.tsp_v19_optimized_fixed_v11_optimized import ChristofidesHybridStructuralOptimizedV11 as V11Solver', 
                 import_section, content, flags=re.DOTALL)

# Write the updated content
with open('evaluate_v11_tsplib_complete_fixed_optimized.py', 'w') as f:
    f.write(content)

print("Updated imports in evaluation script")
