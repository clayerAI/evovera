#!/usr/bin/env python3
"""
Quick test for revised v19 hybrid algorithm.
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

def test_v19():
    """Test the revised v19 algorithm."""
    n = 30
    seed = 42
    
    print(f"Testing revised v19 hybrid algorithm with n={n}, seed={seed}")
    print("=" * 60)
    
    # Generate points
    points = generate_random_points(n, seed)
    
    # Test v19 with different parameter combinations
    print("\nTesting different parameter combinations:")
    
    # Test 1: Default parameters
    solver1 = ChristofidesHybridStructural(points, seed=seed)
    tour1, length1, time1 = solver1.solve(
        percentile_threshold=50.0,
        within_community_weight=0.5,
        between_community_weight=0.3,
        apply_2opt=True
    )
    print(f"  Default params: length={length1:.2f}, time={time1:.3f}s")
    
    # Test 2: Strong within-community centrality
    solver2 = ChristofidesHybridStructural(points, seed=seed)
    tour2, length2, time2 = solver2.solve(
        percentile_threshold=50.0,
        within_community_weight=0.8,
        between_community_weight=0.2,
        apply_2opt=True
    )
    print(f"  Strong within: length={length2:.2f}, time={time2:.3f}s")
    
    # Test 3: Weak centrality influence
    solver3 = ChristofidesHybridStructural(points, seed=seed)
    tour3, length3, time3 = solver3.solve(
        percentile_threshold=50.0,
        within_community_weight=0.2,
        between_community_weight=0.1,
        apply_2opt=True
    )
    print(f"  Weak centrality: length={length3:.2f}, time={time3:.3f}s")
    
    # Test 4: Different community detection threshold
    solver4 = ChristofidesHybridStructural(points, seed=seed)
    tour4, length4, time4 = solver4.solve(
        percentile_threshold=70.0,  # More conservative community detection
        within_community_weight=0.5,
        between_community_weight=0.3,
        apply_2opt=True
    )
    print(f"  70th percentile: length={length4:.2f}, time={time4:.3f}s")
    
    # Compare results
    print(f"\nComparison:")
    print(f"  Best result: {min(length1, length2, length3, length4):.2f}")
    print(f"  Worst result: {max(length1, length2, length3, length4):.2f}")
    print(f"  Range: {max(length1, length2, length3, length4) - min(length1, length2, length3, length4):.2f}")
    
    # Check if tours are different
    tours = [tour1, tour2, tour3, tour4]
    unique_tours = set(str(tour) for tour in tours)
    print(f"  Unique tours: {len(unique_tours)} out of 4")
    
    return {
        'default': length1,
        'strong_within': length2,
        'weak_centrality': length3,
        'conservative_communities': length4
    }

if __name__ == "__main__":
    results = test_v19()