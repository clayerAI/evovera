# Read the script
with open('evaluate_v11_tsplib_complete_fixed_optimized.py', 'r') as f:
    lines = f.readlines()

# Update the solve_func and result handling
updated_lines = []
for line in lines:
    if 'def solve_func():' in line:
        # Update solve_func to return (tour, length) and compute runtime
        indent = ' ' * 12
        updated_lines.append(f'{indent}def solve_func():\n')
        updated_lines.append(f'{indent}    start_solve = time.time()\n')
        updated_lines.append(f'{indent}    tour, length = solver.solve()\n')
        updated_lines.append(f'{indent}    runtime = time.time() - start_solve\n')
        updated_lines.append(f'{indent}    return tour, length, runtime\n')
    elif 'tour, length, runtime = result' in line:
        # Keep this line as is
        updated_lines.append(line)
    else:
        updated_lines.append(line)

# Write the updated script
with open('evaluate_v11_tsplib_complete_fixed_optimized.py', 'w') as f:
    f.writelines(updated_lines)

print("Fixed solve_func to compute runtime")
