import re

with open('solutions/tsp_v19_optimized_fixed_v6.py', 'r') as f:
    content = f.read()

# We need to change the matching logic to match the original:
# Original: for i in range(k): if not visited[i]: find best j where j > i and not visited[j]
# Optimized: for i in range(k): if not matched[i]: find best j where j != i and not matched[j]

# Actually, looking at the code again, the optimized version already does:
# for j in range(k):
#     if i == j or matched[j]:
#         continue
# So it looks at all j, not just j > i.

# But actually, this should be equivalent because when we get to vertex j (where j < i),
# if it's not matched yet, we would match it then. So the order matters!

# Let me change it to match the original exactly: only consider j > i
pattern = r'(\s+)for j in range\(k\):\s*\n\s+if i == j or matched\[j\]:\s*\n\s+continue'

replacement = r'\1for j in range(i + 1, k):\n\1    if matched[j]:\n\1        continue'

fixed_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

# Write back
with open('solutions/tsp_v19_optimized_fixed_v6.py', 'w') as f:
    f.write(fixed_content)

print("Fixed matching logic to only consider j > i (like original)")
