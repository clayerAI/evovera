import numpy as np
import time
from solutions.tsp_v19_optimized_fixed_v6 import ChristofidesHybridStructuralOptimized

def create_bad_tour(n):
    """Create a deliberately bad tour (reverse order)."""
    tour = list(range(n))
    # Add some randomness to make it worse
    for i in range(0, n, 5):
        if i + 1 < n:
            tour[i], tour[i + 1] = tour[i + 1], tour[i]
    tour.append(tour[0])  # Close the tour
    return tour

def optimized_2opt_fast(tour, dist_matrix, time_limit=30.0):
    """Optimized 2-opt with incremental updates and candidate lists."""
    n = len(tour) - 1  # Exclude closing node
    if n <= 3:
        return tour, 0.0
    
    # Remove closing node for processing
    if tour[0] == tour[-1]:
        tour = tour[:-1]
    
    current_length = 0.0
    for i in range(n):
        current_length += dist_matrix[tour[i]][tour[(i + 1) % n]]
    
    best_tour = tour[:]
    best_length = current_length
    
    start_time = time.time()
    
    # Build nearest neighbor lists (once, outside main loop)
    k = min(20, n // 10)
    nn_lists = []
    for i in range(n):
        distances = [(dist_matrix[tour[i]][tour[j]], j) for j in range(n) if j != i]
        distances.sort()
        nn_lists.append([j for _, j in distances[:k]])
    
    improved = True
    iteration = 0
    while improved:
        improved = False
        iteration += 1
        
        for i in range(n):
            if time.time() - start_time > time_limit:
                # Add closing node back
                best_tour.append(best_tour[0])
                return best_tour, best_length
            
            i1 = i
            i2 = (i + 1) % n
            
            # Only check promising j candidates
            for j_idx in nn_lists[i1]:
                j = j_idx
                j1 = j
                j2 = (j + 1) % n
                
                if j1 == i2 or j2 == i1:  # Skip adjacent edges
                    continue
                
                # Calculate delta: remove edges (i1,i2) and (j1,j2), add (i1,j1) and (i2,j2)
                a, b, c, d = tour[i1], tour[i2], tour[j1], tour[j2]
                
                old_cost = dist_matrix[a][b] + dist_matrix[c][d]
                new_cost = dist_matrix[a][c] + dist_matrix[b][d]
                
                delta = new_cost - old_cost
                
                if delta < -1e-9:  # Improvement
                    # Reverse segment between i2 and j1
                    if i2 < j1:
                        segment = tour[i2:j1+1]
                        tour[i2:j1+1] = segment[::-1]
                    else:
                        # Wrap around case
                        segment = tour[i2:] + tour[:j1+1]
                        reversed_segment = segment[::-1]
                        tour[i2:] = reversed_segment[:len(tour)-i2]
                        tour[:j1+1] = reversed_segment[len(tour)-i2:]
                    
                    current_length += delta
                    
                    if current_length < best_length:
                        best_tour = tour[:]
                        best_length = current_length
                    
                    improved = True
                    break  # Restart search
            
            if improved:
                break
    
    # Add closing node back
    best_tour.append(best_tour[0])
    return best_tour, best_length

def test_performance():
    np.random.seed(42)
    n = 200
    points = np.random.rand(n, 2) * 1000
    
    solver = ChristofidesHybridStructuralOptimized(points)
    
    # Create deliberately bad tour
    bad_tour = create_bad_tour(n)
    
    # Compute length of bad tour
    bad_length = 0.0
    for i in range(n):
        bad_length += solver.dist_matrix[bad_tour[i]][bad_tour[(i + 1) % n]]
    
    print(f"Bad tour length: {bad_length:.2f}")
    print(f"Bad tour has {len(bad_tour)} nodes (including closing)")
    
    # Test optimized 2-opt
    start = time.time()
    opt_tour, opt_length = optimized_2opt_fast(bad_tour, solver.dist_matrix, time_limit=5.0)
    opt_time = time.time() - start
    
    print(f"\\nOptimized 2-opt length: {opt_length:.2f}")
    print(f"Optimized 2-opt time: {opt_time:.2f} seconds")
    print(f"Improvement: {((bad_length - opt_length) / bad_length * 100):.2f}%")
    
    # Test with original algorithm's 2-opt (limited time)
    start = time.time()
    orig_tour, orig_length = solver._apply_2opt(bad_tour, time_limit=5.0)
    orig_time = time.time() - start
    
    print(f"\\nOriginal 2-opt length: {orig_length:.2f}")
    print(f"Original 2-opt time: {orig_time:.2f} seconds")
    print(f"Original improvement: {((bad_length - orig_length) / bad_length * 100):.2f}%")

if __name__ == "__main__":
    test_performance()
