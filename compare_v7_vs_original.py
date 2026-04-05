import numpy as np
import time
from solutions.tsp_v19_christofides_hybrid_structural import ChristofidesHybridStructural
from create_optimized_v7 import ChristofidesHybridStructuralOptimizedV7

def test_comparison():
    np.random.seed(42)
    
    sizes = [50, 100, 150]
    results = []
    
    for n in sizes:
        points = np.random.rand(n, 2) * 1000
        
        # Test original v19
        solver_original = ChristofidesHybridStructural(points)
        start = time.time()
        tour_orig, length_orig, _ = solver_original.solve()
        time_orig = time.time() - start
        
        # Test optimized v7
        solver_v7 = ChristofidesHybridStructuralOptimizedV7(points)
        start = time.time()
        tour_v7, length_v7, _ = solver_v7.solve()
        time_v7 = time.time() - start
        
        # Calculate percentage difference
        diff_pct = abs(length_orig - length_v7) / length_orig * 100
        
        results.append({
            'n': n,
            'original_length': length_orig,
            'v7_length': length_v7,
            'diff_pct': diff_pct,
            'original_time': time_orig,
            'v7_time': time_v7,
            'speedup': time_orig / time_v7 if time_v7 > 0 else float('inf')
        })
        
        print(f"n={n}:")
        print(f"  Original: {length_orig:.2f} ({time_orig:.2f}s)")
        print(f"  V7:       {length_v7:.2f} ({time_v7:.2f}s)")
        print(f"  Diff:     {diff_pct:.2f}%")
        print(f"  Speedup:  {time_orig/time_v7:.1f}x")
        print()
    
    # Summary
    print("SUMMARY:")
    avg_diff = sum(r['diff_pct'] for r in results) / len(results)
    avg_speedup = sum(r['speedup'] for r in results) / len(results)
    print(f"Average difference: {avg_diff:.2f}%")
    print(f"Average speedup: {avg_speedup:.1f}x")
    
    return results

if __name__ == "__main__":
    test_comparison()
