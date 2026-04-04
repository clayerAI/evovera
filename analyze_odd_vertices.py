#!/usr/bin/env python3
"""
Analyze number of odd vertices in MST for different n.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import random
import math
from typing import List, Tuple

from solutions.tsp_v19_christofides_hybrid_structural import ChristofidesHybridStructural

def generate_random_points(n: int, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate n random points in unit square."""
    random.seed(seed)
    points = []
    for _ in range(n):
        x = random.random() * 100
        y = random.random() * 100
        points.append((x, y))
    return points

def analyze_odd_vertices():
    """Analyze odd vertex counts for different n."""
    print("=== Odd Vertex Analysis ===")
    
    for n in [50, 100, 200, 300, 400, 500]:
        total_odd = 0
        samples = 10
        
        for seed in range(samples):
            points = generate_random_points(n, seed=seed)
            solver = ChristofidesHybridStructural(points, seed=seed)
            
            # Compute MST
            mst_adj, parent = solver._compute_mst()
            
            # Find odd vertices
            odd_count = 0
            for i in range(n):
                if len(mst_adj[i]) % 2 == 1:
                    odd_count += 1
            
            total_odd += odd_count
        
        avg_odd = total_odd / samples
        odd_ratio = avg_odd / n
        print(f"n={n}: avg odd vertices = {avg_odd:.1f} ({odd_ratio*100:.1f}% of n)")
        print(f"  Pairs to consider: C({int(avg_odd)}, 2) = {int(avg_odd*(avg_odd-1)/2):,}")
        
        # Compare to all pairs
        all_pairs = n * (n - 1) // 2
        print(f"  Reduction factor: {all_pairs / (avg_odd*(avg_odd-1)/2):.1f}x fewer pairs")

if __name__ == "__main__":
    analyze_odd_vertices()