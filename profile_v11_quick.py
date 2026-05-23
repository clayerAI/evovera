#!/usr/bin/env python3
import sys, os, time, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "solutions"))
from tsp_v19_optimized_fixed_v11_optimized import ChristofidesHybridStructuralOptimizedV11
algo = ChristofidesHybridStructuralOptimizedV11()
for n in [250, 350, 500]:
    np.random.seed(42)
    pts = np.random.rand(n, 2)*1000
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            d = ((pts[i]-pts[j])**2).sum()**0.5
            dist[i][j] = d
            dist[j][i] = d
    t0 = time.time()
    sol, qual = algo.solve_tsp(dist, timeout=600, seed=42)
    print(f"n={n}: {time.time()-t0:.2f}s quality={qual*100:.1f}%")
