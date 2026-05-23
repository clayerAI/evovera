#!/usr/bin/env python3
import sys
import os
import time
import numpy as np
import json
import cProfile
import pstats
from io import StringIO

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "solutions"))

try:
    from tsp_v19_optimized_fixed_v11_optimized import ChristofidesHybridStructuralOptimizedV11
    print("OK: Loaded v11 algorithm")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

def generate_random_instance(n, seed=42):
    np.random.seed(seed)
    points = np.random.rand(n, 2) * 1000
    distances = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            d = np.sqrt(np.sum((points[i] - points[j])**2))
            distances[i][j] = d
            distances[j][i] = d
    return points, distances

def profile_v11_instance(n_nodes, trial=1, seed=42):
    print(f"Profiling n={n_nodes} trial={trial}")
    start_gen = time.time()
    points, distances = generate_random_instance(n_nodes, seed=seed+trial)
    gen_time = time.time() - start_gen
    
    algorithm = ChristofidesHybridStructuralOptimizedV11()
    profiler = cProfile.Profile()
    
    start_solve = time.time()
    profiler.enable()
    
    try:
        solution, quality = algorithm.solve_tsp(distances, timeout=600, seed=seed+trial)
    except Exception as e:
        print(f"ERROR: {e}")
        profiler.disable()
        return None
    
    profiler.disable()
    total_time = time.time() - start_solve
    
    print(f"  Result: {total_time:.3f}s, quality={quality*100:.2f}%")
    
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(10)
    print(s.getvalue())
    
    return {
        'n_nodes': n_nodes,
        'trial': trial,
        'total_time': total_time,
        'quality': quality,
        'generation_time': gen_time
    }

if __name__ == '__main__':
    print("Starting v11 bottleneck analysis")
    results = []
    for n in [250, 350, 500]:
        result = profile_v11_instance(n, trial=1, seed=42)
        if result:
            results.append(result)
    
    with open('v11_profiling_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print("Saved results to v11_profiling_results.json")
