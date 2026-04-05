#!/usr/bin/env python3
"""Fix the Phase 3 script completely."""

import re

with open('execute_phase3_strong_solver_comparison.py', 'r') as f:
    content = f.read()

# Fix 1: Remove the unnecessary parser initialization
content = re.sub(r'# Initialize parser\n    parser = TSPLIBParser\(\)\n', '', content)

# Fix 2: Add numpy array to list conversion for OR-Tools
# Find the OR-Tools solving function
ortools_func_start = content.find('def solve_with_ortools(distance_matrix, time_limit_seconds=120):')
if ortools_func_start != -1:
    # Find the callback function
    callback_start = content.find('def distance_callback(from_index, to_index):', ortools_func_start)
    if callback_start != -1:
        # Replace the callback to handle numpy arrays
        callback_end = content.find('return int(distance_matrix[from_node][to_node])', callback_start)
        if callback_end != -1:
            new_callback = '''    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        # Handle both numpy arrays and Python lists
        val = distance_matrix[from_node][to_node]
        if hasattr(val, 'item'):  # numpy scalar
            return int(val.item())
        return int(val)'''
            content = content[:callback_start] + new_callback + content[callback_end + len('return int(distance_matrix[from_node][to_node])'):]

# Fix 3: Add conversion of distance matrix before passing to OR-Tools
# Find where OR-Tools is called
ortools_call_pattern = r'ortools_route, ortools_cost = solve_with_ortools\(dist_matrix, time_limit_seconds=timeout_ortools\)'
if re.search(ortools_call_pattern, content):
    # Replace with conversion
    new_call = '''            # Convert numpy array to Python list for OR-Tools
            if hasattr(dist_matrix, 'tolist'):
                dist_matrix_list = dist_matrix.tolist()
            else:
                dist_matrix_list = dist_matrix
            
            ortools_route, ortools_cost = solve_with_ortools(dist_matrix_list, time_limit_seconds=timeout_ortools)'''
    content = re.sub(ortools_call_pattern, new_call, content)

# Fix 4: Also convert for v11 algorithm if needed
v11_call_pattern = r'solver = ChristofidesHybridStructuralOptimizedV11\(dist_matrix, seed=seed\)'
if re.search(v11_call_pattern, content):
    new_v11_call = '''            # Convert numpy array to Python list for v11 if needed
            if hasattr(dist_matrix, 'tolist'):
                dist_matrix_list = dist_matrix.tolist()
            else:
                dist_matrix_list = dist_matrix
            
            solver = ChristofidesHybridStructuralOptimizedV11(dist_matrix_list, seed=seed)'''
    content = re.sub(v11_call_pattern, new_v11_call, content)

# Fix 5: Check for the syntax error with "ort            ortools_avg_gap"
content = content.replace('ort            ortools_avg_gap =', 'ortools_avg_gap =')

with open('execute_phase3_strong_solver_comparison.py', 'w') as f:
    f.write(content)

print("Fixed Phase 3 script")
