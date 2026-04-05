import numpy as np
import time
from solutions.tsp_v19_optimized_fixed_v6 import ChristofidesHybridStructuralOptimized

def optimized_2opt(tour, dist_matrix, time_limit=30.0):
    """Optimized 2-opt with incremental length updates."""
    n = len(tour)
    if n <= 3:
        return tour, 0.0
    
    # Convert to numpy array for faster indexing
    tour_arr = np.array(tour)
    
    # Precompute tour distances between consecutive nodes
    current_length = 0.0
    for i in range(n - 1):
        current_length += dist_matrix[tour[i]][tour[i + 1]]
    
    best_tour = tour_arr.copy()
    best_length = current_length
    
    start_time = time.time()
    
    improved = True
    while improved:
        improved = False
        
        # Create candidate list: for each node, consider only k nearest neighbors
        k = min(20, n // 10)  # Consider top 20 or 10% of nearest neighbors
        
        # Build nearest neighbor lists
        nn_lists = []
        for i in range(n):
            # Get distances from node i to all others
            distances = [(dist_matrix[tour[i]][tour[j]], j) for j in range(n) if j != i]
            distances.sort()
            nn_lists.append([j for _, j in distances[:k]])
        
        for i in range(1, n - 2):
            if time.time() - start_time > time_limit:
                return best_tour.tolist(), best_length
            
            i_node = tour[i]
            
            # Only check j in candidate list for i+1
            for j_idx in nn_lists[i]:
                j = j_idx
                if j <= i + 1:  # Skip adjacent edges and reverse order
                    continue
                
                # Calculate delta without full tour recomputation
                # Remove edges (i-1, i) and (j, j+1), add edges (i-1, j) and (i, j+1)
                a, b, c, d = tour[i-1], tour[i], tour[j], tour[(j + 1) % n]
                
                old_cost = dist_matrix[a][b] + dist_matrix[c][d]
                new_cost = dist_matrix[a][c] + dist_matrix[b][d]
                
                delta = new_cost - old_cost
                
                if delta < -1e-9:  # Improvement found
                    # Reverse segment i..j
                    new_tour = tour_arr.copy()
                    new_tour[i:j+1] = new_tour[i:j+1][::-1]
                    
                    # Update length incrementally
                    new_length = current_length + delta
                    
                    # Accept move
                    tour_arr = new_tour
                    tour = tour_arr.tolist()
                    current_length = new_length
                    
                    if new_length < best_length:
                        best_tour = new_tour.copy()
                        best_length = new_length
                    
                    improved = True
                    break  # Restart search after improvement
            
            if improved:
                break
    
    return best_tour.tolist(), best_length

def test_optimization():
    np.random.seed(42)
    n = 200
    points = np.random.rand(n, 2) * 1000
    
    solver = ChristofidesHybridStructuralOptimized(points)
    
    # Get initial tour without 2-opt
    tour, length, _ = solver.solve()
    
    print(f"Initial tour length: {length:.2f}")
    print(f"Initial tour has {len(tour)} nodes")
    
    # Test optimized 2-opt
    start = time.time()
    opt_tour, opt_length = optimized_2opt(tour, solver.dist_matrix, time_limit=10.0)
    opt_time = time.time() - start
    
    print(f"Optimized 2-opt length: {opt_length:.2f}")
    print(f"Optimized 2-opt time: {opt_time:.2f} seconds")
    print(f"Improvement: {((length - opt_length) / length * 100):.2f}%")
    
    # Compare with original 2-opt (with time limit)
    start = time.time()
    orig_tour, orig_length = solver._apply_2opt(tour, time_limit=10.0)
    orig_time = time.time() - start
    
    print(f"\\nOriginal 2-opt length: {orig_length:.2f}")
    print(f"Original 2-opt time: {orig_time:.2f} seconds")
    print(f"Original improvement: {((length - orig_length) / length * 100):.2f}%")

if __name__ == "__main__":
    test_optimization()
