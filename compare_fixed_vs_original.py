import sys
sys.path.append('.')
import random
import time

# Import both algorithms
from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected
from solutions.tsp_v19_optimized_fixed_v6 import ChristofidesHybridStructuralOptimized

# Create test instance
random.seed(42)
n = 50
points = [(random.random() * 100, random.random() * 100) for _ in range(n)]

print(f"Testing with n={n} points")
print("=" * 50)

# Test original algorithm
start = time.time()
solver_orig = ChristofidesHybridStructuralCorrected(points, seed=42)
tour_orig, length_orig, runtime_orig = solver_orig.solve(apply_2opt=False)
time_orig = time.time() - start

print("Original algorithm (no 2-opt):")
print(f"  Tour length: {length_orig:.2f}")
print(f"  Runtime: {runtime_orig:.3f}s (measured: {time_orig:.3f}s)")

# Test fixed optimized algorithm  
start = time.time()
solver_opt = ChristofidesHybridStructuralOptimized(points, seed=42)
tour_opt, length_opt, runtime_opt = solver_opt.solve(apply_2opt=False)
time_opt = time.time() - start

print("\nFixed optimized algorithm (no 2-opt):")
print(f"  Tour length: {length_opt:.2f}")
print(f"  Runtime: {runtime_opt:.3f}s (measured: {time_opt:.3f}s)")
print(f"  Speedup: {runtime_orig/runtime_opt:.1f}x")
print(f"  Length difference: {(length_opt - length_orig)/length_orig*100:.2f}%")

# Test with 2-opt
print("\n" + "=" * 50)
print("Testing WITH 2-OPT:")

start = time.time()
solver_orig = ChristofidesHybridStructuralCorrected(points, seed=42)
tour_orig2, length_orig2, runtime_orig2 = solver_orig.solve(apply_2opt=True)
time_orig2 = time.time() - start

print("Original algorithm (with 2-opt):")
print(f"  Tour length: {length_orig2:.2f}")
print(f"  Runtime: {runtime_orig2:.3f}s (measured: {time_orig2:.3f}s)")

start = time.time()
solver_opt = ChristofidesHybridStructuralOptimized(points, seed=42)
tour_opt2, length_opt2, runtime_opt2 = solver_opt.solve(apply_2opt=True)
time_opt2 = time.time() - start

print("\nFixed optimized algorithm (with 2-opt):")
print(f"  Tour length: {length_opt2:.2f}")
print(f"  Runtime: {runtime_opt2:.3f}s (measured: {time_opt2:.3f}s)")
print(f"  Speedup: {runtime_orig2/runtime_opt2:.1f}x")
print(f"  Length difference: {(length_opt2 - length_orig2)/length_orig2*100:.2f}%")

# Check if tours are identical
print("\n" + "=" * 50)
print("Tour comparison (without 2-opt):")
if tour_orig == tour_opt:
    print("  Tours are IDENTICAL!")
else:
    print("  Tours are DIFFERENT")
    # Check if they're the same length at least
    if abs(length_orig - length_opt) < 0.01:
        print("  But same length (within tolerance)")
    else:
        print(f"  Different lengths: {length_orig:.2f} vs {length_opt:.2f}")

print("\nTour comparison (with 2-opt):")
if tour_orig2 == tour_opt2:
    print("  Tours are IDENTICAL!")
else:
    print("  Tours are DIFFERENT")
    if abs(length_orig2 - length_opt2) < 0.01:
        print("  But same length (within tolerance)")
    else:
        print(f"  Different lengths: {length_orig2:.2f} vs {length_opt2:.2f}")
