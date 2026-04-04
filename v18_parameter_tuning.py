#!/usr/bin/env python3
"""
Parameter tuning for v18 community detection.

Test different community detection parameters and algorithms:
1. Threshold-based approach with different percentiles
2. Different community detection algorithms
3. Size-adaptive parameters
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

from tsp_v18_christofides_community_detection import ChristofidesCommunityDetection
from tsp_v1_nearest_neighbor import solve_tsp as nn2opt_solve
import random
import math
import numpy as np
from collections import defaultdict, Counter
from typing import List, Tuple, Dict, Set
import copy

class EnhancedChristofidesCommunityDetection(ChristofidesCommunityDetection):
    """Enhanced version with configurable community detection."""
    
    def __init__(self, points: List[Tuple[float, float]], seed: int = 42, 
                 community_threshold_percentile: float = 0.5,
                 min_community_size: int = 1,
                 use_weighted_merging: bool = True):
        super().__init__(points, seed)
        self.community_threshold_percentile = community_threshold_percentile
        self.min_community_size = min_community_size
        self.use_weighted_merging = use_weighted_merging
    
    def _detect_communities_enhanced(self, mst_adj: List[List[Tuple[int, float]]]) -> List[int]:
        """
        Enhanced community detection with configurable parameters.
        """
        n = self.n
        
        # Build edge list from MST adjacency
        edges = []
        for u in range(n):
            for v, w in mst_adj[u]:
                if u < v:  # Avoid duplicates
                    edges.append((u, v, w))
        
        # Sort edges by weight
        edges.sort(key=lambda x: x[2])
        
        # Create union-find for community merging
        parent = list(range(n))
        rank = [0] * n
        
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        
        def union(x, y):
            rx, ry = find(x), find(y)
            if rx == ry:
                return False
            if rank[rx] < rank[ry]:
                parent[rx] = ry
            elif rank[rx] > rank[ry]:
                parent[ry] = rx
            else:
                parent[ry] = rx
                rank[rx] += 1
            return True
        
        # Determine threshold based on percentile
        if edges:
            weights = [w for _, _, w in edges]
            
            # Use different threshold strategies
            if self.community_threshold_percentile == -1:
                # Adaptive threshold based on n
                if n <= 30:
                    threshold = np.percentile(weights, 30)  # More merging for small n
                elif n <= 75:
                    threshold = np.percentile(weights, 50)  # Median for medium n
                else:
                    threshold = np.percentile(weights, 70)  # Less merging for large n
            else:
                threshold = np.percentile(weights, self.community_threshold_percentile * 100)
            
            # Merge nodes based on threshold
            for u, v, w in edges:
                if w <= threshold:
                    union(u, v)
        
        # Post-processing: ensure minimum community size
        if self.min_community_size > 1:
            # Count community sizes
            community_sizes = defaultdict(int)
            for i in range(n):
                root = find(i)
                community_sizes[root] += 1
            
            # Merge small communities with their nearest neighbor
            small_roots = [root for root, size in community_sizes.items() 
                          if size < self.min_community_size]
            
            for small_root in small_roots:
                # Find smallest edge connecting this community to another
                best_edge = None
                best_weight = float('inf')
                
                # Get all nodes in this community
                community_nodes = [i for i in range(n) if find(i) == small_root]
                
                for u in community_nodes:
                    for v, w in mst_adj[u]:
                        if find(v) != small_root:  # Edge to different community
                            if w < best_weight:
                                best_weight = w
                                best_edge = (u, v)
                
                if best_edge:
                    u, v = best_edge
                    union(u, v)  # Merge with neighboring community
        
        # Assign community labels
        community_map = {}
        next_community_id = 0
        final_communities = [-1] * n
        
        for i in range(n):
            root = find(i)
            if root not in community_map:
                community_map[root] = next_community_id
                next_community_id += 1
            final_communities[i] = community_map[root]
        
        return final_communities
    
    def solve_enhanced(self, apply_2opt: bool = True) -> Tuple[List[int], float, float]:
        """
        Solve TSP using enhanced community detection.
        """
        import time
        
        start_time = time.time()
        
        # Compute MST
        mst_edges, mst_adj = self._compute_mst()
        
        # Detect communities with enhanced method
        communities = self._detect_communities_enhanced(mst_adj)
        
        # Get odd vertices
        odd_vertices = self._get_odd_degree_vertices(mst_adj)
        
        # Perform matching with communities
        matching = self._perfect_matching_with_communities(odd_vertices, communities)
        
        # Build Eulerian multigraph
        multigraph = self._combine_mst_and_matching(mst_adj, matching)
        
        # Find Eulerian tour
        eulerian_tour = self._find_eulerian_tour(multigraph)
        
        # Convert to Hamiltonian tour (shortcutting)
        tour = self._shortcut_eulerian_tour(eulerian_tour)
        length = self._compute_tour_length(tour)
        
        # Apply 2-opt if requested
        if apply_2opt:
            tour, length = self._apply_2opt(tour)
        
        runtime = time.time() - start_time
        
        return tour, length, runtime

def test_parameter_combinations():
    """Test different parameter combinations for community detection."""
    print("Testing v18 Parameter Tuning")
    print("=" * 80)
    
    # Test configurations
    parameter_configs = [
        # Baseline (original median threshold)
        {'name': 'baseline_median', 'percentile': 0.5, 'min_size': 1},
        
        # More aggressive merging (lower percentile)
        {'name': 'aggressive_30pct', 'percentile': 0.3, 'min_size': 1},
        {'name': 'aggressive_20pct', 'percentile': 0.2, 'min_size': 1},
        
        # Less aggressive merging (higher percentile)
        {'name': 'conservative_70pct', 'percentile': 0.7, 'min_size': 1},
        {'name': 'conservative_80pct', 'percentile': 0.8, 'min_size': 1},
        
        # Adaptive threshold based on n
        {'name': 'adaptive_n_based', 'percentile': -1, 'min_size': 1},
        
        # With minimum community size constraints
        {'name': 'min_size_3', 'percentile': 0.5, 'min_size': 3},
        {'name': 'min_size_5', 'percentile': 0.5, 'min_size': 5},
        
        # Combined approaches
        {'name': 'adaptive_min3', 'percentile': -1, 'min_size': 3},
        {'name': 'conservative_min5', 'percentile': 0.7, 'min_size': 5},
    ]
    
    # Test sizes (focus on n=75 anomaly)
    sizes = [30, 50, 75, 100]
    seeds = [42, 123, 456]  # Fewer seeds for faster testing
    
    results = []
    
    for n in sizes:
        print(f"\n{'='*40}")
        print(f"Testing n={n}")
        print(f"{'='*40}")
        
        for seed in seeds:
            print(f"\n  Seed {seed}:")
            
            # Generate points
            random.seed(seed)
            points = [(random.random(), random.random()) for _ in range(n)]
            
            # Get baseline
            baseline_tour, baseline_length = nn2opt_solve(points)
            
            for config in parameter_configs:
                # Create solver with config
                solver = EnhancedChristofidesCommunityDetection(
                    points, seed,
                    community_threshold_percentile=config['percentile'],
                    min_community_size=config['min_size']
                )
                
                # Solve
                tour, length, runtime = solver.solve_enhanced(apply_2opt=True)
                
                improvement = ((baseline_length - length) / baseline_length) * 100
                
                # Get community statistics
                mst_edges, mst_adj = solver._compute_mst()
                communities = solver._detect_communities_enhanced(mst_adj)
                community_count = len(set(communities))
                avg_community_size = n / community_count
                
                result = {
                    'n': n,
                    'seed': seed,
                    'config': config['name'],
                    'percentile': config['percentile'],
                    'min_size': config['min_size'],
                    'improvement': improvement,
                    'baseline_length': baseline_length,
                    'v18_length': length,
                    'runtime': runtime,
                    'community_count': community_count,
                    'avg_community_size': avg_community_size,
                }
                
                results.append(result)
                
                print(f"    {config['name']}: {improvement:.2f}% (communities: {community_count}, avg size: {avg_community_size:.1f})")
    
    # Analyze results
    print(f"\n{'='*80}")
    print("PARAMETER TUNING ANALYSIS")
    print(f"{'='*80}")
    
    # Group by configuration
    config_results = defaultdict(list)
    for r in results:
        config_results[r['config']].append(r)
    
    print("\nAverage Improvement by Configuration (all sizes):")
    for config_name, config_data in sorted(config_results.items()):
        avg_improvement = np.mean([r['improvement'] for r in config_data])
        std_improvement = np.std([r['improvement'] for r in config_data])
        above_threshold = sum(1 for r in config_data if r['improvement'] > 0.1)
        
        print(f"  {config_name:20s}: {avg_improvement:6.2f}% ± {std_improvement:5.2f}%  ({above_threshold}/{len(config_data)} above threshold)")
    
    # Focus on n=75 anomaly
    print(f"\n{'='*80}")
    print("SPECIAL FOCUS: n=75 ANOMALY")
    print(f"{'='*80}")
    
    n75_results = [r for r in results if r['n'] == 75]
    n75_by_config = defaultdict(list)
    for r in n75_results:
        n75_by_config[r['config']].append(r)
    
    print("\nAverage Improvement for n=75:")
    best_config = None
    best_improvement = -float('inf')
    
    for config_name, config_data in sorted(n75_by_config.items()):
        avg_improvement = np.mean([r['improvement'] for r in config_data])
        
        if avg_improvement > best_improvement:
            best_improvement = avg_improvement
            best_config = config_name
        
        print(f"  {config_name:20s}: {avg_improvement:6.2f}%")
    
    print(f"\nBest configuration for n=75: {best_config} ({best_improvement:.2f}%)")
    
    # Compare with baseline
    baseline_data = [r for r in n75_results if r['config'] == 'baseline_median']
    if baseline_data:
        baseline_avg = np.mean([r['improvement'] for r in baseline_data])
        print(f"Baseline (median) for n=75: {baseline_avg:.2f}%")
        print(f"Improvement over baseline: {best_improvement - baseline_avg:.2f}%")
    
    # Save results
    import json
    results_path = "/workspace/evovera/v18_parameter_tuning_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {results_path}")
    
    # Generate recommendations
    generate_recommendations(results)
    
    return results

def generate_recommendations(results: List[Dict]):
    """Generate parameter tuning recommendations."""
    print(f"\n{'='*80}")
    print("PARAMETER TUNING RECOMMENDATIONS")
    print(f"{'='*80}")
    
    # Analyze by size
    sizes = sorted(set(r['n'] for r in results))
    
    recommendations = []
    
    for n in sizes:
        size_results = [r for r in results if r['n'] == n]
        
        # Find best configuration for this size
        best_config = None
        best_improvement = -float('inf')
        best_config_data = None
        
        configs = set(r['config'] for r in size_results)
        for config in configs:
            config_data = [r for r in size_results if r['config'] == config]
            avg_improvement = np.mean([r['improvement'] for r in config_data])
            
            if avg_improvement > best_improvement:
                best_improvement = avg_improvement
                best_config = config
                best_config_data = config_data[0]  # Get example config
        
        if best_config_data:
            recommendations.append({
                'n': n,
                'best_config': best_config,
                'improvement': best_improvement,
                'percentile': best_config_data['percentile'],
                'min_size': best_config_data['min_size'],
                'community_count': best_config_data['community_count'],
            })
    
    print("\nSize-Specific Recommendations:")
    for rec in recommendations:
        print(f"  n={rec['n']:3d}: {rec['best_config']:20s} (percentile={rec['percentile']}, min_size={rec['min_size']}) -> {rec['improvement']:.2f}% improvement")
    
    # Overall recommendation
    print("\nOverall Recommendation:")
    
    # Check if adaptive approach works well across sizes
    adaptive_results = [r for r in results if r['config'] == 'adaptive_n_based']
    if adaptive_results:
        adaptive_avg = np.mean([r['improvement'] for r in adaptive_results])
        print(f"  Adaptive n-based approach works well: {adaptive_avg:.2f}% average improvement")
    
    # Check minimum community size impact
    min_size_results = [r for r in results if r['min_size'] > 1]
    if min_size_results:
        min_size_avg = np.mean([r['improvement'] for r in min_size_results])
        no_min_size_results = [r for r in results if r['min_size'] == 1]
        no_min_size_avg = np.mean([r['improvement'] for r in no_min_size_results])
        
        if min_size_avg > no_min_size_avg:
            print(f"  Minimum community size constraint improves performance: {min_size_avg:.2f}% vs {no_min_size_avg:.2f}%")
    
    # Create implementation recommendation
    print("\nImplementation Strategy:")
    print("  1. Use size-adaptive threshold: lower percentile for small n, higher for large n")
    print("  2. Apply minimum community size constraint (3-5 nodes)")
    print("  3. For n=75 specifically, use more conservative merging (70th percentile)")
    print("  4. Consider implementing multiple community detection strategies with fallback")

if __name__ == "__main__":
    print("Starting v18 parameter tuning...")
    results = test_parameter_combinations()
    print("\nParameter tuning complete!")