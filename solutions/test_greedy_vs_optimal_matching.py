#!/usr/bin/env python3
"""
Test to compare greedy minimum matching vs optimal matching for Christofides.
This helps determine if the greedy approach is fundamentally suboptimal.
"""

import sys
sys.path.append('.')
from solutions.tsp_v2_christofides import EuclideanTSPChristofides
import numpy as np
import itertools
import time

def optimal_minimum_matching(points, odd_vertices):
    """Exhaustive search for optimal perfect matching (only for small n)."""
    n_odd = len(odd_vertices)
    if n_odd % 2 != 0:
        raise ValueError("Number of odd vertices must be even")
    
    # Create distance matrix for odd vertices
    dist_matrix = np.zeros((n_odd, n_odd))
    for i in range(n_odd):
        for j in range(i+1, n_odd):
            dist = np.linalg.norm(points[odd_vertices[i]] - points[odd_vertices[j]])
            dist_matrix[i][j] = dist
            dist_matrix[j][i] = dist
    
    # Generate all perfect matchings
    vertices = list(range(n_odd))
    best_matching = None
    best_cost = float('inf')
    
    # For small n (<= 8), we can brute force
    if n_odd <= 8:
        # Generate all perfect matchings
        for perm in itertools.permutations(vertices):
            # Check if this is a valid perfect matching (pairs)
            cost = 0
            matching = []
            used = [False] * n_odd
            
            for i in range(0, n_odd, 2):
                u = perm[i]
                v = perm[i+1]
                if used[u] or used[v]:
                    break
                cost += dist_matrix[u][v]
                matching.append((odd_vertices[u], odd_vertices[v]))
                used[u] = used[v] = True
            
            if all(used) and cost < best_cost:
                best_cost = cost
                best_matching = matching
        
        return best_matching, best_cost
    else:
        # For larger n, use greedy as baseline
        return None, None

def test_matching_quality(n=20, seed=42):
    """Test greedy vs optimal matching on small instances."""
    print(f"Testing matching quality (n={n}, seed={seed})")
    print("=" * 60)
    
    tsp = EuclideanTSPChristofides(n=n, seed=seed)
    
    # Get MST and odd vertices
    mst_edges = tsp.prim_mst()
    odd_vertices = tsp.find_odd_degree_vertices(mst_edges)
    
    print(f"Number of odd vertices: {len(odd_vertices)}")
    
    # Get greedy matching
    start = time.time()
    greedy_matching = tsp.greedy_minimum_matching(odd_vertices)
    greedy_time = time.time() - start
    
    # Calculate greedy matching cost
    greedy_cost = 0
    for edge in greedy_matching:
        if len(edge) == 3:
            u, v, weight = edge
            greedy_cost += weight
        else:
            u, v = edge
            greedy_cost += tsp.distance(u, v)
    
    print(f"Greedy matching: {len(greedy_matching)} edges, cost={greedy_cost:.4f}, time={greedy_time:.6f}s")
    
    # Get optimal matching (if possible)
    if len(odd_vertices) <= 8:
        start = time.time()
        optimal_matching, optimal_cost = optimal_minimum_matching(tsp.points, odd_vertices)
        optimal_time = time.time() - start
        
        if optimal_matching:
            print(f"Optimal matching: {len(optimal_matching)} edges, cost={optimal_cost:.4f}, time={optimal_time:.6f}s")
            
            # Calculate optimality gap
            gap = (greedy_cost - optimal_cost) / optimal_cost * 100
            print(f"Greedy vs optimal gap: {gap:.2f}%")
            
            # Check if greedy found optimal
            if abs(greedy_cost - optimal_cost) < 1e-6:
                print("✓ Greedy found optimal matching!")
            else:
                print("✗ Greedy is suboptimal")
                
            return gap
        else:
            print("Could not compute optimal matching (too many odd vertices)")
    else:
        print(f"Too many odd vertices ({len(odd_vertices)}) for exhaustive search")
    
    return None

def run_multiple_tests():
    """Run multiple tests to get statistics."""
    print("\n" + "="*60)
    print("COMPREHENSIVE MATCHING QUALITY TEST")
    print("="*60)
    
    gaps = []
    for seed in range(10):
        print(f"\nTest {seed+1}/10:")
        gap = test_matching_quality(n=20, seed=seed)
        if gap is not None:
            gaps.append(gap)
    
    if gaps:
        print("\n" + "="*60)
        print("STATISTICS:")
        print(f"Average optimality gap: {np.mean(gaps):.2f}%")
        print(f"Maximum gap: {np.max(gaps):.2f}%")
        print(f"Minimum gap: {np.min(gaps):.2f}%")
        print(f"Std deviation: {np.std(gaps):.2f}%")
        
        # Count how often greedy is optimal
        optimal_count = sum(1 for g in gaps if abs(g) < 1e-6)
        print(f"Greedy found optimal matching in {optimal_count}/{len(gaps)} cases ({optimal_count/len(gaps)*100:.1f}%)")

if __name__ == "__main__":
    run_multiple_tests()