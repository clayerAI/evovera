#!/usr/bin/env python3
"""
Profile v19 algorithm to identify computational bottlenecks.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import random
import math
import time
import cProfile
import pstats
from typing import List, Tuple

from solutions.tsp_v19_christofides_hybrid_structural import solve_tsp, ChristofidesHybridStructural

def generate_random_points(n: int, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate n random points in unit square."""
    random.seed(seed)
    points = []
    for _ in range(n):
        x = random.random() * 100
        y = random.random() * 100
        points.append((x, y))
    return points

def profile_v19_small():
    """Profile v19 with small n to understand structure."""
    print("Profiling v19 with n=50...")
    points = generate_random_points(50, seed=123)
    
    # Profile the solve_tsp method
    profiler = cProfile.Profile()
    profiler.enable()
    
    tour, length = solve_tsp(points)
    
    profiler.disable()
    
    print(f"Tour length: {length}")
    print(f"Tour valid: {len(set(tour)) == len(points)}")
    
    # Print profiling stats
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
    
    # Also print by time
    print("\n--- By time ---")
    stats.sort_stats('time')
    stats.print_stats(20)

def profile_v19_medium():
    """Profile v19 with medium n to see scaling."""
    print("\nProfiling v19 with n=100...")
    points = generate_random_points(100, seed=456)
    
    # Profile the solve_tsp method
    profiler = cProfile.Profile()
    profiler.enable()
    
    tour, length = solve_tsp(points)
    
    profiler.disable()
    
    print(f"Tour length: {length}")
    print(f"Tour valid: {len(set(tour)) == len(points)}")
    
    # Print profiling stats
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)

def manual_timing_analysis():
    """Manual timing of different components."""
    print("\n=== Manual Timing Analysis ===")
    
    # Test with n=200 (scaling test)
    points = generate_random_points(200, seed=789)
    
    solver = ChristofidesHybridStructural(points, seed=42)
    
    # Time distance matrix computation
    start = time.time()
    dist_matrix = solver._compute_distance_matrix()
    dist_time = time.time() - start
    print(f"Distance matrix (n=200): {dist_time:.3f}s")
    
    # Time MST computation
    start = time.time()
    mst_adj, parent = solver._compute_mst()
    mst_time = time.time() - start
    print(f"MST computation (n=200): {mst_time:.3f}s")
    
    # Time community detection
    start = time.time()
    communities = solver._detect_communities(mst_adj, percentile_threshold=70.0)
    comm_time = time.time() - start
    print(f"Community detection (n=200): {comm_time:.3f}s")
    
    # Time edge centrality
    start = time.time()
    edge_centrality = solver._compute_edge_centrality(mst_adj)
    edge_cent_time = time.time() - start
    print(f"Edge centrality (n=200): {edge_cent_time:.3f}s")
    
    # Time MST paths (likely bottleneck)
    start = time.time()
    mst_paths = solver._build_mst_paths(mst_adj)
    mst_paths_time = time.time() - start
    print(f"MST paths (n=200): {mst_paths_time:.3f}s")
    
    # Time path centrality
    start = time.time()
    path_centrality = solver._compute_path_centrality(mst_paths, edge_centrality)
    path_cent_time = time.time() - start
    print(f"Path centrality (n=200): {path_cent_time:.3f}s")
    
    # Find odd vertices
    odd_vertices = solver._find_odd_degree_vertices(mst_adj)
    
    # Time matching
    start = time.time()
    matching = solver._hybrid_structural_matching(
        odd_vertices, communities, path_centrality,
        within_community_weight=0.8,
        between_community_weight=0.3
    )
    matching_time = time.time() - start
    print(f"Matching (n=200, {len(odd_vertices)} odd vertices): {matching_time:.3f}s")
    
    total_components = dist_time + mst_time + comm_time + edge_cent_time + mst_paths_time + path_cent_time + matching_time
    print(f"\nTotal component time: {total_components:.3f}s")
    print(f"Expected full solve time: ~{total_components * 1.2:.3f}s (including Eulerian tour)")

if __name__ == "__main__":
    print("=== V19 Algorithm Profiling ===")
    profile_v19_small()
    profile_v19_medium()
    manual_timing_analysis()