#!/usr/bin/env python3
"""
Test adaptive weight selection for v16.
Find optimal centrality_weight for different problem instances.
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v16_christofides_path_centrality import ChristofidesPathCentrality
from tsp_v1_nearest_neighbor import solve_tsp as nn2opt_solve
import random
import time
from typing import List, Tuple
import json

def generate_random_points(n: int = 50, seed: int = 42):
    """Generate random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def test_weight_sensitivity(points, seed: int = 42):
    """Test v16 with different centrality weights."""
    weights = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    
    # Get baseline
    baseline_tour, baseline_length = nn2opt_solve(points)
    
    results = []
    for weight in weights:
        solver = ChristofidesPathCentrality(points, seed=seed)
        v16_tour, v16_length, _ = solver.solve(centrality_weight=weight, apply_2opt=True)
        improvement = ((baseline_length - v16_length) / baseline_length) * 100
        
        results.append({
            'weight': weight,
            'v16_length': v16_length,
            'improvement': improvement
        })
    
    # Find best weight
    best_result = max(results, key=lambda x: x['improvement'])
    
    return {
        'baseline_length': baseline_length,
        'results': results,
        'best_weight': best_result['weight'],
        'best_improvement': best_result['improvement']
    }

def analyze_instance_characteristics(points):
    """Analyze instance characteristics that might inform weight selection."""
    n = len(points)
    
    # Simple characteristics for now
    # In a more sophisticated version, we could analyze:
    # - MST structure
    # - Path centrality distribution
    # - Point distribution patterns
    
    # For now, return simple metrics
    return {
        'n': n,
        'characteristics': 'random_uniform'  # Placeholder
    }

def adaptive_weight_selection(instance_characteristics):
    """Select weight based on instance characteristics."""
    # Simple rule for now: use 0.3 for random uniform instances
    # This could be expanded with ML or heuristic rules
    return 0.3

def main():
    print("Adaptive Weight Selection Analysis for v16")
    print("=" * 60)
    
    # Test with different instances
    instances = [
        {'n': 50, 'seed': 42, 'name': 'small_random'},
        {'n': 50, 'seed': 123, 'name': 'small_random_alt'},
        {'n': 100, 'seed': 42, 'name': 'medium_random'},
    ]
    
    all_results = {}
    
    for instance in instances:
        n = instance['n']
        seed = instance['seed']
        name = instance['name']
        
        print(f"\nTesting instance: {name} (n={n}, seed={seed})")
        
        points = generate_random_points(n=n, seed=seed)
        
        # Analyze instance
        characteristics = analyze_instance_characteristics(points)
        
        # Test weight sensitivity
        sensitivity_result = test_weight_sensitivity(points, seed=seed)
        
        # Try adaptive selection
        adaptive_weight = adaptive_weight_selection(characteristics)
        solver = ChristofidesPathCentrality(points, seed=seed)
        adaptive_tour, adaptive_length, _ = solver.solve(centrality_weight=adaptive_weight, apply_2opt=True)
        baseline_length = sensitivity_result['baseline_length']
        adaptive_improvement = ((baseline_length - adaptive_length) / baseline_length) * 100
        
        # Compare with best weight
        best_weight = sensitivity_result['best_weight']
        best_improvement = sensitivity_result['best_improvement']
        
        # Find the result for the best weight
        best_result_data = next(r for r in sensitivity_result['results'] if r['weight'] == best_weight)
        
        print(f"  Baseline (NN+2opt): {baseline_length:.4f}")
        print(f"  Adaptive weight ({adaptive_weight}): {adaptive_length:.4f} ({adaptive_improvement:.2f}%)")
        print(f"  Best weight ({best_weight}): {best_result_data['v16_length']:.4f} ({best_improvement:.2f}%)")
        
        if adaptive_improvement > 0.1:
            print(f"  ✅ Adaptive weight beats 0.1% threshold")
        else:
            print(f"  ❌ Adaptive weight below threshold")
        
        # Store results
        all_results[name] = {
            'instance': instance,
            'characteristics': characteristics,
            'sensitivity': sensitivity_result,
            'adaptive_weight': adaptive_weight,
            'adaptive_improvement': adaptive_improvement,
            'best_weight': best_weight,
            'best_improvement': best_improvement
        }
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY:")
    
    adaptive_success = 0
    total_instances = len(instances)
    
    for name, result in all_results.items():
        if result['adaptive_improvement'] > 0.1:
            adaptive_success += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"{name}: adaptive={result['adaptive_weight']} ({result['adaptive_improvement']:.2f}%) {status}")
    
    print(f"\nAdaptive weight success rate: {adaptive_success}/{total_instances}")
    
    # Save results
    output_file = "adaptive_weight_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nResults saved to {output_file}")
    
    # Recommendations
    print(f"\n{'='*60}")
    print("RECOMMENDATIONS:")
    
    if adaptive_success == total_instances:
        print("✅ Current adaptive rule (weight=0.3) works well for tested instances")
    else:
        print("⚠️  Need to improve adaptive weight selection rules")
        print("   Consider analyzing:")
        print("   - MST structure complexity")
        print("   - Path centrality distribution")
        print("   - Instance size (n)")
        print("   - Point distribution patterns")

if __name__ == "__main__":
    main()