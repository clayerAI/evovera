"""
TSP Decomposition + Merge approach (Phase 2D-2)
Partitions large instance into k subproblems, solves each with Christofides,
merges using simple bridge + 2-opt refinement.
"""
import numpy as np
import sys
sys.path.insert(0, 'solutions')
from tsp_v19_optimized_fixed_v11 import solve_tsp

def partition_recursive_bisection(points, k=2):
    """Partition points into k clusters using recursive bisection."""
    if k == 1:
        return [list(range(len(points)))]
    
    clusters = [list(range(len(points)))]
    for _ in range(int(np.ceil(np.log2(k)))):
        new_clusters = []
        for cluster in clusters:
            if len(cluster) <= 1:
                new_clusters.append(cluster)
                continue
            pts = np.array([points[i] for i in cluster])
            # PCA-based split
            mean = pts.mean(axis=0)
            cov = np.cov(pts.T)
            try:
                eigvals, eigvecs = np.linalg.eigh(cov)
                axis = eigvecs[:, np.argmax(np.abs(eigvals))]
            except:
                axis = np.array([1, 0])
            proj = pts @ axis
            median = np.median(proj)
            mask = proj >= median
            left = [cluster[i] for i in range(len(cluster)) if not mask[i]]
            right = [cluster[i] for i in range(len(cluster)) if mask[i]]
            if left and right:
                new_clusters.extend([left, right])
            else:
                new_clusters.append(cluster)
        clusters = new_clusters
    return clusters[:k]

def merge_tours_simple(subtours, partition, points, distance_matrix):
    """Merge k subtours using simple bridge connection + 2-opt."""
    if len(subtours) == 1:
        return subtours[0]
    
    # Extract node positions from original partition
    merged = []
    for i, subtour in enumerate(subtours):
        # subtour is in LOCAL indices; convert to global using partition[i]
        global_subtour = [partition[i][local_idx] for local_idx in subtour]
        merged.extend(global_subtour)
    
    # 2-opt refinement with safety checks
    n = len(merged)
    improved = True
    iteration = 0
    max_iterations = min(1000, n * 2)
    
    while improved and iteration < max_iterations:
        improved = False
        iteration += 1
        
        for i in range(n - 2):
            for j in range(i + 2, min(i + 20, n)):  # Bounded window
                if j == n - 1 and i == 0:
                    continue
                
                # Try 2-opt swap
                a, b = merged[i], merged[i + 1]
                c, d = merged[j], merged[(j + 1) % n]
                
                old_dist = distance_matrix[a, b] + distance_matrix[c, d]
                new_dist = distance_matrix[a, c] + distance_matrix[b, d]
                
                if new_dist < old_dist - 1e-6:
                    # Reverse segment [i+1:j+1]
                    merged[i + 1:j + 1] = reversed(merged[i + 1:j + 1])
                    improved = True
                    break
            if improved:
                break
    
    # Verify no duplicates
    if len(set(merged)) != len(merged):
        print(f"ERROR: Duplicates in merge: {len(merged)} vs {len(set(merged))}")
        return None
    
    return merged

def solve_tsp_decomposed(points, distance_matrix, k=1, seed=42):
    """Main entry point: decomposition + merge approach."""
    np.random.seed(seed)
    n = len(points)
    
    if k == 1:
        # No decomposition, just call v11
        tour, length = solve_tsp(points, distance_matrix, seed)
        return tour[:-1], length  # Remove duplicate endpoint
    
    # Partition points
    partition = partition_recursive_bisection(points, k)
    
    # Solve subproblems
    subtours = []
    for cluster in partition:
        if len(cluster) == 0:
            continue
        
        # Extract subproblem
        sub_points = [points[i] for i in cluster]
        sub_dist = distance_matrix[np.ix_(cluster, cluster)]
        
        # Solve with v11
        sub_tour, sub_length = solve_tsp(sub_points, distance_matrix=sub_dist, seed=seed)
        subtours.append(sub_tour[:-1])  # Remove duplicate endpoint
    
    # Merge
    merged = merge_tours_simple(subtours, partition, points, distance_matrix)
    if merged is None:
        return None, None
    
    # Compute final tour length
    final_length = sum(distance_matrix[merged[i], merged[(i + 1) % len(merged)]] 
                       for i in range(len(merged)))
    
    return merged, final_length

# Test on eil51
if __name__ == '__main__':
    with open('data/tsplib/eil51.tsp') as f:
        lines = f.readlines()
    
    data_start = None
    for i, line in enumerate(lines):
        if line.startswith('NODE_COORD_SECTION'):
            data_start = i + 1
            break
    
    coordinates = []
    if data_start:
        for line in lines[data_start:]:
            if line.startswith('EOF'):
                break
            parts = line.strip().split()
            if len(parts) >= 3:
                x, y = float(parts[1]), float(parts[2])
                coordinates.append((x, y))
    
    coordinates = np.array(coordinates)
    n = len(coordinates)
    
    print(f"Testing on eil51")
    print(f"  n={n}")
    
    # Distance matrix
    dist = np.linalg.norm(coordinates[:, None, :] - coordinates[None, :, :], axis=2)
    
    # Dummy points for v11
    dummy_points = [(0, 0)] * n
    
    # Test k=1 and k=2
    for k in [1, 2]:
        tour, length = solve_tsp_decomposed(dummy_points, dist, k=k, seed=42)
        if tour is not None:
            print(f"  k={k}: n={len(tour)}, length={length:.2f}")
        else:
            print(f"  k={k}: FAILED")
