#!/usr/bin/env python3
"""
Fix the call to _hybrid_structural_matching in v11.
"""
import sys
import os

# Read the fixed file
with open('/workspace/evovera/solutions/tsp_v19_optimized_fixed_v11_fixed.py', 'r') as f:
    content = f.read()

# Find the call to _hybrid_structural_matching
call_start = content.find('matching = self._hybrid_structural_matching(')
if call_start == -1:
    print("ERROR: Could not find call to _hybrid_structural_matching")
    sys.exit(1)

# Find the end of the call (next line with closing parenthesis)
call_end = content.find('\n', call_start)
# Look for the closing parenthesis
paren_count = 1
pos = call_start
while paren_count > 0 and pos < len(content):
    pos += 1
    if content[pos] == '(':
        paren_count += 1
    elif content[pos] == ')':
        paren_count -= 1
call_end = pos + 1

# Extract the call
call_text = content[call_start:call_end]
print(f"Current call:\n{call_text}")

# Replace with correct call
correct_call = '''        matching = self._hybrid_structural_matching(
            odd_vertices, communities, path_centrality,
            within_community_weight, between_community_weight
        )'''

# Replace in content
new_content = content[:call_start] + correct_call + content[call_end:]

# Write the fixed file
with open('/workspace/evovera/solutions/tsp_v19_optimized_fixed_v11_fixed2.py', 'w') as f:
    f.write(new_content)

print(f"\nFixed call in new file: tsp_v19_optimized_fixed_v11_fixed2.py")
