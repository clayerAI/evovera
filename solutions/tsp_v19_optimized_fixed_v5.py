#!/usr/bin/env python3
"""
Christofides Hybrid Structural Algorithm - OPTIMIZED VERSION (v5)
Includes 2-opt optimization like original.
"""

from typing import List, Tuple, Dict, Set, Optional
import math
import random
import numpy as np

class ChristofidesHybridStructuralOptimized:
    """Optimized Christofides hybrid structural algorithm."""
    
    def __init__(self, points: List[Tuple[float, float]], seed: int = 42):
        self.points = points
        self.n = len(points)
        self.seed = seed
        random.seed(seed)
        self.dist_matrix = self._compute_distance_matrix()
        self.parent_lca = None
        self.depth = None
        self.up = None
        self.log_n = None
    
    def _compute_distance_matrix(self) -> List[List[float]]:
        dist = [[0.0] * self.n for _ in range(self.n)]
        for i in range(self.n):
            xi, yi = self.points[i]
            for j in range(i + 1, self.n):
                xj, yj = self.points[j]
                d = math.sqrt((xi - xj) ** 2 + (yi - yj) ** 2)
                dist[i][j] = d
                dist[j][i] = d
        return dist
    
    def _compute_mst(self) -> Tuple[List[List[Tuple[int, float]]], List[int]]:
        n = self.n
        mst_adj = [[] for _ in range(n)]
        parent = [-1] * n
        visited = [False] * n
        min_edge = [float('inf')] * n
        min_edge[0] = 0.0
        
        for _ in range(n):
            u = -1
            for i in range(n):
                if not visited[i] and (u == -1 or min_edge[i] < min_edge[u]):
                    u = i
            
            visited[u] = True
            
            if parent[u] != -1:
                p = parent[u]
                weight = self.dist_matrix[u][p]
                mst_adj[u].append((p, weight))
                mst_adj[p].append((u, weight))
            
            for v in range(n):
                if not visited[v] and self.dist_matrix[u][v] < min_edge[v]:
                    min_edge[v] = self.dist_matrix[u][v]
                    parent[v] = u
        
        return mst_adj, parent
    
    def _build_lca_structure(self, parent: List[int]):
        n = self.n
        adj = [[] for _ in range(n)]
        for v in range(1, n):
            p = parent[v]
            adj[v].append(p)
            adj[p].append(v)
        
        depth = [0] * n
        stack = [(0, -1, 0)]
        while stack:
            node, par, d = stack.pop()
            depth[node] = d
            for neighbor in adj[node]:
                if neighbor != par:
                    stack.append((neighbor, node, d + 1))
        
        log_n = 1
        while (1 << log_n) <= n:
            log_n += 1
        
        up = [[-1] * log_n for _ in range(n)]
        for v in range(n):
            up[v][0] = parent[v] if parent[v] != -1 else v
        
        for j in range(1, log_n):
            for v in range(n):
                up[v][j] = up[up[v][j - 1]][j - 1]
        
        self.parent_lca = parent
        self.depth = depth
        self.up = up
        self.log_n = log_n
    
    def _lca(self, u: int, v: int) -> int:
        if self.depth[u] < self.depth[v]:
            u, v = v, u
        
        diff = self.depth[u] - self.depth[v]
        for j in range(self.log_n):
            if diff & (1 << j):
                u = self.up[u][j]
        
        if u == v:
            return u
        
        for j in range(self.log_n - 1, -1, -1):
            if self.up[u][j] != self.up[v][j]:
                u = self.up[u][j]
                v = self.up[v][j]
        
        return self.up[u][0]
    
    def _compute_edge_centrality(self, mst_adj: List[List[Tuple[int, float]]]) -> Dict[Tuple[int, int], float]:
        n = self.n
        adj = [[] for _ in range(n)]
        for u in range(n):
            for v, _ in mst_adj[u]:
                adj[u].append(v)
        
        visited = [False] * n
        edge_centrality = {}
        
        def dfs(node: int) -> int:
            visited[node] = True
            size = 1
            for neighbor in adj[node]:
                if not visited[neighbor]:
                    child_size = dfs(neighbor)
                    size += child_size
                    edge = (min(node, neighbor), max(node, neighbor))
                    edge_centrality[edge] = child_size * (n - child_size)
            return size
        
        dfs(0)
        
        if edge_centrality:
            max_val = max(edge_centrality.values())
            for edge in edge_centrality:
                edge_centrality[edge] /= max_val
        
        return edge_centrality
    
    def _detect_communities(self, mst_adj: List[List[Tuple[int, float]]], 
                           percentile_threshold: float = 70) -> Dict[int, int]:
        edge_weights = []
        for u in range(self.n):
            for v, weight in mst_adj[u]:
                if u < v:
                    edge_weights.append(weight)
        
        if not edge_weights:
            return {i: 0 for i in range(self.n)}
        
        cutoff = np.percentile(edge_weights, percentile_threshold)
        
        filtered_adj = [[] for _ in range(self.n)]
        for u in range(self.n):
            for v, weight in mst_adj[u]:
                if weight <= cutoff:
                    filtered_adj[u].append(v)
        
        visited = [False] * self.n
        community_id = 0
        communities = {}
        
        for i in range(self.n):
            if not visited[i]:
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
        
        return communities
    
    def _compute_path_centrality_lazy(self, u: int, v: int, 
                                     edge_centrality: Dict[Tuple[int, int], float]) -> float:
        if u == v:
            return 0.0
        
        lca = self._lca(u, v)
        total = 0.0
        
        node = u
        while node != lca:
            parent = self.parent_lca[node]
            edge = (min(node, parent), max(node, parent))
            total += edge_centrality.get(edge, 0.0)
            node = parent
        
        node = v
        while node != lca:
            parent = self.parent_lca[node]
            edge = (min(node, parent), max(node, parent))
            total += edge_centrality.get(edge, 0.0)
            node = parent
        
        path_length = self.depth[u] + self.depth[v] - 2 * self.depth[lca]
        if path_length > 0:
            total /= path_length
        
        return total
    
    def _hybrid_structural_matching_optimized(self, odd_vertices: List[int],
                                             communities: Dict[int, int],
                                             edge_centrality: Dict[Tuple[int, int], float],
                                             within_community_weight: float = 0.8,
                                             between_community_weight: float = 0.3) -> List[Tuple[int, int]]:
        k = len(odd_vertices)
        idx_to_vertex = {i: v for i, v in enumerate(odd_vertices)}
        
        dist_matrix = [[0.0] * k for _ in range(k)]
        for i in range(k):
            u = idx_to_vertex[i]
            for j in range(i + 1, k):
                v = idx_to_vertex[j]
                dist = self.dist_matrix[u][v]
                dist_matrix[i][j] = dist
                dist_matrix[j][i] = dist
        
        matched = [False] * k
        matching = []
        
        for i in range(k):
            if matched[i]:
                continue
            
            best_j = -1
            best_score = float('inf')
            u = idx_to_vertex[i]
            u_comm = communities.get(u, 0)
            
            for j in range(k):
                if i == j or matched[j]:
                    continue
                
                v = idx_to_vertex[j]
                v_comm = communities.get(v, 0)
                distance = dist_matrix[i][j]
                
                if u_comm == v_comm:
                    distance *= within_community_weight
                else:
                    distance *= between_community_weight
                
                path_cent = self._compute_path_centrality_lazy(u, v, edge_centrality)
                distance *= (1.0 - 0.5 * path_cent)
                
                if distance < best_score:
                    best_score = distance
                    best_j = j
            
            if best_j != -1:
                matched[i] = True
                matched[best_j] = True
                matching.append((idx_to_vertex[i], idx_to_vertex[best_j]))
        
        return matching
    
    def _apply_2opt(self, tour: List[int], time_limit: float = 60.0) -> Tuple[List[int], float]:
        n = self.n
        best_tour = tour[:]
        best_length = self._tour_length(tour)
        
        import time
        start_time = time.time()
        
        improved = True
        while improved:
            improved = False
            for i in range(1, n - 1):
                for j in range(i + 1, n):
                    if time.time() - start_time > time_limit:
                        return best_tour, best_length
                    
                    new_tour = best_tour[:i] + list(reversed(best_tour[i:j + 1])) + best_tour[j + 1:]
                    if new_tour[0] != new_tour[-1]:
                        new_tour.append(new_tour[0])
                    
                    new_length = self._tour_length(new_tour)
                    if new_length < best_length:
                        best_tour = new_tour
                        best_length = new_length
                        improved = True
                        break
                if improved:
                    break
        
        return best_tour, best_length
    
    def _tour_length(self, tour: List[int]) -> float:
        total = 0.0
        for i in range(len(tour) - 1):
            total += self.dist_matrix[tour[i]][tour[i + 1]]
        return total
    
    def solve(self, percentile_threshold: float = 70,
              within_community_weight: float = 0.8,
              between_community_weight: float = 0.3,
              apply_2opt: bool = True,
              time_limit: float = 60.0) -> Tuple[List[int], float, float]:
        import time
        start_time = time.time()
        
        n = self.n
        
        mst_adj, parent = self._compute_mst()
        self._build_lca_structure(parent)
        edge_centrality = self._compute_edge_centrality(mst_adj)
        communities = self._detect_communities(mst_adj, percentile_threshold)
        
        degrees = [0] * n
        for u in range(n):
            degrees[u] = len(mst_adj[u])
        odd_vertices = [i for i in range(n) if degrees[i] % 2 == 1]
        
        matching = self._hybrid_structural_matching_optimized(
            odd_vertices, communities, edge_centrality,
            within_community_weight, between_community_weight
        )
        
        euler_adj = [[] for _ in range(n)]
        for u in range(n):
            for v, weight in mst_adj[u]:
                if u < v:
                    euler_adj[u].append(v)
                    euler_adj[v].append(u)
        
        for u, v in matching:
            euler_adj[u].append(v)
            euler_adj[v].append(u)
        
        edge_count = {}
        for u in range(n):
            for v in euler_adj[u]:
                edge = (min(u, v), max(u, v))
                edge_count[edge] = edge_count.get(edge, 0) + 1
        
        circuit = []
        stack = [0]
        while stack:
            u = stack[-1]
            found = False
            for v in euler_adj[u]:
                edge = (min(u, v), max(u, v))
                if edge_count[edge] > 0:
                    edge_count[edge] -= 1
                    stack.append(v)
                    found = True
                    break
            if not found:
                circuit.append(stack.pop())
        
        circuit.reverse()
        
        visited = [False] * n
        tour = []
        for v in circuit:
            if not visited[v]:
                visited[v] = True
                tour.append(v)
        
        tour.append(tour[0])
        
        runtime = time.time() - start_time
        tour_length = self._tour_length(tour)
        
        if apply_2opt:
            remaining_time = max(0.0, time_limit - runtime)
            if remaining_time > 0:
                tour, tour_length = self._apply_2opt(tour, remaining_time)
                runtime = time.time() - start_time
        
        return tour, tour_length, runtime


def solve_tsp(points: List[Tuple[float, float]],
              distance_matrix: Optional[List[List[float]]] = None,
              seed: Optional[int] = None) -> Tuple[List[int], float]:
    solver = ChristofidesHybridStructuralOptimized(
        points=points,
        seed=seed if seed is not None else 42
    )
    
    tour, length, _ = solver.solve(
        percentile_threshold=70,
        within_community_weight=0.8,
        between_community_weight=0.3,
        apply_2opt=True
    )
    
    return tour, length


if __name__ == "__main__":
    import sys
    sys.path.append(".")
    
    random.seed(42)
    n = 50
    points = [(random.random() * 100, random.random() * 100) for _ in range(n)]
    
    solver = ChristofidesHybridStructuralOptimized(points, seed=42)
    tour, length, runtime = solver.solve(apply_2opt=True)
    
    print(f"Test with n={n}:")
    print(f"  Tour length: {length:.2f}")
    print(f"  Runtime: {runtime:.3f}s")
    print(f"  Tour: {tour[:5]}...{tour[-5:]}")
