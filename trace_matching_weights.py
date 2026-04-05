#!/usr/bin/env python3
"""
Trace matching weights to find differences.
"""

import sys
import random
sys.path.append('.')

def main():
    n = 10  # Small for tracing
    random.seed(42)
    points = [(random.random() * 100, random.random() * 100) for _ in range(n)]
    
    print("=== TRACING MATCHING WEIGHTS ===\n")
    
    # Run original and capture intermediate values
    print("Running original algorithm with tracing...")
    
    # We'll modify the original algorithm to trace
    from solutions.tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected
    
    # Create a subclass that adds tracing
    class TracingOriginal(ChristofidesHybridStructuralCorrected):
        def _hybrid_structural_matching(self, odd_vertices, communities, path_centrality, 
                                       within_community_weight=0.8, between_community_weight=0.3):
            k = len(odd_vertices)
            
            # Build complete graph on odd vertices
            odd_dist = [[0.0] * k for _ in range(k)]
            weight_details = {}  # Store computed weights for each pair
            
            for i in range(k):
                u = odd_vertices[i]
                for j in range(i + 1, k):
                    v = odd_vertices[j]
                    dist = self.dist_matrix[u][v]
                    
                    # Get community relationship
                    comm_u = communities.get(u, 0)
                    comm_v = communities.get(v, 0)
                    
                    # Get path centrality
                    centrality = path_centrality.get((min(u, v), max(u, v)), 0.0)
                    
                    # Apply hybrid weighting
                    if comm_u == comm_v:
                        weight = dist * (1.0 - within_community_weight * centrality)
                        comm_type = "same"
                    else:
                        weight = dist * (1.0 - between_community_weight * centrality)
                        comm_type = "diff"
                    
                    odd_dist[i][j] = weight
                    odd_dist[j][i] = weight
                    
                    # Store details
                    key = (u, v)
                    weight_details[key] = {
                        'dist': dist,
                        'centrality': centrality,
                        'weight': weight,
                        'comm_type': comm_type,
                        'comm_u': comm_u,
                        'comm_v': comm_v
                    }
            
            # Greedy matching
            visited = [False] * k
            matching = []
            matching_order = []
            
            for i in range(k):
                if not visited[i]:
                    best_j = -1
                    best_weight = float('inf')
                    
                    for j in range(i + 1, k):
                        if not visited[j] and odd_dist[i][j] < best_weight:
                            best_weight = odd_dist[i][j]
                            best_j = j
                    
                    if best_j != -1:
                        u = odd_vertices[i]
                        v = odd_vertices[best_j]
                        matching.append((u, v))
                        matching_order.append({
                            'step': len(matching_order),
                            'u': u, 'v': v,
                            'weight': best_weight,
                            'details': weight_details[(u, v)]
                        })
                        visited[i] = True
                        visited[best_j] = True
            
            return matching, matching_order, weight_details
    
    # Run tracing original
    solver_orig = TracingOriginal(points=points, seed=42)
    
    # We need to run solve to get the matching
    result = solver_orig.solve(percentile_threshold=70.0)
    tour_orig, length_orig, _ = result
    
    # But we need to intercept the matching call
    # Let me instead manually compute what the original would do
    print("\nManually computing original matching...")
    
    # Get odd vertices (simulate what Christofides would do)
    # Actually, let me just run the full algorithm and add print statements
    print("\n=== RUNNING ORIGINAL WITH DEBUG ===")
    
    # Create another subclass with debug prints
    class DebugOriginal(ChristofidesHybridStructuralCorrected):
        def _hybrid_structural_matching(self, odd_vertices, communities, path_centrality, 
                                       within_community_weight=0.8, between_community_weight=0.3):
            print(f"\n[ORIGINAL] Odd vertices: {odd_vertices}")
            print(f"[ORIGINAL] Communities: {communities}")
            
            k = len(odd_vertices)
            odd_dist = [[0.0] * k for _ in range(k)]
            
            print("\n[ORIGINAL] Computing weights:")
            for i in range(k):
                u = odd_vertices[i]
                for j in range(i + 1, k):
                    v = odd_vertices[j]
                    dist = self.dist_matrix[u][v]
                    
                    comm_u = communities.get(u, 0)
                    comm_v = communities.get(v, 0)
                    
                    centrality = path_centrality.get((min(u, v), max(u, v)), 0.0)
                    
                    if comm_u == comm_v:
                        weight = dist * (1.0 - within_community_weight * centrality)
                        comm_type = "same"
                    else:
                        weight = dist * (1.0 - between_community_weight * centrality)
                        comm_type = "diff"
                    
                    odd_dist[i][j] = weight
                    odd_dist[j][i] = weight
                    
                    print(f"  ({u},{v}): dist={dist:.2f}, centrality={centrality:.4f}, "
                          f"comm={comm_type}({comm_u},{comm_v}), weight={weight:.4f}")
            
            # Greedy matching
            visited = [False] * k
            matching = []
            
            print("\n[ORIGINAL] Greedy matching steps:")
            for i in range(k):
                if not visited[i]:
                    best_j = -1
                    best_weight = float('inf')
                    
                    for j in range(i + 1, k):
                        if not visited[j] and odd_dist[i][j] < best_weight:
                            best_weight = odd_dist[i][j]
                            best_j = j
                    
                    if best_j != -1:
                        u = odd_vertices[i]
                        v = odd_vertices[best_j]
                        matching.append((u, v))
                        visited[i] = True
                        visited[best_j] = True
                        print(f"  Step {len(matching)}: matched ({u},{v}) with weight {best_weight:.4f}")
            
            print(f"[ORIGINAL] Final matching: {matching}")
            return matching
    
    solver_debug_orig = DebugOriginal(points=points, seed=42)
    result_debug = solver_debug_orig.solve(percentile_threshold=70.0)
    
    print("\n=== RUNNING OPTIMIZED WITH DEBUG ===")
    
    # Now do the same for optimized
    from solutions.tsp_v19_optimized_fixed_v2 import ChristofidesHybridStructuralOptimized
    
    class DebugOptimized(ChristofidesHybridStructuralOptimized):
        def _hybrid_structural_matching_optimized(self, odd_vertices, communities, edge_centrality,
                                                 within_community_weight=0.8, between_community_weight=0.3):
            print(f"\n[OPTIMIZED] Odd vertices: {odd_vertices}")
            print(f"[OPTIMIZED] Communities: {communities}")
            
            k = len(odd_vertices)
            dist_matrix = self._compute_distance_matrix()
            odd_dist = [[0.0] * k for _ in range(k)]
            
            print("\n[OPTIMIZED] Computing base distances:")
            for i in range(k):
                u = odd_vertices[i]
                for j in range(i + 1, k):
                    v = odd_vertices[j]
                    dist = dist_matrix[u][v]
                    odd_dist[i][j] = dist
                    odd_dist[j][i] = dist
                    print(f"  ({u},{v}): dist={dist:.2f}")
            
            # Greedy matching with community-aware weights
            matched = [False] * k
            matching = []
            step = 0
            
            print("\n[OPTIMIZED] Greedy matching steps (global minimum):")
            while True:
                min_weight = float('inf')
                min_pair = (-1, -1)
                min_details = None
                
                for i in range(k):
                    if matched[i]:
                        continue
                    
                    for j in range(i + 1, k):
                        if matched[j]:
                            continue
                        
                        u = odd_vertices[i]
                        v = odd_vertices[j]
                        
                        # Base distance
                        weight = odd_dist[i][j]
                        
                        # Apply community-based weighting
                        if communities[u] == communities[v]:
                            path_cent = self._compute_path_centrality_lazy(u, v, edge_centrality)
                            adjusted = weight * (1.0 - within_community_weight * path_cent)
                            comm_type = "same"
                        else:
                            path_cent = self._compute_path_centrality_lazy(u, v, edge_centrality)
                            adjusted = weight * (1.0 - between_community_weight * path_cent)
                            comm_type = "diff"
                        
                        if adjusted < min_weight:
                            min_weight = adjusted
                            min_pair = (i, j)
                            min_details = {
                                'u': u, 'v': v,
                                'dist': weight,
                                'centrality': path_cent,
                                'adjusted': adjusted,
                                'comm_type': comm_type
                            }
                
                if min_pair[0] == -1:
                    break
                
                i, j = min_pair
                matched[i] = matched[j] = True
                u = odd_vertices[i]
                v = odd_vertices[j]
                matching.append((u, v))
                step += 1
                
                print(f"  Step {step}: matched ({u},{v}) with "
                      f"dist={min_details['dist']:.2f}, "
                      f"centrality={min_details['centrality']:.4f}, "
                      f"adjusted={min_details['adjusted']:.4f}, "
                      f"comm={min_details['comm_type']}")
            
            print(f"[OPTIMIZED] Final matching: {matching}")
            return matching
    
    solver_debug_opt = DebugOptimized(points=points, seed=42)
    result_opt = solver_debug_opt.solve(percentile_threshold=70.0)

if __name__ == "__main__":
    main()
