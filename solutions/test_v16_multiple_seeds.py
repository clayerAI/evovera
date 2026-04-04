#!/usr/bin/env python3
"""
Test v16 with multiple random seeds to check consistency
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import time
from solutions.tsp_v1_nearest_neighbor import solve_tsp as nn2opt_solve
from solutions.tsp_v16_christofides_path_centrality import solve_tsp as v16_solve

def generate_random_points(n, seed):
    """Generate random Euclidean points"""
    np.random.seed(seed)
    return np.random.rand(n, 2) * 1000

def test_seed(n, seed):
    """Test a single seed"""
    points = generate_random_points(n, seed)
    
    # NN+2opt
    nn_tour, nn_length = nn2opt_solve(points)
    
    # v16
    v16_tour, v16_length = v16_solve(points, seed=seed)
    
    improvement = ((nn_length - v16_length) / nn_length) * 100
    return nn_length, v16_length, improvement

def main():
    print("=== v16 Consistency Test with Multiple Seeds ===")
    print("Testing n=100 with 5 different random seeds")
    
    n = 100
    seeds = [42, 123, 456, 789, 999]
    
    results = []
    for seed in seeds:
        print(f"\nSeed {seed}:")
        nn_len, v16_len, imp = test_seed(n, seed)
        print(f"  NN+2opt: {nn_len:.4f}")
        print(f"  v16:     {v16_len:.4f}")
        print(f"  Improvement: {imp:.2f}%")
        results.append((nn_len, v16_len, imp))
    
    # Calculate statistics
    improvements = [r[2] for r in results]
    avg_improvement = np.mean(improvements)
    std_improvement = np.std(improvements)
    
    print(f"\n=== Summary ===")
    print(f"Average improvement: {avg_improvement:.2f}%")
    print(f"Std deviation: {std_improvement:.2f}%")
    print(f"Min improvement: {min(improvements):.2f}%")
    print(f"Max improvement: {max(improvements):.2f}%")
    
    # Check if all seeds exceed threshold
    all_above_threshold = all(imp > 0.1 for imp in improvements)
    if all_above_threshold:
        print(f"✅ ALL seeds exceed 0.1% publication threshold")
    else:
        print(f"❌ Some seeds below 0.1% threshold")
    
    # Statistical significance check
    if avg_improvement - std_improvement > 0.1:
        print(f"✅ Statistically significant improvement (mean - std > 0.1%)")
    else:
        print(f"⚠️  Improvement may not be statistically significant")
    
    return all_above_threshold

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)