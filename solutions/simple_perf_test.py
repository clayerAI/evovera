import sys
sys.path.append('.')
from tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected
from tsp_v19_optimized_fixed_v11_proper import ChristofidesHybridStructuralOptimizedV11
import numpy as np
import random
import time

def generate_random_points(n, seed=42):
    random.seed(seed)
    return [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(n)]

print("Simple performance test (n=100, single iteration)...")
points = generate_random_points(100, seed=42)

# v19
solver_v19 = ChristofidesHybridStructuralCorrected(points=points)
start = time.time()
tour_v19, length_v19, _ = solver_v19.solve()
v19_time = time.time() - start

# v11
solver_v11 = ChristofidesHybridStructuralOptimizedV11(points=points)
start = time.time()
tour_v11, length_v11, _ = solver_v11.solve()
v11_time = time.time() - start

print(f"v19: {v19_time:.3f}s, length: {length_v19:.2f}")
print(f"v11: {v11_time:.3f}s, length: {length_v11:.2f}")
print(f"Speedup: {v19_time/v11_time:.2f}x")
print(f"Quality diff: {abs(length_v11 - length_v19)/length_v19*100:.4f}%")

if abs(length_v11 - length_v19)/length_v19*100 <= 0.1:
    print("✅ Quality preserved within 0.1% tolerance")
else:
    print("❌ Quality degradation detected")
