#!/usr/bin/env python3
"""
Fix community detection in optimized algorithm.
"""

import sys
import os
sys.path.append('.')

import random
import numpy as np
from solutions.tsp_v19_optimized_fixed import ChristofidesHybridStructuralOptimized

def generate_random_points(n: int, seed: int = 42):
    """Generate n random points in unit square."""
    random.seed(seed)
    points = []
    for _ in range(n):
        x = random.random() * 100
        y = random.random() * 100
        points.append((x, y))
    return points

def analyze_community_difference():
    """Analyze why communities are different."""
    print("=== Analyzing Community Detection Difference ===")
    
    points = generate_random_points(50, seed=50)
    solver = ChristofidesHybridStructuralOptimized(points=points, seed=50)
    
    # Compute MST
    mst_adj, _ = solver._compute_mst()
    
    # Compute edge centrality
    edge_centrality = solver._compute_edge_centrality_optimized(mst_adj)
    
    print(f"Edge centrality stats:")
    values = list(edge_centrality.values())
    print(f"  Min: {min(values):.4f}")
    print(f"  Max: {max(values):.4f}")
    print(f"  Mean: {np.mean(values):.4f}")
    print(f"  Std: {np.std(values):.4f}")
    
    # Test different percentile thresholds
    print("\n=== Testing Different Percentile Thresholds ===")
    
    thresholds = [50, 60, 70, 80, 90]
    for threshold in thresholds:
        # Create copy of MST without high-centrality edges
        n = 50
        mst_copy = [[] for _ in range(n)]
        
        # Find threshold value
        centrality_values = list(edge_centrality.values())
        if not centrality_values:
            thresh_val = 0
        else:
            thresh_val = np.percentile(centrality_values, threshold)
        
        print(f"\nThreshold {threshold}% (value={thresh_val:.4f}):")
        
        edges_removed = 0
        for u in range(n):
            for v, weight in mst_adj[u]:
                if u < v:
                    edge = (u, v)
                    if edge in edge_centrality and edge_centrality[edge] >= thresh_val:
                        edges_removed += 1
                    else:
                        mst_copy[u].append((v, weight))
                        mst_copy[v].append((u, weight))
        
        print(f"  Edges removed: {edges_removed}")
        
        # Find connected components
        visited = [False] * n
        communities = {}
        community_id = 0
        
        for i in range(n):
            if not visited[i]:
                # BFS to find component
                queue = [i]
                visited[i] = True
                
                while queue:
                    u = queue.pop(0)
                    communities[u] = community_id
                    
                    for v, _ in mst_copy[u]:
                        if not visited[v]:
                            visited[v] = True
                            queue.append(v)
                
                community_id += 1
        
        print(f"  Communities: {community_id}")
        
        # Show community sizes
        community_sizes = {}
        for v, cid in communities.items():
            community_sizes[cid] = community_sizes.get(cid, 0) + 1
        
        print(f"  Community sizes: {list(community_sizes.values())}")

def test_fixed_community_detection():
    """Test with fixed community detection."""
    print("\n=== Testing Fixed Community Detection ===")
    
    # Copy the optimized algorithm and fix community detection
    import math
    from typing import List, Tuple, Dict, Set, Optional, Union
    
    class FixedChristofidesHybridStructuralOptimized:
        """Optimized algorithm with fixed community detection."""
        
        def __init__(self, points: Optional[List[Tuple[float, float]]] = None,
                     distance_matrix: Optional[Union[List[List[float]], np.ndarray]] = None,
                     seed: Optional[int] = None):
            if points is None and distance_matrix is None:
                raise ValueError("Must provide either points or distance_matrix")
            
            if points is not None:
                self.points = points
                self.n = len(points)
                self.distance_matrix = None
            else:
                self.points = None
                self.n = len(distance_matrix)
                self.distance_matrix = distance_matrix
            
            self.seed = seed if seed is not None else random.randint(1, 10000)
            random.seed(self.seed)
            
            # Precomputed data structures
            self._parent = None
            self._depth = None
            self._mst_adj = None
            self._edge_centrality = None
            self._communities = None
        
        def _compute_distance_matrix(self) -> List[List[float]]:
            if self.distance_matrix is not None:
                return self.distance_matrix
            
            n = self.n
            dist_matrix = [[0.0] * n for _ in range(n)]
            
            for i in range(n):
                xi, yi = self.points[i]
                for j in range(i + 1, n):
                    xj, yj = self.points[j]
                    dist = math.sqrt((xi - xj)**2 + (yi - yj)**2)
                    dist_matrix[i][j] = dist
                    dist_matrix[j][i] = dist
            
            return dist_matrix
        
        def _compute_mst(self) -> Tuple[List[List[Tuple[int, float]]], List[int]]:
            n = self.n
            dist_matrix = self._compute_distance_matrix()
            
            # Prim's algorithm
            in_mst = [False] * n
            min_edge = [float('inf')] * n
            parent = [-1] * n
            
            min_edge[0] = 0
            mst_adj = [[] for _ in range(n)]
            
            for _ in range(n):
                u = -1
                for v in range(n):
                    if not in_mst[v] and (u == -1 or min_edge[v] < min_edge[u]):
                        u = v
                
                in_mst[u] = True
                
                if parent[u] != -1:
                    weight = dist_matrix[u][parent[u]]
                    mst_adj[u].append((parent[u], weight))
                    mst_adj[parent[u]].append((u, weight))
                
                for v in range(n):
                    if not in_mst[v] and dist_matrix[u][v] < min_edge[v]:
                        min_edge[v] = dist_matrix[u][v]
                        parent[v] = u
            
            return mst_adj, parent
        
        def _compute_edge_centrality_optimized(self, mst_adj: List[List[Tuple[int, float]]]) -> Dict[Tuple[int, int], float]:
            n = self.n
            
            # Build parent-child relationships
            parent = [-1] * n
            children = [[] for _ in range(n)]
            visited = [False] * n
            queue = [0]
            visited[0] = True
            
            while queue:
                u = queue.pop(0)
                for v, _ in mst_adj[u]:
                    if not visited[v]:
                        visited[v] = True
                        parent[v] = u
                        children[u].append(v)
                        queue.append(v)
            
            # Compute subtree sizes
            subtree_size = [1] * n
            stack = [(0, False)]
            
            while stack:
                u, visited_children = stack.pop()
                
                if not visited_children:
                    stack.append((u, True))
                    for v in children[u]:
                        stack.append((v, False))
                else:
                    for v in children[u]:
                        subtree_size[u] += subtree_size[v]
            
            # Compute edge centrality
            edge_centrality = {}
            for u in range(n):
                for v in children[u]:
                    size_v = subtree_size[v]
                    centrality = size_v * (n - size_v)
                    edge_centrality[(min(u, v), max(u, v))] = centrality
            
            # Normalize
            max_centrality = max(edge_centrality.values()) if edge_centrality else 1
            edge_centrality = {edge: c / max_centrality for edge, c in edge_centrality.items()}
            
            return edge_centrality
        
        def _detect_communities_fixed(self, mst_adj: List[List[Tuple[int, float]]], 
                                     percentile_threshold: float = 70.0) -> Dict[int, int]:
            """
            Fixed community detection that matches original algorithm logic.
            """
            n = self.n
            
            # Compute edge centrality
            edge_centrality = self._compute_edge_centrality_optimized(mst_adj)
            
            # Find threshold - use same logic as original
            centrality_values = list(edge_centrality.values())
            if not centrality_values:
                return {i: 0 for i in range(n)}
            
            # Sort and find threshold
            sorted_values = sorted(centrality_values)
            idx = int(len(sorted_values) * percentile_threshold / 100)
            idx = min(idx, len(sorted_values) - 1)
            threshold = sorted_values[idx]
            
            print(f"  DEBUG: threshold={threshold:.4f} (percentile={percentile_threshold})")
            
            # Remove edges above threshold
            mst_copy = [[] for _ in range(n)]
            for u in range(n):
                for v, weight in mst_adj[u]:
                    if u < v:
                        edge = (u, v)
                        if edge in edge_centrality and edge_centrality[edge] >= threshold:
                            # Remove edge (don't add to copy)
                            pass
                        else:
                            mst_copy[u].append((v, weight))
                            mst_copy[v].append((u, weight))
            
            # Find connected components
            visited = [False] * n
            communities = {}
            community_id = 0
            
            for i in range(n):
                if not visited[i]:
                    queue = [i]
                    visited[i] = True
                    
                    while queue:
                        u = queue.pop(0)
                        communities[u] = community_id
                        
                        for v, _ in mst_copy[u]:
                            if not visited[v]:
                                visited[v] = True
                                queue.append(v)
                    
                    community_id += 1
            
            return communities
        
        def solve(self, percentile_threshold: float = 70.0) -> Tuple[List[int], float]:
            """Solve with fixed community detection."""
            # 1. Compute MST
            mst_adj, _ = self._compute_mst()
            
            # 2. Compute edge centrality
            edge_centrality = self._compute_edge_centrality_optimized(mst_adj)
            
            # 3. Detect communities (FIXED)
            communities = self._detect_communities_fixed(mst_adj, percentile_threshold)
            
            # 4. Find odd-degree vertices
            odd_vertices = []
            for i in range(self.n):
                if len(mst_adj[i]) % 2 == 1:
                    odd_vertices.append(i)
            
            # 5. Simple greedy matching (for testing)
            dist_matrix = self._compute_distance_matrix()
            k = len(odd_vertices)
            matched = [False] * k
            matching = []
            
            # Sort odd vertices by degree centrality
            odd_with_centrality = []
            for i, v in enumerate(odd_vertices):
                # Simple centrality: degree in MST
                centrality = len(mst_adj[v])
                odd_with_centrality.append((centrality, i, v))
            
            odd_with_centrality.sort(reverse=True)
            
            # Greedy matching
            for _, i, u in odd_with_centrality:
                if matched[i]:
                    continue
                
                # Find closest unmatched odd vertex
                best_j = -1
                best_dist = float('inf')
                
                for _, j, v in odd_with_centrality:
                    if i == j or matched[j]:
                        continue
                    
                    dist = dist_matrix[u][v]
                    if dist < best_dist:
                        best_dist = dist
                        best_j = j
                
                if best_j != -1:
                    matched[i] = matched[best_j] = True
                    v = odd_vertices[best_j]
                    matching.append((u, v))
            
            # 6. Find Eulerian tour
            multigraph_adj = [[] for _ in range(self.n)]
            for u in range(self.n):
                for v, _ in mst_adj[u]:
                    if u < v:
                        multigraph_adj[u].append(v)
                        multigraph_adj[v].append(u)
            
            for u, v in matching:
                multigraph_adj[u].append(v)
                multigraph_adj[v].append(u)
            
            # Hierholzer's algorithm
            stack = [0]
            eulerian_tour = []
            
            while stack:
                u = stack[-1]
                if multigraph_adj[u]:
                    v = multigraph_adj[u].pop()
                    multigraph_adj[v].remove(u)
                    stack.append(v)
                else:
                    eulerian_tour.append(stack.pop())
            
            eulerian_tour.reverse()
            
            # 7. Shortcut
            visited = [False] * self.n
            tour = []
            for vertex in eulerian_tour:
                if not visited[vertex]:
                    visited[vertex] = True
                    tour.append(vertex)
            
            # 8. Compute length
            length = 0.0
            for i in range(len(tour)):
                u = tour[i]
                v = tour[(i + 1) % len(tour)]
                length += dist_matrix[u][v]
            
            return tour, length
    
    # Test the fixed version
    points = generate_random_points(50, seed=50)
    
    print("\nTesting fixed algorithm:")
    solver = FixedChristofidesHybridStructuralOptimized(points=points, seed=50)
    
    for threshold in [60, 70, 80]:
        print(f"\nThreshold {threshold}%:")
        tour, length = solver.solve(percentile_threshold=threshold)
        print(f"  Tour length: {length:.2f}")
        print(f"  Valid tour: {len(set(tour)) == 50}")

if __name__ == "__main__":
    analyze_community_difference()
    test_fixed_community_detection()
