#!/usr/bin/env python3
"""
Analyze v16 inconsistency across different seeds.
Vera's review shows v16 has inconsistent performance:
Seed 42: +1.61% ✅
Seed 123: -1.24% ❌  
Seed 456: +1.21% ✅
Seed 789: -0.39% ❌
Seed 999: +6.60% ✅

Goal: Understand why performance varies and optimize for consistency.
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v16_christofides_path_centrality import ChristofidesPathCentrality
from tsp_v2_christofides import solve_tsp as christofides_solve
import numpy as np
import random
import time
from typing import List, Tuple
import json

def generate_random_points(n: int = 50, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def analyze_v16_components(points: List[Tuple[float, float]], seed: int = 42):
    """Analyze different components of v16 algorithm."""
    solver = ChristofidesPathCentrality(points, seed=seed)
    
    # 1. Compute MST
    mst_adj, parent = solver._compute_mst()
    
    # 2. Compute edge centrality
    edge_centrality = solver._compute_edge_centrality(mst_adj)
    
    # 3. Build MST paths and compute path centrality
    mst_paths = solver._build_mst_paths(mst_adj)
    path_centrality = solver._compute_path_centrality(mst_paths, edge_centrality)
    
    # 4. Find odd degree vertices
    odd_vertices = solver._find_odd_degree_vertices(mst_adj)
    
    # Analyze edge centrality distribution
    centrality_values = list(edge_centrality.values())
    
    # Analyze path centrality distribution for odd vertex pairs
    odd_path_centralities = []
    for i in range(len(odd_vertices)):
        u = odd_vertices[i]
        for j in range(i + 1, len(odd_vertices)):
            v = odd_vertices[j]
            key = (min(u, v), max(u, v))
            if key in path_centrality:
                odd_path_centralities.append(path_centrality[key])
    
    # Analyze MST structure
    mst_degrees = [len(adj) for adj in mst_adj]
    
    return {
        'seed': seed,
        'n_points': len(points),
        'n_odd_vertices': len(odd_vertices),
        'edge_centrality_stats': {
            'min': min(centrality_values) if centrality_values else 0,
            'max': max(centrality_values) if centrality_values else 0,
            'mean': sum(centrality_values) / len(centrality_values) if centrality_values else 0,
            'std': np.std(centrality_values) if centrality_values else 0
        },
        'path_centrality_stats': {
            'min': min(odd_path_centralities) if odd_path_centralities else 0,
            'max': max(odd_path_centralities) if odd_path_centralities else 0,
            'mean': sum(odd_path_centralities) / len(odd_path_centralities) if odd_path_centralities else 0,
            'std': np.std(odd_path_centralities) if odd_path_centralities else 0
        },
        'mst_stats': {
            'avg_degree': sum(mst_degrees) / len(mst_degrees),
            'max_degree': max(mst_degrees),
            'min_degree': min(mst_degrees)
        }
    }

def test_different_centrality_weights(points: List[Tuple[float, float]], seed: int = 42):
    """Test v16 with different centrality weights."""
    solver = ChristofidesPathCentrality(points, seed=seed)
    
    weights = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    results = []
    
    for weight in weights:
        tour, length, runtime = solver.solve(centrality_weight=weight, apply_2opt=True)
        results.append({
            'weight': weight,
            'length': length,
            'runtime': runtime
        })
    
    return results

def compare_seeds(n: int = 50):
    """Compare v16 performance across different seeds."""
    seeds = [42, 123, 456, 789, 999]
    results = []
    
    for seed in seeds:
        points = generate_random_points(n=n, seed=seed)
        points_array = np.array(points)
        
        # Standard Christofides
        christofides_tour, christofides_length = christofides_solve(points_array)
        
        # v16 with different weights
        solver = ChristofidesPathCentrality(points, seed=seed)
        
        # Test default weight (0.3)
        v16_tour, v16_length, v16_runtime = solver.solve(centrality_weight=0.3, apply_2opt=True)
        
        # Test best weight from optimization
        weight_results = test_different_centrality_weights(points, seed)
        best_result = min(weight_results, key=lambda x: x['length'])
        
        improvement_default = (christofides_length - v16_length) / christofides_length * 100
        improvement_best = (christofides_length - best_result['length']) / christofides_length * 100
        
        # Analyze components
        component_analysis = analyze_v16_components(points, seed)
        
        results.append({
            'seed': seed,
            'christofides_length': christofides_length,
            'v16_length_default': v16_length,
            'v16_length_best': best_result['length'],
            'improvement_default': improvement_default,
            'improvement_best': improvement_best,
            'best_weight': best_result['weight'],
            'component_analysis': component_analysis
        })
        
        print(f"Seed {seed}:")
        print(f"  Christofides: {christofides_length:.4f}")
        print(f"  v16 (weight=0.3): {v16_length:.4f} ({improvement_default:.2f}%)")
        print(f"  v16 (best weight={best_result['weight']}): {best_result['length']:.4f} ({improvement_best:.2f}%)")
        print(f"  Edge centrality mean: {component_analysis['edge_centrality_stats']['mean']:.3f}")
        print(f"  Path centrality mean: {component_analysis['path_centrality_stats']['mean']:.3f}")
        print(f"  Odd vertices: {component_analysis['n_odd_vertices']}")
        print()
    
    return results

def analyze_correlation(results):
    """Analyze correlation between component metrics and performance."""
    import numpy as np
    
    seeds = [r['seed'] for r in results]
    improvements = [r['improvement_default'] for r in results]
    
    # Extract metrics
    edge_centrality_means = [r['component_analysis']['edge_centrality_stats']['mean'] for r in results]
    path_centrality_means = [r['component_analysis']['path_centrality_stats']['mean'] for r in results]
    edge_centrality_stds = [r['component_analysis']['edge_centrality_stats']['std'] for r in results]
    path_centrality_stds = [r['component_analysis']['path_centrality_stats']['std'] for r in results]
    n_odd_vertices = [r['component_analysis']['n_odd_vertices'] for r in results]
    
    # Calculate correlations
    correlations = {}
    
    if len(improvements) > 1:
        correlations['edge_centrality_mean'] = np.corrcoef(edge_centrality_means, improvements)[0, 1] if len(edge_centrality_means) > 1 else 0
        correlations['path_centrality_mean'] = np.corrcoef(path_centrality_means, improvements)[0, 1] if len(path_centrality_means) > 1 else 0
        correlations['edge_centrality_std'] = np.corrcoef(edge_centrality_stds, improvements)[0, 1] if len(edge_centrality_stds) > 1 else 0
        correlations['path_centrality_std'] = np.corrcoef(path_centrality_stds, improvements)[0, 1] if len(path_centrality_stds) > 1 else 0
        correlations['n_odd_vertices'] = np.corrcoef(n_odd_vertices, improvements)[0, 1] if len(n_odd_vertices) > 1 else 0
    
    print("\n=== CORRELATION ANALYSIS ===")
    for metric, corr in correlations.items():
        print(f"{metric}: {corr:.3f}")
        
        if abs(corr) > 0.5:
            if corr > 0:
                print(f"  Strong positive correlation: Higher {metric} → Better improvement")
            else:
                print(f"  Strong negative correlation: Higher {metric} → Worse improvement")
    
    return correlations

def main():
    print("Analyzing v16 inconsistency across seeds")
    print("=" * 60)
    
    n = 50
    results = compare_seeds(n)
    
    # Save results
    with open(f'/workspace/evovera/v16_inconsistency_analysis_n{n}.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Analyze correlations
    correlations = analyze_correlation(results)
    
    # Identify patterns
    print("\n=== PATTERN ANALYSIS ===")
    
    # Group by performance
    good_seeds = [r for r in results if r['improvement_default'] > 0]
    bad_seeds = [r for r in results if r['improvement_default'] <= 0]
    
    print(f"Good seeds (positive improvement): {[r['seed'] for r in good_seeds]}")
    print(f"Bad seeds (negative improvement): {[r['seed'] for r in bad_seeds]}")
    
    if good_seeds and bad_seeds:
        # Compare averages
        avg_edge_centrality_good = sum(r['component_analysis']['edge_centrality_stats']['mean'] for r in good_seeds) / len(good_seeds)
        avg_edge_centrality_bad = sum(r['component_analysis']['edge_centrality_stats']['mean'] for r in bad_seeds) / len(bad_seeds)
        
        avg_path_centrality_good = sum(r['component_analysis']['path_centrality_stats']['mean'] for r in good_seeds) / len(good_seeds)
        avg_path_centrality_bad = sum(r['component_analysis']['path_centrality_stats']['mean'] for r in bad_seeds) / len(bad_seeds)
        
        print(f"\nAverage edge centrality:")
        print(f"  Good seeds: {avg_edge_centrality_good:.3f}")
        print(f"  Bad seeds: {avg_edge_centrality_bad:.3f}")
        print(f"  Difference: {avg_edge_centrality_good - avg_edge_centrality_bad:.3f}")
        
        print(f"\nAverage path centrality:")
        print(f"  Good seeds: {avg_path_centrality_good:.3f}")
        print(f"  Bad seeds: {avg_path_centrality_bad:.3f}")
        print(f"  Difference: {avg_path_centrality_good - avg_path_centrality_bad:.3f}")
    
    # Recommendations
    print("\n=== RECOMMENDATIONS ===")
    
    if correlations.get('path_centrality_mean', 0) > 0.5:
        print("1. Path centrality mean strongly correlates with performance")
        print("   → Consider adaptive centrality weight based on path centrality distribution")
    
    if correlations.get('edge_centrality_std', 0) < -0.5:
        print("2. Edge centrality std negatively correlates with performance")
        print("   → High variance in edge centrality may hurt matching quality")
        print("   → Consider normalizing centrality scores")
    
    # Check if weight optimization helps
    weight_improvements = []
    for r in results:
        if r['improvement_best'] > r['improvement_default']:
            weight_improvements.append(r['improvement_best'] - r['improvement_default'])
    
    if weight_improvements:
        avg_weight_improvement = sum(weight_improvements) / len(weight_improvements)
        print(f"3. Weight optimization improves performance by {avg_weight_improvement:.2f}% on average")
        print("   → Implement adaptive weight selection based on instance characteristics")
    
    print("\n4. Consider implementing:")
    print("   - Instance classification (good vs bad for v16)")
    print("   - Adaptive centrality weight based on MST structure")
    print("   - Fallback to standard Christofides for problematic instances")
    print("   - Ensemble approach combining multiple centrality measures")

if __name__ == "__main__":
    main()