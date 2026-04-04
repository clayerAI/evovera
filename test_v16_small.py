#!/usr/bin/env python3
"""
Quick test of v16 with small n to verify it works.
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v16_christofides_path_centrality import solve_tsp as v16_solve
from tsp_v1_nearest_neighbor import solve_tsp as nn2opt_solve
import random
import time

def generate_random_points(n: int = 50, seed: int = 42):
    """Generate random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def main():
    print("Quick v16 test with n=50")
    print("=" * 60)
    
    n = 50
    seed = 42
    
    points = generate_random_points(n=n, seed=seed)
    
    # Test NN+2opt
    print("Running NN+2opt...")
    start = time.time()
    nn2opt_tour, nn2opt_len = nn2opt_solve(points)
    nn2opt_time = time.time() - start
    
    # Test v16
    print("Running v16...")
    start = time.time()
    v16_tour, v16_len = v16_solve(points, seed=seed)
    v16_time = time.time() - start
    
    # Calculate improvement
    improvement = ((nn2opt_len - v16_len) / nn2opt_len) * 100
    
    print(f"\nResults (n={n}, seed={seed}):")
    print(f"NN+2opt: {nn2opt_len:.4f} ({nn2opt_time:.2f}s)")
    print(f"v16:     {v16_len:.4f} ({v16_time:.2f}s)")
    print(f"Improvement: {improvement:.2f}%")
    
    if improvement > 0.1:
        print("✅ v16 beats 0.1% novelty threshold!")
    else:
        print("❌ v16 does not beat 0.1% threshold")
    
    # Test with a few more seeds quickly
    print(f"\n{'='*60}")
    print("Testing with 3 more seeds (n=50)...")
    
    improvements = [improvement]
    
    for seed in [43, 44, 45]:
        points = generate_random_points(n=n, seed=seed)
        
        nn2opt_tour, nn2opt_len = nn2opt_solve(points)
        v16_tour, v16_len = v16_solve(points, seed=seed)
        
        imp = ((nn2opt_len - v16_len) / nn2opt_len) * 100
        improvements.append(imp)
        
        print(f"Seed {seed}: {imp:.2f}% improvement")
    
    avg_improvement = sum(improvements) / len(improvements)
    positive_count = sum(1 for imp in improvements if imp > 0.1)
    
    print(f"\nSummary (n=50, 4 seeds):")
    print(f"Average improvement: {avg_improvement:.2f}%")
    print(f"Seeds beating 0.1% threshold: {positive_count}/4")
    
    if avg_improvement > 0.1:
        print("✅ v16 shows promising results at n=50")
    else:
        print("⚠️  v16 performance needs investigation")

if __name__ == "__main__":
    main()