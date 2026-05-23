#!/usr/bin/env python3
import sys, os, time, numpy as np, json, cProfile, pstats
from io import StringIO

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "solutions"))

try:
    from tsp_v19_optimized_fixed_v11_optimized import ChristofidesHybridStructuralOptimizedV11
except Exception as e:
    print(f"ERROR: {e}"); sys.exit(1)

def gen_instance(n, seed=42):
    np.random.seed(seed)
    points = np.random.rand(n, 2) * 1000
    distances = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            d = np.sqrt(np.sum((points[i] - points[j])**2))
            distances[i][j] = d
            distances[j][i] = d
    return points, distances

def profile_one(n_nodes, trial=1, seed=42):
    print(f"Profiling n={n_nodes} trial={trial}")
    t0 = time.time()
    points, distances = gen_instance(n_nodes, seed=seed+trial)
    gen_time = time.time() - t0
    
    algo = ChristofidesHybridStructuralOptimizedV11()
    prof = cProfile.Profile()
    t0 = time.time()
    prof.enable()
    
    try:
        solution, quality = algo.solve_tsp(distances, timeout=600, seed=seed+trial)
    except Exception as e:
        prof.disable()
        print(f"ERROR: {e}")
        return None
    
    prof.disable()
    total_time = time.time() - t0
    print(f"  Time: {total_time:.3f}s, quality: {quality*100:.2f}%")
    
    s = StringIO()
    ps = pstats.Stats(prof, stream=s).sort_stats("cumulative")
    ps.print_stats(10)
    print(s.getvalue())
    
    return {"n": n_nodes, "time": total_time, "quality": quality}

results = [profile_one(n, trial=1) for n in [250, 350, 500]]
with open("v11_profile_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print("Done")
