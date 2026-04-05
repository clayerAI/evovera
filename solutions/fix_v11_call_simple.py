#!/usr/bin/env python3
"""
Fix the call to _hybrid_structural_matching in v11.
"""
import sys
import os

# Read the fixed file
with open('/workspace/evovera/solutions/tsp_v19_optimized_fixed_v11_fixed.py', 'r') as f:
    lines = f.readlines()

# Find the line with the call
for i, line in enumerate(lines):
    if '_hybrid_structural_matching(' in line:
        print(f"Found call at line {i+1}: {line.strip()}")
        # Find the full call (might span multiple lines)
        call_lines = []
        j = i
        paren_count = 0
        while j < len(lines):
            call_lines.append(lines[j])
            paren_count += lines[j].count('(') - lines[j].count(')')
            if paren_count <= 0 and ')' in lines[j]:
                break
            j += 1
        
        call_text = ''.join(call_lines)
        print(f"Full call:\n{call_text}")
        
        # Replace these lines
        replacement = '''        matching = self._hybrid_structural_matching(
            odd_vertices, communities, path_centrality,
            within_community_weight, between_community_weight
        )'''
        
        # Remove old lines and insert replacement
        del lines[i:j+1]
        lines.insert(i, replacement + '\n')
        break

# Write the fixed file
with open('/workspace/evovera/solutions/tsp_v19_optimized_fixed_v11_fixed2.py', 'w') as f:
    f.writelines(lines)

print(f"\nFixed call in new file: tsp_v19_optimized_fixed_v11_fixed2.py")
