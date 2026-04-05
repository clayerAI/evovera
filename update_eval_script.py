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

# Update the evaluate_instance function to include timeout
eval_func_start = 'def evaluate_instance(instance_name: str, filepath: str, optimal: float, seeds: int = N_SEEDS) -> Dict:'
eval_func_end = '    return results'

# Find and update the evaluation function
lines = content.split('\n')
in_eval_func = False
updated_lines = []
timeout_added = False

for i, line in enumerate(lines):
    if line.strip() == eval_func_start:
        in_eval_func = True
        updated_lines.append(line)
    elif in_eval_func and line.strip() == '    for seed in range(seeds):':
        # Add timeout configuration before the seed loop
        updated_lines.append('    # Timeout configuration (seconds)')
        updated_lines.append('    timeout_config = {')
        updated_lines.append('        "att532": 300,  # Increased timeout for large ATT instance')
        updated_lines.append('        "a280": 180,')
        updated_lines.append('        "d198": 120,')
        updated_lines.append('        "lin318": 180,')
        updated_lines.append('        "pr439": 240')
        updated_lines.append('    }')
        updated_lines.append('    timeout = timeout_config.get(instance_name, 120)')
        updated_lines.append('')
        updated_lines.append(line)
        timeout_added = True
    elif in_eval_func and 'solver = V11Solver(distance_matrix=distance_matrix)' in line:
        # Update the solver call to include timeout
        indent = ' ' * 12  # Match the indentation level
        updated_lines.append(f'{indent}# Run v11 algorithm with timeout')
        updated_lines.append(f'{indent}def solve_func():')
        updated_lines.append(f'{indent}    return solver.solve()')
        updated_lines.append(f'{indent}')
        updated_lines.append(f'{indent}result = run_with_timeout(solve_func, timeout)')
        updated_lines.append(f'{indent}if result is None:')
        updated_lines.append(f'{indent}    print(f"TIMEOUT: Exceeded {timeout}s timeout")')
        updated_lines.append(f'{indent}    continue')
        updated_lines.append(f'{indent}')
        updated_lines.append(f'{indent}tour, length, runtime = result')
        updated_lines.append(f'{indent}elapsed = time.time() - start_time')
        
        # Skip the original solver.solve() line
        continue
    elif in_eval_func and line.strip() == '            # Run v11 algorithm':
        # Skip this comment line since we added our own
        continue
    elif in_eval_func and line.strip() == '            tour, length, runtime = solver.solve()':
        # Skip this line since we already handled it
        continue
    elif in_eval_func and line.strip() == eval_func_end:
        in_eval_func = False
        updated_lines.append(line)
    else:
        updated_lines.append(line)

# Join back
updated_content = '\n'.join(updated_lines)

# Write the updated script
with open('evaluate_v11_tsplib_complete_fixed_optimized.py', 'w') as f:
    f.write(updated_content)

print("Updated evaluation script with timeout handling")
