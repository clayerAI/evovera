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

def benchmark(n_values=[50, 100, 200, 300], iterations=3):
    print("=== PERFORMANCE BENCHMARK ===")
    print(f"Iterations per n: {iterations}")
    print()
    
    results = []
    
    for n in n_values:
        print(f"Benchmarking n={n}:")
        v19_times = []
        v11_times = []
        
        for it in range(iterations):
            points = generate_random_points(n, seed=it)
            
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
            
            v19_times.append(v19_time)
            v11_times.append(v11_time)
            
            # Verify quality
            if abs(length_v11 - length_v19) / length_v19 * 100 > 0.1:
                print(f"  ❌ Iteration {it}: Quality degradation detected!")
        
        avg_v19 = sum(v19_times) / len(v19_times)
        avg_v11 = sum(v11_times) / len(v11_times)
        speedup = avg_v19 / avg_v11 if avg_v11 > 0 else 0
        
        results.append((n, avg_v19, avg_v11, speedup))
        
        print(f"  v19 avg: {avg_v19:.3f}s")
        print(f"  v11 avg: {avg_v11:.3f}s")
        print(f"  Speedup: {speedup:.2f}x")
        print()
    
    print("=== RESULTS ===")
    print(f"{'n':>5} {'v19 (s)':>10} {'v11 (s)':>10} {'Speedup':>10}")
    print("-" * 40)
    for n, v19, v11, speedup in results:
        print(f"{n:5} {v19:10.3f} {v11:10.3f} {speedup:10.2f}x")
    
    return results

if __name__ == "__main__":
    benchmark()
