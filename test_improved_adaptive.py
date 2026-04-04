#!/usr/bin/env python3
"""
Test improved adaptive weight selection for v16.
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v16_christofides_path_centrality import solve_tsp as v16_solve
from tsp_v1_nearest_neighbor import solve_tsp as nn2opt_solve
import random
import time
from typing import List, Tuple
import json

def generate_random_points(n: int = 50, seed: int = 42):
    """Generate random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def test_adaptive_rule():
    """Test the improved adaptive weight selection rule."""
    print("Testing Improved Adaptive Weight Selection Rule")
    print("=" * 60)
    
    test_cases = [
        {'n': 30, 'seed': 42, 'name': 'very_small'},
        {'n': 50, 'seed': 42, 'name': 'small'},
        {'n': 75, 'seed': 42, 'name': 'medium_small'},
        {'n': 100, 'seed': 42, 'name': 'medium'},
        {'n': 150, 'seed': 42, 'name': 'medium_large'},
        {'n': 200, 'seed': 42, 'name': 'large'},
    ]
    
    results = []
    
    for test_case in test_cases:
        n = test_case['n']
        seed = test_case['seed']
        name = test_case['name']
        
        print(f"\nTesting {name} (n={n}):")
        
        points = generate_random_points(n=n, seed=seed)
        
        # Get baseline
        baseline_tour, baseline_length = nn2opt_solve(points)
        
        # Test with adaptive weight (None = use adaptive rule)
        adaptive_tour, adaptive_length = v16_solve(points, seed=seed, centrality_weight=None)
        adaptive_improvement = ((baseline_length - adaptive_length) / baseline_length) * 100
        
        # Test with fixed weight=0.3 for comparison
        fixed_tour, fixed_length = v16_solve(points, seed=seed, centrality_weight=0.3)
        fixed_improvement = ((baseline_length - fixed_length) / baseline_length) * 100
        
        # Determine adaptive weight that would be used
        if n <= 50:
            adaptive_weight_used = 0.3
        elif n <= 100:
            adaptive_weight_used = 0.7
        else:
            adaptive_weight_used = 1.0
        
        print(f"  Baseline: {baseline_length:.4f}")
        print(f"  Fixed weight (0.3): {fixed_length:.4f} ({fixed_improvement:.2f}%)")
        print(f"  Adaptive weight ({adaptive_weight_used}): {adaptive_length:.4f} ({adaptive_improvement:.2f}%)")
        
        if adaptive_improvement > fixed_improvement:
            print(f"  ✅ Adaptive rule improves by {adaptive_improvement - fixed_improvement:.2f}%")
        elif adaptive_improvement < fixed_improvement:
            print(f"  ❌ Adaptive rule worse by {fixed_improvement - adaptive_improvement:.2f}%")
        else:
            print(f"  ⚖️  Same performance")
        
        results.append({
            'name': name,
            'n': n,
            'seed': seed,
            'baseline_length': baseline_length,
            'fixed_weight_length': fixed_length,
            'fixed_improvement': fixed_improvement,
            'adaptive_weight_used': adaptive_weight_used,
            'adaptive_length': adaptive_length,
            'adaptive_improvement': adaptive_improvement,
            'improvement_delta': adaptive_improvement - fixed_improvement
        })
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY:")
    
    improved_cases = sum(1 for r in results if r['improvement_delta'] > 0)
    worse_cases = sum(1 for r in results if r['improvement_delta'] < 0)
    equal_cases = sum(1 for r in results if r['improvement_delta'] == 0)
    
    print(f"Cases where adaptive rule improves: {improved_cases}/{len(results)}")
    print(f"Cases where adaptive rule worsens: {worse_cases}/{len(results)}")
    print(f"Cases with equal performance: {equal_cases}/{len(results)}")
    
    avg_improvement_delta = sum(r['improvement_delta'] for r in results) / len(results)
    print(f"Average improvement delta: {avg_improvement_delta:.3f}%")
    
    # Save results
    output_file = "improved_adaptive_rule_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    # Recommendations
    print(f"\n{'='*60}")
    print("RECOMMENDATIONS:")
    
    if avg_improvement_delta > 0:
        print("✅ Improved adaptive rule provides better average performance")
    else:
        print("⚠️  Improved adaptive rule needs further tuning")
    
    # Show detailed results
    print(f"\nDetailed results by problem size:")
    print("Size (n) | Adaptive Weight | Fixed Imp% | Adaptive Imp% | Delta")
    print("-" * 70)
    
    for r in results:
        print(f"{r['n']:8d} | {r['adaptive_weight_used']:15.1f} | {r['fixed_improvement']:10.2f} | {r['adaptive_improvement']:13.2f} | {r['improvement_delta']:6.2f}")

if __name__ == "__main__":
    test_adaptive_rule()