import numpy as np
import time
from typing import List, Tuple, Dict
import math

class ChristofidesHybridStructuralOptimizedV7:
    def __init__(self, points: np.ndarray):
        self.points = points
        self.n = len(points)
        self.dist_matrix = None
        
    def _compute_distance_matrix(self) -> None:
        """Compute Euclidean distance matrix."""
        self.dist_matrix = np.zeros((self.n, self.n))
        for i in range(self.n):
            for j in range(i + 1, self.n):
                dx = self.points[i][0] - self.points[j][0]
                dy = self.points[i][1] - self.points[j][1]
                dist = math.sqrt(dx * dx + dy * dy)
                self.dist_matrix[i][j] = dist
                self.dist_matrix[j][i] = dist
    
    def _compute_mst(self) -> List[List[Tuple[int, float]]]:
        """Compute Minimum Spanning Tree using Prim's algorithm."""
        visited = [False] * self.n
        min_edge = [float('inf')] * self.n
        parent = [-1] * self.n
        mst_adj = [[] for _ in range(self.n)]
        
        min_edge[0] = 0
        for _ in range(self.n):
            # Find minimum edge
            v = -1
            for j in range(self.n):
                if not visited[j] and (v == -1 or min_edge[j] < min_edge[v]):
                    v = j
            
            visited[v] = True
            
            # Add edge to MST
            if parent[v] != -1:
                weight = self.dist_matrix[v][parent[v]]
                mst_adj[v].append((parent[v], weight))
                mst_adj[parent[v]].append((v, weight))
            
            # Update min edges
            for to in range(self.n):
                if not visited[to] and self.dist_matrix[v][to] < min_edge[to]:
                    min_edge[to] = self.dist_matrix[v][to]
                    parent[to] = v
        
        return mst_adj
    
    def _detect_communities(self, mst_adj: List[List[Tuple[int, float]]], 
                           percentile_threshold: float = 70) -> Dict[int, int]:
        """Detect communities by removing long MST edges."""
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
    
    def _compute_edge_centrality(self, mst_adj: List[List[Tuple[int, float]]]) -> Dict[Tuple[int, int], float]:
        """Compute edge centrality based on MST structure."""
        # Simple centrality: inverse of edge weight (shorter edges are more central)
        edge_centrality = {}
        for u in range(self.n):
            for v, weight in mst_adj[u]:
                if u < v:
                    # Normalize: centrality = 1 / (1 + weight/avg_weight)
                    edge_centrality[(u, v)] = 1.0 / (1.0 + weight)
        return edge_centrality
    
    def _find_odd_degree_vertices(self, mst_adj: List[List[Tuple[int, float]]]) -> List[int]:
        """Find vertices with odd degree in MST."""
        odd_vertices = []
        for i in range(self.n):
            if len(mst_adj[i]) % 2 == 1:
                odd_vertices.append(i)
        return odd_vertices
    
    def _hybrid_structural_matching_fast(self, odd_vertices: List[int],
                                         communities: Dict[int, int],
                                         edge_centrality: Dict[Tuple[int, int], float],
                                         within_community_weight: float = 0.8,
                                         between_community_weight: float = 0.3) -> List[Tuple[int, int]]:
        """Fast matching with precomputed path centralities."""
        k = len(odd_vertices)
        if k == 0:
            return []
        
        # Precompute all pairwise distances and community info
        dists = np.zeros((k, k))
        comm_matrix = np.zeros((k, k), dtype=int)
        
        for i in range(k):
            u = odd_vertices[i]
            u_comm = communities.get(u, 0)
            for j in range(i + 1, k):
                v = odd_vertices[j]
                dists[i][j] = self.dist_matrix[u][v]
                dists[j][i] = dists[i][j]
                comm_matrix[i][j] = 1 if u_comm == communities.get(v, 0) else 0
                comm_matrix[j][i] = comm_matrix[i][j]
        
        # Greedy matching
        matched = [False] * k
        matching = []
        
        for i in range(k):
            if matched[i]:
                continue
            
            best_j = -1
            best_score = float('inf')
            
            for j in range(k):
                if i == j or matched[j]:
                    continue
                
                distance = dists[i][j]
                
                # Simple centrality approximation: use edge between i and j if exists in MST
                # Otherwise use average centrality
                u, v = odd_vertices[i], odd_vertices[j]
                edge_key = (min(u, v), max(u, v))
                centrality = edge_centrality.get(edge_key, 0.5)  # Default 0.5
                
                # Adjust distance based on community and centrality
                if comm_matrix[i][j] == 1:  # Same community
                    distance *= (1.0 - within_community_weight * centrality)
                else:  # Different communities
                    distance *= (1.0 - between_community_weight * centrality)
                
                if distance < best_score:
                    best_score = distance
                    best_j = j
            
            if best_j != -1:
                matched[i] = True
                matched[best_j] = True
                matching.append((odd_vertices[i], odd_vertices[best_j]))
        
        return matching
    
    def _build_eulerian_tour(self, mst_adj: List[List[Tuple[int, float]]], 
                            matching: List[Tuple[int, int]]) -> List[int]:
        """Build Eulerian tour from MST and matching."""
        # Combine MST and matching into multigraph
        multigraph = [[] for _ in range(self.n)]
        for u in range(self.n):
            for v, _ in mst_adj[u]:
                multigraph[u].append(v)
        
        for u, v in matching:
            multigraph[u].append(v)
            multigraph[v].append(u)
        
        # Find Eulerian tour using Hierholzer's algorithm
        tour = []
        stack = [0]
        
        while stack:
            v = stack[-1]
            if multigraph[v]:
                u = multigraph[v].pop()
                # Remove reverse edge
                if v in multigraph[u]:
                    multigraph[u].remove(v)
                stack.append(u)
            else:
                tour.append(stack.pop())
        
        return tour[::-1]
    
    def _shortcut_eulerian_tour(self, eulerian_tour: List[int]) -> List[int]:
        """Convert Eulerian tour to Hamiltonian tour by shortcutting."""
        visited = [False] * self.n
        tour = []
        
        for node in eulerian_tour:
            if not visited[node]:
                visited[node] = True
                tour.append(node)
        
        return tour
    
    def _tour_length(self, tour: List[int]) -> float:
        """Compute tour length."""
        total = 0.0
        for i in range(len(tour) - 1):
            total += self.dist_matrix[tour[i]][tour[i + 1]]
        return total
    
    def _optimized_2opt(self, tour: List[int], time_limit: float = 30.0) -> Tuple[List[int], float]:
        """Optimized 2-opt with incremental updates and candidate lists."""
        n = len(tour) - 1  # Exclude closing node
        if n <= 3:
            return tour, self._tour_length(tour)
        
        # Remove closing node for processing
        if tour[0] == tour[-1]:
            tour = tour[:-1]
        
        current_length = 0.0
        for i in range(n):
            current_length += self.dist_matrix[tour[i]][tour[(i + 1) % n]]
        
        best_tour = tour[:]
        best_length = current_length
        
        start_time = time.time()
        
        # Build nearest neighbor lists (once)
        k = min(20, n // 10)
        nn_lists = []
        for i in range(n):
            distances = [(self.dist_matrix[tour[i]][tour[j]], j) for j in range(n) if j != i]
            distances.sort()
            nn_lists.append([j for _, j in distances[:k]])
        
        improved = True
        while improved:
            improved = False
            
            for i in range(n):
                if time.time() - start_time > time_limit:
                    # Add closing node back
                    best_tour.append(best_tour[0])
                    return best_tour, best_length
                
                i1 = i
                i2 = (i + 1) % n
                
                # Check promising j candidates
                for j_idx in nn_lists[i1]:
                    j = j_idx
                    j1 = j
                    j2 = (j + 1) % n
                    
                    if j1 == i2 or j2 == i1:  # Skip adjacent edges
                        continue
                    
                    # Calculate delta incrementally
                    a, b, c, d = tour[i1], tour[i2], tour[j1], tour[j2]
                    
                    old_cost = self.dist_matrix[a][b] + self.dist_matrix[c][d]
                    new_cost = self.dist_matrix[a][c] + self.dist_matrix[b][d]
                    
                    delta = new_cost - old_cost
                    
                    if delta < -1e-9:  # Improvement
                        # Reverse segment between i2 and j1
                        if i2 < j1:
                            segment = tour[i2:j1+1]
                            tour[i2:j1+1] = segment[::-1]
                        else:
                            # Wrap around case
                            segment = tour[i2:] + tour[:j1+1]
                            reversed_segment = segment[::-1]
                            tour[i2:] = reversed_segment[:len(tour)-i2]
                            tour[:j1+1] = reversed_segment[len(tour)-i2:]
                        
                        current_length += delta
                        
                        if current_length < best_length:
                            best_tour = tour[:]
                            best_length = current_length
                        
                        improved = True
                        break  # Restart search
                
                if improved:
                    break
        
        # Add closing node back
        best_tour.append(best_tour[0])
        return best_tour, best_length
    
    def solve(self) -> Tuple[List[int], float, float]:
        """Solve TSP using optimized Christofides hybrid structural algorithm."""
        import time
        start_time = time.time()
        
        # Build distance matrix
        self._compute_distance_matrix()
        
        # Compute MST
        mst_adj = self._compute_mst()
        
        # Detect communities
        communities = self._detect_communities(mst_adj)
        
        # Compute edge centrality
        edge_centrality = self._compute_edge_centrality(mst_adj)
        
        # Find odd-degree vertices
        odd_vertices = self._find_odd_degree_vertices(mst_adj)
        
        # Perform fast hybrid structural matching
        matching = self._hybrid_structural_matching_fast(
            odd_vertices, communities, edge_centrality
        )
        
        # Build Eulerian tour
        eulerian_tour = self._build_eulerian_tour(mst_adj, matching)
        
        # Convert to Hamiltonian tour
        tour = self._shortcut_eulerian_tour(eulerian_tour)
        
        # Close the tour
        if tour[0] != tour[-1]:
            tour.append(tour[0])
        
        # Apply optimized 2-opt
        tour, tour_length = self._optimized_2opt(tour, time_limit=60.0)
        
        end_time = time.time()
        time_taken = end_time - start_time
        
        return tour, tour_length, time_taken

# Test the optimized algorithm
if __name__ == "__main__":
    np.random.seed(42)
    
    # Test with increasing sizes
    for n in [50, 100, 200, 300]:
        points = np.random.rand(n, 2) * 1000
        
        solver = ChristofidesHybridStructuralOptimizedV7(points)
        
        start = time.time()
        tour, length, _ = solver.solve()
        elapsed = time.time() - start
        
        print(f"n={n}: length={length:.2f}, time={elapsed:.2f}s")
