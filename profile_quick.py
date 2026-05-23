import sys, os, time, numpy as np
sys.path.insert(0, os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "solutions"))
try:
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
        import time as timer
        t0 = timer.time()
        sol, qual = algo.solve_tsp(dist, timeout=600, seed=42)
        print(f"n={n} time={timer.time()-t0:.2f}s qual={qual*100:.1f}%")
except Exception as e:
    print(f"Error: {e}")
