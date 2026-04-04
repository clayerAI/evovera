#!/usr/bin/env python3
"""
Diagnose v18 n=75 anomaly by examining community detection behavior.
"""

import sys
sys.path.append('/workspace/evovera/solutions')

from tsp_v18_christofides_community_detection import ChristofidesCommunityDetection
from tsp_v1_nearest_neighbor import solve_tsp as nn2opt_solve
import random
import time
import statistics
from collections import Counter

def analyze_communities(points, seed=42):
    """Analyze community detection for given points."""
    solver = ChristofidesCommunityDetection(points, seed=seed)
    
    # Compute MST
    mst_edges, mst_adj = solver._compute_mst()
    
    # Detect communities
    communities = solver._detect_communities(mst_adj)
    
    # Analyze community structure
    community_sizes = Counter(communities)
    num_communities = len(community_sizes)
    
    # Get odd degree vertices
    odd_vertices = solver._get_odd_degree_vertices(mst_adj)
    
    # Count odd vertices per community
    odd_by_community = Counter()
    for v in odd_vertices:
        odd_by_community[communities[v]] += 1
    
    return {
        'num_communities': num_communities,
        'community_sizes': dict(community_sizes),
        'odd_vertices_count': len(odd_vertices),
        'odd_by_community': dict(odd_by_community),
        'communities': communities
    }

def test_v18_detailed(n=75, seeds=[42, 43, 44, 45, 46]):
    """Detailed analysis of v18 performance."""
    print(f"Detailed Analysis of v18 at n={n}")
    print("=" * 70)
    
    for seed in seeds:
        print(f"\nSeed {seed}:")
        print("-" * 40)
        
        # Generate points
        random.seed(seed)
        points = [(random.random(), random.random()) for _ in range(n)]
        
        # Get baseline
        baseline_tour, baseline_length = nn2opt_solve(points)
        
        # Analyze v18
        solver = ChristofidesCommunityDetection(points, seed=seed)
        
        # Compute MST
        mst_edges, mst_adj = solver._compute_mst()
        
        # Detect communities
        communities = solver._detect_communities(mst_adj)
        
        # Analyze community structure
        community_sizes = Counter(communities)
        num_communities = len(community_sizes)
        
        # Get odd degree vertices
        odd_vertices = solver._get_odd_degree_vertices(mst_adj)
        
        # Count odd vertices per community
        odd_by_community = Counter()
        for v in odd_vertices:
            odd_by_community[communities[v]] += 1
        
        # Run full algorithm
        v18_tour, v18_length, runtime = solver.solve()
        
        improvement = ((baseline_length - v18_length) / baseline_length) * 100
        
        print(f"  Baseline length: {baseline_length:.4f}")
        print(f"  v18 length: {v18_length:.4f}")
        print(f"  Improvement: {improvement:.2f}%")
        print(f"  Number of communities: {num_communities}")
        print(f"  Community sizes: {sorted(community_sizes.values())}")
        print(f"  Odd vertices: {len(odd_vertices)}")
        print(f"  Odd vertices by community: {dict(odd_by_community)}")
        
        # Check if any community has odd number of odd vertices (problematic)
        problematic = []
        for comm_id, count in odd_by_community.items():
            if count % 2 == 1:
                problematic.append(comm_id)
        
        if problematic:
            print(f"  ⚠️  Problematic communities (odd count of odd vertices): {problematic}")
        else:
            print(f"  ✓ All communities have even count of odd vertices")
        
        # Check community size distribution
        if num_communities == 1:
            print(f"  ⚠️  Only 1 community detected (no community structure)")
        elif max(community_sizes.values()) > n * 0.8:
            print(f"  ⚠️  One community dominates (>80% of nodes)")
        
        # Check if improvement correlates with community structure
        if improvement > 0:
            print(f"  ✅ Positive improvement")
        else:
            print(f"  ❌ Negative improvement")

def analyze_mst_edge_weights(n=75, seeds=[42, 43, 44, 45, 46]):
    """Analyze MST edge weight distribution across seeds."""
    print(f"\nMST Edge Weight Analysis for n={n}")
    print("=" * 70)
    
    weight_stats = {}
    
    for seed in seeds:
        random.seed(seed)
        points = [(random.random(), random.random()) for _ in range(n)]
        
        solver = ChristofidesCommunityDetection(points, seed=seed)
        mst_edges, mst_adj = solver._compute_mst()
        
        weights = [w for _, _, w in mst_edges]
        
        weight_stats[seed] = {
            'min': min(weights),
            'max': max(weights),
            'mean': statistics.mean(weights),
            'median': statistics.median(weights),
            'std': statistics.stdev(weights) if len(weights) > 1 else 0
        }
    
    # Print comparison
    print(f"{'Seed':<6} {'Min':<8} {'Max':<8} {'Mean':<8} {'Median':<8} {'Std':<8}")
    print("-" * 50)
    
    for seed, stats in weight_stats.items():
        print(f"{seed:<6} {stats['min']:.6f} {stats['max']:.6f} {stats['mean']:.6f} "
              f"{stats['median']:.6f} {stats['std']:.6f}")

if __name__ == "__main__":
    print("Vera: Diagnosing v18 n=75 Anomaly")
    print("=" * 70)
    
    # Run detailed analysis
    test_v18_detailed(n=75, seeds=[42, 43, 44, 45, 46])
    
    # Analyze MST edge weights
    analyze_mst_edge_weights(n=75, seeds=[42, 43, 44, 45, 46])
    
    print("\n" + "=" * 70)
    print("Analysis complete.")