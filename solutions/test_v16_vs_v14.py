#!/usr/bin/env python3
"""
Test v16 (Path-Based Centrality) vs v14 (Edge Centrality) vs Standard Christofides.
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v16_christofides_path_centrality import solve_tsp as v16_solve
from tsp_v14_christofides_adaptive_matching import solve_tsp as v14_solve
from tsp_v2_christofides import solve_tsp as christofides_solve
from tsp_v1_nearest_neighbor import solve_tsp as nn_2opt_solve

import random
import numpy as np
from typing import List, Tuple

def generate_random_points(n: int = 50, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def compare_algorithms(points: List[Tuple[float, float]], n_trials: int = 3):
    """Compare performance of different algorithms."""
    results = []
    
    # Convert points to numpy for Christofides
    points_array = np.array(points)
    
    for trial in range(n_trials):
        print(f"\n=== Trial {trial+1}/{n_trials} ===")
        
        # Baseline
        baseline_tour, baseline_length = nn_2opt_solve(points)
        
        # Standard Christofides
        christofides_tour, christofides_length = christofides_solve(points_array)
        christofides_improvement = (baseline_length - christofides_length) / baseline_length * 100
        
        # v14 (Edge Centrality)
        v14_tour, v14_length = v14_solve(points, seed=42+trial)
        v14_improvement = (baseline_length - v14_length) / baseline_length * 100
        
        # v16 (Path-Based Centrality)
        v16_tour, v16_length = v16_solve(points, seed=42+trial)
        v16_improvement = (baseline_length - v16_length) / baseline_length * 100
        
        print(f"Baseline (NN+2opt): {baseline_length:.4f}")
        print(f"Standard Christofides: {christofides_length:.4f} ({christofides_improvement:.2f}% vs baseline)")
        print(f"v14 Edge Centrality: {v14_length:.4f} ({v14_improvement:.2f}% vs baseline)")
        print(f"v16 Path Centrality: {v16_length:.4f} ({v16_improvement:.2f}% vs baseline)")
        
        # Compare v16 vs v14
        v16_vs_v14 = (v14_length - v16_length) / v14_length * 100 if v14_length > 0 else 0
        print(f"v16 vs v14: {v16_vs_v14:.2f}% improvement")
        
        # Compare v16 vs Standard Christofides
        v16_vs_christofides = (christofides_length - v16_length) / christofides_length * 100 if christofides_length > 0 else 0
        print(f"v16 vs Standard Christofides: {v16_vs_christofides:.2f}% improvement")
        
        results.append({
            'trial': trial,
            'baseline': baseline_length,
            'christofides': christofides_length,
            'v14': v14_length,
            'v16': v16_length,
            'christofides_improvement': christofides_improvement,
            'v14_improvement': v14_improvement,
            'v16_improvement': v16_improvement,
            'v16_vs_v14': v16_vs_v14,
            'v16_vs_christofides': v16_vs_christofides
        })
    
    # Calculate averages
    print("\n=== AVERAGE RESULTS ===")
    avg_baseline = sum(r['baseline'] for r in results) / len(results)
    avg_christofides = sum(r['christofides'] for r in results) / len(results)
    avg_v14 = sum(r['v14'] for r in results) / len(results)
    avg_v16 = sum(r['v16'] for r in results) / len(results)
    
    avg_christofides_imp = sum(r['christofides_improvement'] for r in results) / len(results)
    avg_v14_imp = sum(r['v14_improvement'] for r in results) / len(results)
    avg_v16_imp = sum(r['v16_improvement'] for r in results) / len(results)
    
    avg_v16_vs_v14 = sum(r['v16_vs_v14'] for r in results) / len(results)
    avg_v16_vs_christofides = sum(r['v16_vs_christofides'] for r in results) / len(results)
    
    print(f"Average Baseline: {avg_baseline:.4f}")
    print(f"Average Standard Christofides: {avg_christofides:.4f} ({avg_christofides_imp:.2f}% vs baseline)")
    print(f"Average v14 Edge Centrality: {avg_v14:.4f} ({avg_v14_imp:.2f}% vs baseline)")
    print(f"Average v16 Path Centrality: {avg_v16:.4f} ({avg_v16_imp:.2f}% vs baseline)")
    print(f"\nAverage v16 vs v14: {avg_v16_vs_v14:.2f}% improvement")
    print(f"Average v16 vs Standard Christofides: {avg_v16_vs_christofides:.2f}% improvement")
    
    # Determine if v16 beats the 0.1% threshold
    threshold = 0.1
    beats_threshold = avg_v16_vs_christofides > threshold
    
    print(f"\n=== NOVELTY ASSESSMENT ===")
    if beats_threshold:
        print(f"✅ v16 BEATS 0.1% threshold: {avg_v16_vs_christofides:.2f}% > {threshold}%")
        print("Potential for novelty verification!")
    else:
        print(f"❌ v16 DOES NOT beat 0.1% threshold: {avg_v16_vs_christofides:.2f}% <= {threshold}%")
        print("Need further improvements.")
    
    return results, beats_threshold

def test_different_sizes():
    """Test algorithms with different problem sizes."""
    sizes = [20, 30, 50, 100]
    
    for size in sizes:
        print(f"\n{'='*60}")
        print(f"Testing with n={size}")
        print('='*60)
        
        points = generate_random_points(n=size, seed=42)
        
        # Run comparison
        results, beats_threshold = compare_algorithms(points, n_trials=2)
        
        if beats_threshold:
            print(f"✅ v16 shows promise for n={size}")
        else:
            print(f"⚠️  v16 needs improvement for n={size}")

def main():
    print("Testing v16 (Path-Based Centrality) vs v14 (Edge Centrality) vs Standard Christofides")
    
    # Test with moderate size
    points = generate_random_points(n=50, seed=42)
    results, beats_threshold = compare_algorithms(points, n_trials=3)
    
    # Test different sizes
    test_different_sizes()

if __name__ == "__main__":
    main()