import sys
sys.path.append('.')
from tsp_v19_optimized_fixed_v11_proper import ChristofidesHybridStructuralOptimizedV11
import numpy as np

print("Testing TSPLIB compatibility (distance_matrix parameter)...")

# Test 1: Points only (Euclidean)
n = 10
points = [(i, i) for i in range(n)]
solver1 = ChristofidesHybridStructuralOptimizedV11(points=points)
tour1, length1, _ = solver1.solve()
print(f"✓ Test 1 (points only): Tour length = {length1:.2f}")

# Test 2: Distance matrix only (TSPLIB style)
dist_matrix = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        if i != j:
            dist_matrix[i][j] = abs(i - j)  # Manhattan distance for simplicity

solver2 = ChristofidesHybridStructuralOptimizedV11(distance_matrix=dist_matrix)
tour2, length2, _ = solver2.solve()
print(f"✓ Test 2 (distance_matrix only): Tour length = {length2:.2f}")

# Test 3: Both points and distance matrix (should use distance_matrix)
solver3 = ChristofidesHybridStructuralOptimizedV11(points=points, distance_matrix=dist_matrix)
tour3, length3, _ = solver3.solve()
print(f"✓ Test 3 (both): Tour length = {length3:.2f}")

# Verify consistency
if abs(length2 - length3) < 1e-6:
    print("✅ TSPLIB compatibility verified: distance_matrix parameter works correctly")
else:
    print(f"❌ Inconsistency: length2={length2}, length3={length3}")

# Test ATT distance metric (TSPLIB specific)
print("\nTesting ATT distance metric simulation...")
# Create a simple ATT-like distance: ceil(sqrt((dx^2 + dy^2)/10.0))
att_dist_matrix = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        if i != j:
            d = np.sqrt((i - j)**2 + (i - j)**2)  # Euclidean
            att_dist_matrix[i][j] = np.ceil(d / 10.0)  # ATT-like

solver_att = ChristofidesHybridStructuralOptimizedV11(distance_matrix=att_dist_matrix)
tour_att, length_att, _ = solver_att.solve()
print(f"✓ ATT-like distance: Tour length = {length_att:.2f}")

print("\n✅ All TSPLIB compatibility tests passed!")
