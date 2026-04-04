#!/usr/bin/env python3
"""
Investigate why Standard Christofides appears to underperform.
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v2_christofides import solve_tsp as christofides_solve
from tsp_v1_nearest_neighbor import solve_tsp as nn_2opt_solve
import numpy as np
import random

def generate_random_points(n: int = 50, seed: int = 42) -> list:
    """Generate random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def test_christofides_directly(points):
    """Test Christofides directly to understand performance."""
    print(f"Testing with {len(points)} points")
    
    # Convert to numpy array
    points_array = np.array(points)
    
    # Run Christofides
    try:
        tour, length = christofides_solve(points_array)
        print(f"Christofides tour length: {length:.4f}")
        
        # Run baseline
        baseline_tour, baseline_length = nn_2opt_solve(points)
        print(f"Baseline (NN+2opt) length: {baseline_length:.4f}")
        
        improvement = (baseline_length - length) / baseline_length * 100
        print(f"Christofides vs Baseline: {improvement:.2f}%")
        
        return length, baseline_length, improvement
    except Exception as e:
        print(f"Error running Christofides: {e}")
        return None, None, None

def test_multiple_seeds():
    """Test with different random seeds."""
    n = 50
    results = []
    
    for seed in [42, 43, 44, 45, 46]:
        print(f"\n=== Seed {seed} ===")
        points = generate_random_points(n=n, seed=seed)
        
        christofides_len, baseline_len, improvement = test_christofides_directly(points)
        
        if christofides_len is not None:
            results.append({
                'seed': seed,
                'christofides': christofides_len,
                'baseline': baseline_len,
                'improvement': improvement
            })
    
    if results:
        print("\n=== SUMMARY ===")
        avg_christofides = sum(r['christofides'] for r in results) / len(results)
        avg_baseline = sum(r['baseline'] for r in results) / len(results)
        avg_improvement = sum(r['improvement'] for r in results) / len(results)
        
        print(f"Average Christofides: {avg_christofides:.4f}")
        print(f"Average Baseline: {avg_baseline:.4f}")
        print(f"Average Improvement: {avg_improvement:.2f}%")
        
        # Check if Christofides is consistently worse
        if avg_improvement < 0:
            print(f"\n⚠️  Christofides is UNDERPERFORMING baseline by {-avg_improvement:.2f}%")
            print("Possible issues:")
            print("1. Christofides implementation bug")
            print("2. 2-opt not working properly in Christofides")
            print("3. Matching algorithm issue")
            print("4. Eulerian tour/shortcutting issue")
        else:
            print(f"\n✅ Christofides is IMPROVING over baseline by {avg_improvement:.2f}%")

def test_small_case():
    """Test with a very small, verifiable case."""
    print("\n=== Testing small verifiable case ===")
    
    # Simple square
    points = [(0, 0), (1, 0), (1, 1), (0, 1)]
    points_array = np.array(points)
    
    print(f"Points: {points}")
    
    # Optimal tour length for square: perimeter = 4.0
    # Nearest neighbor + 2opt should find optimal or near-optimal
    
    # Run Christofides
    tour, length = christofides_solve(points_array)
    print(f"Christofides tour: {tour}")
    print(f"Christofides length: {length:.4f}")
    print(f"Optimal length: 4.0")
    print(f"Difference: {length - 4.0:.4f}")
    
    # Run baseline
    baseline_tour, baseline_length = nn_2opt_solve(points)
    print(f"\nBaseline tour: {baseline_tour}")
    print(f"Baseline length: {baseline_length:.4f}")
    
    if length > baseline_length + 0.1:  # Allow small floating point differences
        print(f"\n❌ Christofides is worse than baseline for simple square!")
        print(f"Christofides: {length:.4f}, Baseline: {baseline_length:.4f}")
    else:
        print(f"\n✅ Christofides performs reasonably for simple square")

def main():
    print("Investigating Christofides performance issue")
    
    # Test with standard size
    points = generate_random_points(n=50, seed=42)
    test_christofides_directly(points)
    
    # Test multiple seeds
    test_multiple_seeds()
    
    # Test small verifiable case
    test_small_case()

if __name__ == "__main__":
    main()