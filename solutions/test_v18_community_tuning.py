#!/usr/bin/env python3
"""
Test different community detection parameters for v18.
"""

import sys
sys.path.append('/workspace/evovera/solutions')

from tsp_v18_christofides_community_detection import ChristofidesCommunityDetection
from tsp_v1_nearest_neighbor import solve_tsp as nn2opt_solve
import random
import time
import statistics

class TunedChristofidesCommunityDetection(ChristofidesCommunityDetection):
    """Variant with tunable community detection."""
    
    def __init__(self, points, seed=42, merge_threshold=0.5):
        super().__init__(points, seed=seed)
        self.merge_threshold = merge_threshold  # 0.5 = median, 0.75 = 75th percentile, etc.
    
    def _detect_communities(self, mst_adj):
        """Detect communities with tunable threshold."""
        n = self.n
        
        # Initialize each node as its own community
        communities = list(range(n))
        
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
        
        # Merge nodes connected by lighter edges (below threshold percentile)
        if edges:
            # Calculate threshold weight
            weights = [w for _, _, w in edges]
            threshold_idx = int(len(weights) * self.merge_threshold)
            threshold_weight = weights[threshold_idx] if threshold_idx < len(weights) else weights[-1]
            
            for u, v, w in edges:
                if w <= threshold_weight:
                    union(u, v)
        
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

def test_community_thresholds(n=75, seeds=[42, 43, 44, 45, 46]):
    """Test different merge thresholds for community detection."""
    print(f"Testing Community Detection Thresholds for n={n}")
    print("=" * 80)
    
    thresholds = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    
    results = {}
    
    for threshold in thresholds:
        print(f"\nThreshold = {threshold}:")
        print("-" * 40)
        
        improvements = []
        num_communities_list = []
        
        for seed in seeds:
            random.seed(seed)
            points = [(random.random(), random.random()) for _ in range(n)]
            
            # Get baseline
            baseline_tour, baseline_length = nn2opt_solve(points)
            
            # Test tuned v18
            solver = TunedChristofidesCommunityDetection(points, seed=seed, merge_threshold=threshold)
            
            # Run algorithm
            v18_tour, v18_length, runtime = solver.solve()
            
            improvement = ((baseline_length - v18_length) / baseline_length) * 100
            
            # Analyze communities
            mst_edges, mst_adj = solver._compute_mst()
            communities = solver._detect_communities(mst_adj)
            num_communities = len(set(communities))
            
            improvements.append(improvement)
            num_communities_list.append(num_communities)
            
            print(f"  Seed {seed}: Improvement={improvement:.2f}%, Communities={num_communities}")
        
        avg_improvement = statistics.mean(improvements)
        avg_communities = statistics.mean(num_communities_list)
        positive_count = sum(1 for imp in improvements if imp > 0)
        above_threshold_count = sum(1 for imp in improvements if imp > 0.1)
        
        print(f"  Average: Improvement={avg_improvement:.2f}%, Communities={avg_communities:.1f}")
        print(f"  Positive: {positive_count}/{len(seeds)}, Above 0.1%: {above_threshold_count}/{len(seeds)}")
        
        results[threshold] = {
            'avg_improvement': avg_improvement,
            'avg_communities': avg_communities,
            'positive_count': positive_count,
            'above_threshold_count': above_threshold_count,
            'improvements': improvements
        }
    
    # Find best threshold
    best_threshold = max(thresholds, key=lambda t: results[t]['avg_improvement'])
    best_result = results[best_threshold]
    
    print(f"\n{'='*80}")
    print(f"BEST THRESHOLD: {best_threshold}")
    print(f"  Average improvement: {best_result['avg_improvement']:.2f}%")
    print(f"  Average communities: {best_result['avg_communities']:.1f}")
    print(f"  Positive improvements: {best_result['positive_count']}/{len(seeds)}")
    print(f"  Above 0.1% threshold: {best_result['above_threshold_count']}/{len(seeds)}")
    
    return results, best_threshold

def test_combined_v16_v18(n=75, seeds=[42, 43, 44, 45, 46]):
    """Test combining v16's path-based centrality with v18's community detection."""
    print(f"\nTesting Combined v16+v18 Approach for n={n}")
    print("=" * 80)
    
    # First, let me check if we can import v16
    try:
        from tsp_v16_christofides_path_centrality import ChristofidesPathCentrality
        v16_available = True
    except ImportError:
        print("  v16 not available for import")
        v16_available = False
        return
    
    improvements = []
    
    for seed in seeds:
        random.seed(seed)
        points = [(random.random(), random.random()) for _ in range(n)]
        
        # Get baseline
        baseline_tour, baseline_length = nn2opt_solve(points)
        
        # IDEA: Use v16's path centrality to weight edges for community detection
        # Or use v16's matching within v18's communities
        
        # For now, just test v16 alone for comparison
        v16_solver = ChristofidesPathCentrality(points, seed=seed)
        v16_tour, v16_length, v16_runtime = v16_solver.solve()
        v16_improvement = ((baseline_length - v16_length) / baseline_length) * 100
        
        # Test v18 with best threshold
        v18_solver = TunedChristofidesCommunityDetection(points, seed=seed, merge_threshold=0.6)
        v18_tour, v18_length, v18_runtime = v18_solver.solve()
        v18_improvement = ((baseline_length - v18_length) / baseline_length) * 100
        
        print(f"  Seed {seed}: v16={v16_improvement:.2f}%, v18={v18_improvement:.2f}%")
        improvements.append(v18_improvement)
    
    avg_improvement = statistics.mean(improvements)
    positive_count = sum(1 for imp in improvements if imp > 0)
    
    print(f"\n  Average v18 improvement: {avg_improvement:.2f}%")
    print(f"  Positive improvements: {positive_count}/{len(seeds)}")

if __name__ == "__main__":
    print("Vera: Tuning v18 Community Detection")
    print("=" * 80)
    
    # Test different community detection thresholds
    results, best_threshold = test_community_thresholds(n=75, seeds=[42, 43, 44, 45, 46])
    
    # Test combined approach if v16 is available
    test_combined_v16_v18(n=75, seeds=[42, 43, 44, 45, 46])
    
    print("\n" + "=" * 80)
    print("Analysis complete. Key insight: Community detection threshold needs tuning.")