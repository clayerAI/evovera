import sys
sys.path.append('.')
from tsp_v19_optimized_fixed_v11_proper import ChristofidesHybridStructuralOptimizedV11
from tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected
import numpy as np
import random
import time

def generate_random_points(n, seed=42):
    """Generate n random points in [0, 1000]^2."""
    random.seed(seed)
    return [(random.uniform(0, 1000), random.uniform(0, 1000)) for _ in range(n)]

def compute_tour_length(tour, dist_matrix):
    """Compute length of a tour."""
    length = 0
    for i in range(len(tour)):
        u = tour[i]
        v = tour[(i + 1) % len(tour)]
        length += dist_matrix[u][v]
    return length

def test_quality(n_values=[10, 20, 30], seeds=[0, 1, 2], tolerance=0.001):
    """Test quality preservation of v11 vs original v19."""
    print("Testing proper v11 implementation...")
    print(f"Tolerance: {tolerance*100:.1f}%")
    
    all_passed = True
    results = []
    
    for n in n_values:
        print(f"\n=== Testing n={n} ===")
        for seed in seeds:
            points = generate_random_points(n, seed)
            
            # Create distance matrix
            dist_matrix = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    if i != j:
                        xi, yi = points[i]
                        xj, yj = points[j]
                        dist_matrix[i][j] = np.sqrt((xi - xj)**2 + (yi - yj)**2)
            
            # Solve with original v19
            solver_v19 = ChristofidesHybridStructuralCorrected(points=points)
            tour_v19, length_v19, _ = solver_v19.solve()
            
            # Solve with v11
            solver_v11 = ChristofidesHybridStructuralOptimizedV11(points=points)
            tour_v11, length_v11, _ = solver_v11.solve()
            
            # Compute relative difference
            rel_diff = abs(length_v11 - length_v19) / length_v19 if length_v19 > 0 else 0
            
            # Check if within tolerance
            passed = rel_diff <= tolerance
            status = "✓" if passed else "✗"
            
            print(f"  {status} Seed {seed}: {rel_diff*100:.4f}% diff "
                  f"(v19: {length_v19:.2f}, v11: {length_v11:.2f})")
            
            if not passed:
                all_passed = False
            
            results.append({
                'n': n,
                'seed': seed,
                'v19_length': length_v19,
                'v11_length': length_v11,
                'rel_diff': rel_diff,
                'passed': passed
            })
    
    print(f"\n{'✅' if all_passed else '❌'} {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    return all_passed, results

if __name__ == "__main__":
    success, results = test_quality()
    if not success:
        print("\nFailed tests:")
        for r in results:
            if not r['passed']:
                print(f"  n={r['n']}, seed={r['seed']}: {r['rel_diff']*100:.4f}%")
        sys.exit(1)
