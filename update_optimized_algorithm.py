#!/usr/bin/env python3
"""
Update optimized algorithm to match original community detection.
"""

import sys
import os
sys.path.append('.')

import random
import numpy as np
import math
from typing import List, Tuple, Dict, Set, Optional, Union

def update_optimized_algorithm():
    """Update the optimized algorithm file."""
    
    with open('solutions/tsp_v19_optimized_fixed.py', 'r') as f:
        content = f.read()
    
    # Find the _detect_communities method
    lines = content.split('\n')
    
    # Find start and end of _detect_communities
    start_idx = -1
    for i, line in enumerate(lines):
        if 'def _detect_communities' in line:
            start_idx = i
            break
    
    if start_idx == -1:
        print("ERROR: Could not find _detect_communities method")
        return
    
    # Find end of method (next method or end of class)
    end_idx = start_idx
    for i in range(start_idx + 1, len(lines)):
        if lines[i].strip().startswith('def ') or lines[i].strip().startswith('class '):
            end_idx = i
            break
        if i == len(lines) - 1:
            end_idx = len(lines)
    
    print(f"Found _detect_communities at lines {start_idx}-{end_idx}")
    
    # Replace with correct implementation
    new_method = '''    def _detect_communities(self, mst_adj: List[List[Tuple[int, float]]], 
                           percentile_threshold: float = 70) -> Dict[int, int]:
        """
        Detect communities in MST by analyzing edge weight distribution.
        
        Approach: Remove edges above percentile threshold, then find connected components.
        Higher percentile = fewer edges removed = fewer, larger communities.
        Lower percentile = more edges removed = more, smaller communities.
        
        Args:
            mst_adj: MST adjacency list
            percentile_threshold: Percentile for edge weight cutoff (0-100)
            
        Returns:
            Dictionary mapping vertex index to community ID
        """
        # Collect all MST edge weights
        edge_weights = []
        for u in range(self.n):
            for v, weight in mst_adj[u]:
                if u < v:  # Count each edge once
                    edge_weights.append(weight)
        
        if not edge_weights:
            # All vertices in same community
            return {i: 0 for i in range(self.n)}
        
        # Calculate cutoff weight at given percentile
        cutoff = np.percentile(edge_weights, percentile_threshold)
        
        # Build graph without edges above cutoff
        filtered_adj = [[] for _ in range(self.n)]
        for u in range(self.n):
            for v, weight in mst_adj[u]:
                if weight <= cutoff:
                    filtered_adj[u].append(v)
        
        # Find connected components (communities)
        visited = [False] * self.n
        community_id = 0
        communities = {}
        
        for i in range(self.n):
            if not visited[i]:
                # BFS to find component
                queue = [i]
                visited[i] = True
                
                while queue:
                    node = queue.pop(0)
                    communities[node] = community_id
                    
                    for neighbor in filtered_adj[node]:
                        if not visited[neighbor]:
                            visited[neighbor] = True
                            queue.append(neighbor)
                
                community_id += 1
        
        return communities'''
    
    # Replace the method
    new_lines = lines[:start_idx] + [new_method] + lines[end_idx:]
    
    # Also need to add numpy import if not present
    if 'import numpy as np' not in content:
        # Find the imports section
        import_section = -1
        for i, line in enumerate(new_lines):
            if 'import ' in line and 'def ' not in line and 'class ' not in line:
                import_section = i
                break
        
        if import_section != -1:
            new_lines.insert(import_section + 1, 'import numpy as np')
    
    # Write back
    with open('solutions/tsp_v19_optimized_fixed.py', 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("Updated _detect_communities method")
    
    # Now test the updated algorithm
    print("\n=== Testing Updated Algorithm ===")
    
    # Import the updated class
    sys.path.insert(0, '.')
    from solutions.tsp_v19_optimized_fixed import ChristofidesHybridStructuralOptimized
    
    def generate_random_points(n: int, seed: int = 42):
        random.seed(seed)
        points = []
        for _ in range(n):
            x = random.random() * 100
            y = random.random() * 100
            points.append((x, y))
        return points
    
    # Test with n=50
    points = generate_random_points(50, seed=50)
    
    print("Testing community detection:")
    solver = ChristofidesHybridStructuralOptimized(points=points, seed=50)
    
    mst_adj, _ = solver._compute_mst()
    communities = solver._detect_communities(mst_adj, percentile_threshold=70)
    
    print(f"Number of communities: {len(set(communities.values()))}")
    
    # Compare with original algorithm
    print("\nComparing with original algorithm:")
    
    # Import original
    from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected
    
    solver_orig = ChristofidesHybridStructuralCorrected(points=points, seed=50)
    mst_adj_orig, _ = solver_orig._compute_mst()
    communities_orig = solver_orig._detect_communities(mst_adj_orig, percentile_threshold=70)
    
    print(f"Original communities: {len(set(communities_orig.values()))}")
    
    # Check if communities match
    match_count = 0
    for i in range(50):
        if communities.get(i, -1) == communities_orig.get(i, -1):
            match_count += 1
    
    print(f"Vertices with same community: {match_count}/50 ({match_count/50*100:.1f}%)")
    
    # Run full solve
    print("\nRunning full solve (optimized):")
    tour, length = solver.solve(percentile_threshold=70)
    print(f"Tour length: {length:.2f}")
    print(f"Valid tour: {len(set(tour)) == 50}")
    
    # Run original solve
    print("\nRunning original solve:")
    result_orig = solver_orig.solve(percentile_threshold=70)
    if isinstance(result_orig, tuple):
        tour_orig, length_orig = result_orig
    else:
        tour_orig = result_orig
        # Compute length
        dist_matrix = solver_orig._compute_distance_matrix()
        length_orig = 0.0
        for i in range(len(tour_orig)):
            u = tour_orig[i]
            v = tour_orig[(i + 1) % len(tour_orig)]
            length_orig += dist_matrix[u][v]
    
    print(f"Original tour length: {length_orig:.2f}")
    print(f"Length difference: {((length - length_orig) / length_orig * 100):.1f}%")

if __name__ == "__main__":
    update_optimized_algorithm()
