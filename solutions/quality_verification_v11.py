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

def compute_tour_length(tour, points):
    total = 0
    for i in range(len(tour)):
        x1, y1 = points[tour[i]]
        x2, y2 = points[tour[(i + 1) % len(tour)]]
        total += np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return total

def test_quality(n_values=[10, 20, 30, 50, 100], seeds=5):
    print("=== QUALITY VERIFICATION TEST ===")
    print(f"Tolerance: 0.1%")
    print(f"Seeds per n: {seeds}")
    print()
    
    all_pass = True
    max_diff = 0.0
    worst_case = None
    
    for n in n_values:
        print(f"Testing n={n}:")
        diffs = []
        
        for seed in range(seeds):
            points = generate_random_points(n, seed)
            
            # Original v19
            solver_v19 = ChristofidesHybridStructuralCorrected(points=points)
            tour_v19, length_v19, _ = solver_v19.solve()
            
            # v11
            solver_v11 = ChristofidesHybridStructuralOptimizedV11(points=points)
            tour_v11, length_v11, _ = solver_v11.solve()
            
            # Compute difference
            if length_v19 > 0:
                diff_pct = abs(length_v11 - length_v19) / length_v19 * 100
            else:
                diff_pct = 0.0
                
            diffs.append(diff_pct)
            
            if diff_pct > max_diff:
                max_diff = diff_pct
                worst_case = (n, seed, length_v19, length_v11, diff_pct)
            
            status = "✓" if diff_pct <= 0.1 else "✗"
            print(f"  {status} Seed {seed}: {diff_pct:.4f}% diff (v19: {length_v19:.2f}, v11: {length_v11:.2f})")
        
        avg_diff = sum(diffs) / len(diffs)
        max_n_diff = max(diffs)
        print(f"  Avg diff: {avg_diff:.4f}%, Max diff: {max_n_diff:.4f}%")
        
        if max_n_diff > 0.1:
            all_pass = False
            print(f"  ❌ FAILED: Exceeds 0.1% tolerance")
        else:
            print(f"  ✅ PASSED: Within tolerance")
        print()
    
    print("=== SUMMARY ===")
    if all_pass:
        print(f"✅ ALL TESTS PASSED")
    else:
        print(f"❌ SOME TESTS FAILED")
    
    print(f"Maximum difference observed: {max_diff:.4f}%")
    if worst_case:
        n, seed, v19_len, v11_len, diff = worst_case
        print(f"Worst case: n={n}, seed={seed}, v19={v19_len:.2f}, v11={v11_len:.2f}, diff={diff:.4f}%")
    
    return all_pass, max_diff

if __name__ == "__main__":
    success, max_diff = test_quality()
    sys.exit(0 if success else 1)
