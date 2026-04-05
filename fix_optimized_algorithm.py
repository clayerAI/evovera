import re

with open('solutions/tsp_v19_optimized_fixed_v6.py', 'r') as f:
    content = f.read()

# Find the matching method and fix the formula
# We need to change:
# if u_comm == v_comm:
#     distance *= within_community_weight
# else:
#     distance *= between_community_weight
# 
# path_cent = self._compute_path_centrality_lazy(u, v, edge_centrality)
# distance *= (1.0 - 0.5 * path_cent)
#
# To:
# path_cent = self._compute_path_centrality_lazy(u, v, edge_centrality)
# if u_comm == v_comm:
#     distance *= (1.0 - within_community_weight * path_cent)
# else:
#     distance *= (1.0 - between_community_weight * path_cent)

# Find the method
lines = content.split('\n')
in_method = False
method_start = -1
method_end = -1

for i, line in enumerate(lines):
    if line.strip().startswith('def _hybrid_structural_matching_optimized'):
        in_method = True
        method_start = i
    elif in_method and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
        # Found end of method (non-indented line)
        method_end = i
        break

if method_end == -1:
    method_end = len(lines)

print(f"Method found at lines {method_start} to {method_end}")

# Extract method lines
method_lines = lines[method_start:method_end]

# Find the problematic section
for i, line in enumerate(method_lines):
    if 'distance *= within_community_weight' in line:
        print(f"Found weight multiplication at line {i}: {line.strip()}")
    if 'distance *= (1.0 - 0.5 * path_cent)' in line:
        print(f"Found centrality multiplication at line {i}: {line.strip()}")

# Let's do a simpler fix: replace the whole section
fixed_content = content

# Replace the problematic lines
pattern = r'(\s+)if u_comm == v_comm:\s*\n\s+distance \*= within_community_weight\s*\n\s+else:\s*\n\s+distance \*= between_community_weight\s*\n\s+path_cent = self\._compute_path_centrality_lazy\(u, v, edge_centrality\)\s*\n\s+distance \*= \(1\.0 - 0\.5 \* path_cent\)'

replacement = r'\1path_cent = self._compute_path_centrality_lazy(u, v, edge_centrality)\n\1if u_comm == v_comm:\n\1    distance *= (1.0 - within_community_weight * path_cent)\n\1else:\n\1    distance *= (1.0 - between_community_weight * path_cent)'

fixed_content = re.sub(pattern, replacement, fixed_content, flags=re.MULTILINE)

# Write back
with open('solutions/tsp_v19_optimized_fixed_v6.py', 'w') as f:
    f.write(fixed_content)

print("Fixed the matching algorithm formula!")
