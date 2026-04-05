import sys
sys.path.append('.')

# Test the fixed matching algorithm
import random
from solutions.tsp_v19_optimized_fixed_v6 import ChristofidesHybridStructuralOptimized

# Create a simple test
random.seed(42)
n = 20
points = [(random.random() * 100, random.random() * 100) for _ in range(n)]

solver = ChristofidesHybridStructuralOptimized(points, seed=42)

# Run the algorithm
tour, length, runtime = solver.solve(apply_2opt=False)
print(f"Fixed algorithm (no 2-opt):")
print(f"  Tour length: {length:.2f}")
print(f"  Runtime: {runtime:.3f}s")

# Also test with 2-opt
tour2, length2, runtime2 = solver.solve(apply_2opt=True)
print(f"\nFixed algorithm (with 2-opt):")
print(f"  Tour length: {length2:.2f}")
print(f"  Runtime: {runtime2:.3f}s")
print(f"  2-opt improvement: {(length - length2)/length*100:.1f}%")

# Compare with original
print("\nNow comparing with original algorithm...")
