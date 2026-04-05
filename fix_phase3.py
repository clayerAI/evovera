#!/usr/bin/env python3
"""Fix the Phase 3 script."""

import re

with open('execute_phase3_strong_solver_comparison.py', 'r') as f:
    content = f.read()

# Fix the parsing section
old_section = '''        # Parse instance
        try:
            parser = TSPLIBParser(instance_file)
        if not parser.parse():
            print(f'  ERROR: Failed to parse {instance_file}')
            continue
        points = parser.get_coordinates()
        dist_matrix = parser.get_distance_matrix()
            n_nodes = len(points)'''

new_section = '''        # Parse instance
        try:
            parser = TSPLIBParser(instance_file)
            if not parser.parse():
                print(f'  ERROR: Failed to parse {instance_file}')
                continue
            points = parser.get_coordinates()
            dist_matrix = parser.get_distance_matrix()
            n_nodes = len(points)'''

content = content.replace(old_section, new_section)

# Also need to add the except block
if 'except Exception as e:' not in content:
    # Find where the try block ends
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'n_nodes = len(points)' in line:
            # Insert except block after this line
            indent = len(line) - len(line.lstrip())
            indent_str = ' ' * indent
            lines.insert(i + 1, f'{indent_str}except Exception as e:')
            lines.insert(i + 2, f'{indent_str}    print(f"  ERROR: Exception parsing {{instance_file}}: {{e}}")')
            lines.insert(i + 3, f'{indent_str}    continue')
            break
    content = '\n'.join(lines)

with open('execute_phase3_strong_solver_comparison.py', 'w') as f:
    f.write(content)

print("Fixed Phase 3 script")
