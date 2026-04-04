#!/usr/bin/env python3
"""
Test to demonstrate the greedy matching issue in Christofides algorithm.
The greedy matching quality depends on vertex ordering, causing significant variance.
"""

import sys
sys.path.append('.')
from solutions.tsp_v2_christofides import EuclideanTSPChristofides
import numpy as np
import random

def analyze_greedy_matching_issue():
    """Analyze the greedy matching issue in Christofides algorithm."""
    
    # Create instance with seed=42, n=100
    tsp = EuclideanTSPChristofides(n=100, seed=42)
    
    # Get MST and odd vertices
    mst_edges = tsp.prim_mst()
    odd_vertices = tsp.find_odd_degree_vertices(mst_edges)
    
    print(f"Number of odd vertices: {len(odd_vertices)}")
    print(f"Odd vertices: {odd_vertices[:10]}...")  # Show first 10
    
    # Test 1: Original greedy matching
    matching1 = tsp.greedy_minimum_matching(odd_vertices)
    matching_distance1 = sum(weight for u, v, weight in matching1)
    print(f"\nOriginal greedy matching:")
    print(f"  Matching edges: {len(matching1)}")
    print(f"  Total matching distance: {matching_distance1:.4f}")
    
    # Test 2: Shuffle odd vertices and run greedy matching
    random.seed(123)
    odd_shuffled = odd_vertices.copy()
    random.shuffle(odd_shuffled)
    
    matching2 = []
    matched = [False] * tsp.n
    odd_list = odd_shuffled.copy()
    
    while odd_list:
        u = odd_list.pop(0)
        if matched[u]:
            continue
        
        best_v = None
        best_dist = float('inf')
        
        for v in odd_list:
            if not matched[v]:
                dist = tsp.distance(u, v)
                if dist < best_dist:
                    best_dist = dist
                    best_v = v
        
        if best_v is not None:
            matching2.append((u, best_v, best_dist))
            matched[u] = True
            matched[best_v] = True
            odd_list.remove(best_v)
    
    matching_distance2 = sum(weight for u, v, weight in matching2)
    print(f"\nShuffled greedy matching (seed=123):")
    print(f"  Matching edges: {len(matching2)}")
    print(f"  Total matching distance: {matching_distance2:.4f}")
    print(f"  Difference: {abs(matching_distance1 - matching_distance2):.4f}")
    print(f"  Percent difference: {abs(matching_distance1 - matching_distance2)/matching_distance1*100:.2f}%")
    
    # Test 3: Sort odd vertices by distance from center (deterministic)
    center = np.array([0.5, 0.5])
    odd_sorted = sorted(odd_vertices, 
                       key=lambda v: np.linalg.norm(tsp.points[v] - center))
    
    matching3 = []
    matched = [False] * tsp.n
    odd_list = odd_sorted.copy()
    
    while odd_list:
        u = odd_list.pop(0)
        if matched[u]:
            continue
        
        best_v = None
        best_dist = float('inf')
        
        for v in odd_list:
            if not matched[v]:
                dist = tsp.distance(u, v)
                if dist < best_dist:
                    best_dist = dist
                    best_v = v
        
        if best_v is not None:
            matching3.append((u, best_v, best_dist))
            matched[u] = True
            matched[best_v] = True
            odd_list.remove(best_v)
    
    matching_distance3 = sum(weight for u, v, weight in matching3)
    print(f"\nSorted greedy matching (by distance from center):")
    print(f"  Matching edges: {len(matching3)}")
    print(f"  Total matching distance: {matching_distance3:.4f}")
    print(f"  Improvement over original: {(matching_distance1 - matching_distance3)/matching_distance1*100:.2f}%")
    
    # Test 4: Run full Christofides with different orderings
    print(f"\n--- Full Christofides Algorithm Results ---")
    
    # Original
    tour1, dist1 = tsp.christofides(apply_two_opt=True)
    print(f"Original Christofides: {dist1:.4f}")
    
    # Create modified class with deterministic ordering
    class ModifiedChristofides(EuclideanTSPChristofides):
        def greedy_minimum_matching(self, odd_vertices):
            """Greedy matching with deterministic ordering by distance from center."""
            if not odd_vertices:
                return []
            
            # Sort odd vertices by distance from center
            center = np.array([0.5, 0.5])
            odd_sorted = sorted(odd_vertices,
                              key=lambda v: np.linalg.norm(self.points[v] - center))
            
            matched = [False] * self.n
            matching_edges = []
            odd_list = odd_sorted.copy()
            
            while odd_list:
                u = odd_list.pop(0)
                if matched[u]:
                    continue
                
                best_v = None
                best_dist = float('inf')
                
                for v in odd_list:
                    if not matched[v]:
                        dist = self.distance(u, v)
                        if dist < best_dist:
                            best_dist = dist
                            best_v = v
                
                if best_v is not None:
                    matching_edges.append((u, best_v, best_dist))
                    matched[u] = True
                    matched[best_v] = True
                    odd_list.remove(best_v)
            
            return matching_edges
    
    # Test modified version
    tsp_mod = ModifiedChristofides(n=100, seed=42)
    tour2, dist2 = tsp_mod.christofides(apply_two_opt=True)
    print(f"Modified Christofides (deterministic): {dist2:.4f}")
    print(f"Improvement: {(dist1 - dist2)/dist1*100:.2f}%")
    
    return {
        "original_matching_distance": matching_distance1,
        "shuffled_matching_distance": matching_distance2,
        "sorted_matching_distance": matching_distance3,
        "original_christofides": dist1,
        "modified_christofides": dist2
    }

if __name__ == "__main__":
    results = analyze_greedy_matching_issue()
    
    # Save results
    import json
    with open("greedy_matching_analysis.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to greedy_matching_analysis.json")