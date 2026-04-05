#!/usr/bin/env python3
"""
Simple test to identify v19 bottlenecks.
"""

import sys
import os
import random
import time
from typing import List, Tuple

# Add current directory to path
sys.path.insert(0, os.getcwd())

from solutions.tsp_v19_christofides_hybrid_structural_corrected import solve_tsp, ChristofidesHybridStructuralCorrected

def generate_random_points(n: int, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate n random points in unit square."""
    random.seed(seed)
    points = []
    for _ in range(n):
        x = random.random() * 100
        y = random.random() * 100
        points.append((x, y))
    return points

def test_scaling():
    """Test v19 scaling with different sizes."""
    print("Testing v19 algorithm scaling...")
    
    sizes = [50, 100, 150, 200]
    
    for n in sizes:
        print(f"\n--- Testing n={n} ---")
        points = generate_random_points(n, seed=n)
        
        start = time.time()
        try:
            tour, length = solve_tsp(points, timeout=60)  # 1 minute timeout
            elapsed = time.time() - start
            print(f"  Success: {elapsed:.2f}s, length={length:.2f}")
            print(f"  Valid tour: {len(set(tour)) == len(points)}")
        except Exception as e:
            elapsed = time.time() - start
            print(f"  Failed after {elapsed:.2f}s: {e}")
            
            # Try with solver object to get more details
            try:
                solver = ChristofidesHybridStructuralCorrected(points, seed=42)
                # Test individual components
                print("  Testing individual components...")
                
                start_comp = time.time()
                dist_matrix = solver._compute_distance_matrix()
                print(f"    Distance matrix: {time.time() - start_comp:.2f}s")
                
                start_comp = time.time()
                mst_adj, parent = solver._compute_mst()
                print(f"    MST computation: {time.time() - start_comp:.2f}s")
                
                start_comp = time.time()
                communities = solver._detect_communities(mst_adj, percentile_threshold=70.0)
                print(f"    Community detection: {time.time() - start_comp:.2f}s")
                
                start_comp = time.time()
                edge_centrality = solver._compute_edge_centrality(mst_adj)
                print(f"    Edge centrality: {time.time() - start_comp:.2f}s")
                
                # This is likely the bottleneck
                start_comp = time.time()
                mst_paths = solver._build_mst_paths(mst_adj)
                print(f"    MST paths: {time.time() - start_comp:.2f}s")
                
            except Exception as e2:
                print(f"    Component test failed: {e2}")

if __name__ == "__main__":
    test_scaling()
