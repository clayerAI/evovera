#!/usr/bin/env python3
# Rewrite the _two_opt method

import re

with open('solutions/tsp_v19_optimized_fixed_v11_optimized.py', 'r') as f:
    content = f.read()

# Find the _two_opt method
two_opt_start = content.find('    def _two_opt(self, tour: List[int]) -> List[int]:')
if two_opt_start == -1:
    print("Could not find _two_opt method")
    exit(1)

# Find the end of the method (next method or end of class)
method_end = content.find('\n    def ', two_opt_start + 1)
if method_end == -1:
    method_end = content.find('\nclass ', two_opt_start + 1)
if method_end == -1:
    method_end = len(content)

two_opt_method = content[two_opt_start:method_end]

# Replace with correct implementation
correct_two_opt = '''    def _two_opt(self, tour: List[int]) -> List[int]:
        """Apply 2-opt local optimization."""
        n = len(tour) - 1  # Exclude closing node
        improved = True
        
        while improved:
            improved = False
            
            for i in range(1, n - 1):
                for j in range(i + 1, n):
                    # Check if swap would improve tour
                    a, b = tour[i-1], tour[i]
                    c, d = tour[j], tour[j+1]
                    
                    current = self.distance_matrix[a][b] + self.distance_matrix[c][d]
                    new = self.distance_matrix[a][c] + self.distance_matrix[b][d]
                    
                    if new < current - 1e-9:
                        # Reverse segment from i to j
                        tour[i:j+1] = reversed(tour[i:j+1])
                        improved = True
                        break
                if improved:
                    break
        
        return tour'''

# Replace the method
new_content = content[:two_opt_start] + correct_two_opt + content[method_end:]

with open('solutions/tsp_v19_optimized_fixed_v11_optimized.py', 'w') as f:
    f.write(new_content)

print("Rewrote _two_opt method")
