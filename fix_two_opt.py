#!/usr/bin/env python3
# Fix the _two_opt method in the optimized v11 algorithm

import re

with open('solutions/tsp_v19_optimized_fixed_v11_optimized.py', 'r') as f:
    content = f.read()

# Find and fix the duplicate line
lines = content.split('\n')
for i in range(len(lines)):
    if 'current = (self.distance_matrix[a][b] +' in lines[i] and 'self                    current =' in lines[i+1]:
        # Remove the duplicate line
        lines[i+1] = '                              self.distance_matrix[c][d])'
        break

fixed_content = '\n'.join(lines)

with open('solutions/tsp_v19_optimized_fixed_v11_optimized.py', 'w') as f:
    f.write(fixed_content)

print("Fixed duplicate line in _two_opt method")
