# Read the script
with open('evaluate_v11_tsplib_complete_fixed_optimized.py', 'r') as f:
    lines = f.readlines()

# Find the evaluate_instance function
in_eval_func = False
updated_lines = []
timeout_added = False

for i, line in enumerate(lines):
    if 'def evaluate_instance(' in line:
        in_eval_func = True
        updated_lines.append(line)
    elif in_eval_func and 'for seed in range(seeds):' in line:
        # Add timeout configuration before the seed loop
        indent = ' ' * 4
        updated_lines.append(f'{indent}# Timeout configuration (seconds)\n')
        updated_lines.append(f'{indent}timeout_config = {{\n')
        updated_lines.append(f'{indent}    "att532": 300,  # Increased timeout for large ATT instance\n')
        updated_lines.append(f'{indent}    "a280": 180,\n')
        updated_lines.append(f'{indent}    "d198": 120,\n')
        updated_lines.append(f'{indent}    "lin318": 180,\n')
        updated_lines.append(f'{indent}    "pr439": 240\n')
        updated_lines.append(f'{indent}}}\n')
        updated_lines.append(f'{indent}timeout = timeout_config.get(instance_name, 120)\n')
        updated_lines.append(f'{indent}\n')
        updated_lines.append(line)
        timeout_added = True
    elif in_eval_func and 'solver = V11Solver(distance_matrix=distance_matrix)' in line:
        # Keep the solver creation
        updated_lines.append(line)
    elif in_eval_func and '# Run v11 algorithm' in line and lines[i+1].strip() == 'tour, length, runtime = solver.solve()':
        # Replace the solver call with timeout handling
        indent = ' ' * 12
        updated_lines.append(f'{indent}# Run v11 algorithm with timeout\n')
        updated_lines.append(f'{indent}def solve_func():\n')
        updated_lines.append(f'{indent}    return solver.solve()\n')
        updated_lines.append(f'{indent}\n')
        updated_lines.append(f'{indent}result = run_with_timeout(solve_func, timeout)\n')
        updated_lines.append(f'{indent}if result is None:\n')
        updated_lines.append(f'{indent}    print(f"TIMEOUT: Exceeded {{timeout}}s timeout")\n')
        updated_lines.append(f'{indent}    continue\n')
        updated_lines.append(f'{indent}\n')
        updated_lines.append(f'{indent}tour, length, runtime = result\n')
        updated_lines.append(f'{indent}elapsed = time.time() - start_time\n')
        
        # Skip the next line (tour, length, runtime = solver.solve())
        continue
    elif in_eval_func and 'tour, length, runtime = solver.solve()' in line:
        # Skip this line since we already handled it
        continue
    elif in_eval_func and 'elapsed = time.time() - start_time' in line:
        # Skip this line since we already added it
        continue
    else:
        updated_lines.append(line)

# Write the updated script
with open('evaluate_v11_tsplib_complete_fixed_optimized.py', 'w') as f:
    f.writelines(updated_lines)

print("Updated evaluation script with timeout handling")
