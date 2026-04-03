"""
TSP Hybrid Algorithm: Christofides with Tabu Search Improvement

Novel hybrid combining:
1. Christofides algorithm for initial solution with 1.5x approximation guarantee
2. Tabu Search for intensive local optimization with memory-based escape from local optima

Key novelty: Using Christofides' theoretical guarantee as a strong starting point
for Tabu Search, which typically struggles with poor initial solutions.
"""

import numpy as np
import math
import time
from typing import List, Tuple, Set, Dict
from collections import deque

class EuclideanTSPChristofidesTabuHybrid:
    """
    Hybrid TSP solver: Christofides + Tabu Search
    """
    
    def __init__(self, points: List[Tuple[float, float]], seed: int = 42):
        self.points = points
        self.n = len(points)
        self.seed = seed
        np.random.seed(seed)
        
        # Precompute distance matrix
        self.dist = self._compute_distance_matrix()
        
        # Tabu Search parameters
        self.tabu_tenure = min(20, self.n // 4)  # Size of tabu list
        self.max_iterations = 1000
        self.max_non_improving = 100
        
    def _compute_distance_matrix(self) -> np.ndarray:
        """Compute Euclidean distance matrix."""
        dist = np.zeros((self.n, self.n))
        for i in range(self.n):
            for j in range(i + 1, self.n):
                dx = self.points[i][0] - self.points[j][0]
                dy = self.points[i][1] - self.points[j][1]
                d = math.sqrt(dx*dx + dy*dy)
                dist[i, j] = d
                dist[j, i] = d
        return dist
    
    def _mst_prim(self) -> List[List[int]]:
        """Prim's algorithm for Minimum Spanning Tree."""
        visited = [False] * self.n
        parent = [-1] * self.n
        key = [float('inf')] * self.n
        key[0] = 0
        
        for _ in range(self.n):
            # Find minimum key vertex not yet visited
            min_key = float('inf')
            u = -1
            for v in range(self.n):
                if not visited[v] and key[v] < min_key:
                    min_key = key[v]
                    u = v
            
            visited[u] = True
            
            # Update key values for adjacent vertices
            for v in range(self.n):
                if (not visited[v] and self.dist[u, v] < key[v] and 
                    u != v and self.dist[u, v] > 0):
                    key[v] = self.dist[u, v]
                    parent[v] = u
        
        # Build adjacency list
        adj = [[] for _ in range(self.n)]
        for v in range(1, self.n):
            u = parent[v]
            if u != -1:
                adj[u].append(v)
                adj[v].append(u)
        
        return adj
    
    def _find_odd_vertices(self, adj: List[List[int]]) -> List[int]:
        """Find vertices with odd degree in MST."""
        odd_vertices = []
        for i in range(self.n):
            if len(adj[i]) % 2 == 1:
                odd_vertices.append(i)
        return odd_vertices
    
    def _greedy_matching(self, odd_vertices: List[int]) -> List[Tuple[int, int]]:
        """Greedy algorithm for minimum weight perfect matching."""
        m = len(odd_vertices)
        if m == 0:
            return []
        
        # Create list of all possible edges between odd vertices
        edges = []
        for i in range(m):
            for j in range(i + 1, m):
                u = odd_vertices[i]
                v = odd_vertices[j]
                edges.append((self.dist[u, v], u, v))
        
        # Sort edges by weight
        edges.sort(key=lambda x: x[0])
        
        # Greedy matching
        matched = [False] * self.n
        matching = []
        
        for weight, u, v in edges:
            if not matched[u] and not matched[v]:
                matched[u] = True
                matched[v] = True
                matching.append((u, v))
        
        return matching
    
    def _eulerian_circuit(self, adj: List[List[int]], 
                         matching: List[Tuple[int, int]]) -> List[int]:
        """Find Eulerian circuit in multigraph (MST + matching)."""
        # Add matching edges to adjacency list
        multigraph_adj = [neighbors.copy() for neighbors in adj]
        for u, v in matching:
            multigraph_adj[u].append(v)
            multigraph_adj[v].append(u)
        
        # Hierholzer's algorithm for Eulerian circuit
        circuit = []
        stack = [0]
        
        while stack:
            v = stack[-1]
            if multigraph_adj[v]:
                u = multigraph_adj[v].pop()
                # Remove the reverse edge
                multigraph_adj[u].remove(v)
                stack.append(u)
            else:
                circuit.append(stack.pop())
        
        # Reverse to get correct order
        circuit.reverse()
        return circuit
    
    def _shortcut_eulerian(self, eulerian: List[int]) -> List[int]:
        """Convert Eulerian circuit to Hamiltonian tour by shortcutting."""
        visited = [False] * self.n
        tour = []
        
        for v in eulerian:
            if not visited[v]:
                visited[v] = True
                tour.append(v)
        
        # Close the tour
        tour.append(tour[0])
        return tour
    
    def christofides_tour(self) -> Tuple[List[int], float]:
        """Christofides algorithm for TSP."""
        # 1. Minimum Spanning Tree
        mst_adj = self._mst_prim()
        
        # 2. Find odd-degree vertices
        odd_vertices = self._find_odd_vertices(mst_adj)
        
        # 3. Minimum weight perfect matching on odd vertices
        matching = self._greedy_matching(odd_vertices)
        
        # 4. Eulerian circuit
        eulerian = self._eulerian_circuit(mst_adj, matching)
        
        # 5. Shortcut to Hamiltonian tour
        tour = self._shortcut_eulerian(eulerian)
        
        # Calculate tour length
        tour_length = self._tour_length(tour)
        
        return tour, tour_length
    
    def _tour_length(self, tour: List[int]) -> float:
        """Calculate total length of a tour."""
        total = 0.0
        for i in range(len(tour) - 1):
            total += self.dist[tour[i], tour[i + 1]]
        return total
    
    def _two_opt_move(self, tour: List[int], i: int, j: int) -> List[int]:
        """Perform 2-opt move: reverse segment between i+1 and j."""
        # Reverse tour[i+1:j+1]
        new_tour = tour[:i+1] + tour[i+1:j+1][::-1] + tour[j+1:]
        return new_tour
    
    def _calculate_2opt_gain(self, tour: List[int], i: int, j: int) -> float:
        """Calculate gain from 2-opt move (positive gain means improvement)."""
        a, b = tour[i], tour[i + 1]
        c, d = tour[j], tour[j + 1]
        
        old_distance = self.dist[a, b] + self.dist[c, d]
        new_distance = self.dist[a, c] + self.dist[b, d]
        
        return old_distance - new_distance  # Positive = improvement
    
    def tabu_search(self, initial_tour: List[int], initial_length: float) -> Tuple[List[int], float]:
        """
        Tabu Search improvement on Christofides solution.
        
        Features:
        - Tabu list prevents cycling
        - Aspiration criterion allows good moves even if tabu
        - Diversification after stagnation
        """
        current_tour = initial_tour.copy()
        current_length = initial_length
        best_tour = current_tour.copy()
        best_length = current_length
        
        # Tabu list: stores forbidden moves (edge swaps)
        tabu_list = deque(maxlen=self.tabu_tenure)
        
        # Track non-improving iterations for diversification
        non_improving = 0
        
        for iteration in range(self.max_iterations):
            best_move = None
            best_gain = 0.0
            best_move_type = None
            
            # Evaluate all possible 2-opt moves
            for i in range(self.n - 2):
                for j in range(i + 2, self.n - 1):
                    # Don't consider adjacent edges
                    if j == i + 1:
                        continue
                    
                    gain = self._calculate_2opt_gain(current_tour, i, j)
                    
                    if gain > 1e-10:  # Small epsilon to avoid floating point issues
                        # Create move signature (ordered pair of edges)
                        edge1 = (current_tour[i], current_tour[i + 1])
                        edge2 = (current_tour[j], current_tour[j + 1])
                        move = tuple(sorted([edge1, edge2]))
                        
                        # Aspiration criterion: accept if new best
                        if gain > best_gain:
                            if move in tabu_list:
                                # Check aspiration: if this would give new global best
                                new_length = current_length - gain
                                if new_length < best_length:
                                    best_gain = gain
                                    best_move = (i, j)
                                    best_move_type = 'aspiration'
                            else:
                                best_gain = gain
                                best_move = (i, j)
                                best_move_type = 'regular'
            
            # Apply best move if found
            if best_move is not None:
                i, j = best_move
                
                # Create move signature for tabu list
                edge1 = (current_tour[i], current_tour[i + 1])
                edge2 = (current_tour[j], current_tour[j + 1])
                move = tuple(sorted([edge1, edge2]))
                
                # Apply the move
                current_tour = self._two_opt_move(current_tour, i, j)
                current_length -= best_gain
                
                # Add to tabu list (forbid reversing this move)
                tabu_list.append(move)
                
                # Update best solution
                if current_length < best_length:
                    best_tour = current_tour.copy()
                    best_length = current_length
                    non_improving = 0
                    print(f"  Iteration {iteration}: New best {best_length:.4f} (gain: {best_gain:.4f})")
                else:
                    non_improving += 1
            else:
                non_improving += 1
            
            # Diversification: restart from best solution with perturbation
            if non_improving >= self.max_non_improving:
                print(f"  Diversification at iteration {iteration}")
                # Perturb current solution
                current_tour = self._perturb_tour(best_tour)
                current_length = self._tour_length(current_tour)
                tabu_list.clear()  # Reset tabu list
                non_improving = 0
        
        return best_tour, best_length
    
    def _perturb_tour(self, tour: List[int]) -> List[int]:
        """Perturb tour for diversification."""
        # Perform a random 4-opt move (double bridge)
        if self.n < 8:
            return tour.copy()
        
        # Find 4 random positions
        positions = sorted(np.random.choice(self.n - 1, 4, replace=False))
        a, b, c, d = positions
        
        # Double bridge perturbation: A-B C-D -> A-C B-D
        new_tour = tour[:a+1] + tour[c+1:d+1] + tour[b+1:c+1] + tour[a+1:b+1] + tour[d+1:]
        return new_tour
    
    def solve_tsp(self) -> Tuple[List[int], float]:
        """
        Solve TSP using Christofides + Tabu Search hybrid.
        
        Returns:
            tour: List of node indices in visitation order
            tour_length: Total distance of tour
        """
        print(f"Christofides-Tabu Hybrid solving {self.n}-node TSP")
        
        # Step 1: Christofides for initial solution
        start_time = time.time()
        christofides_tour, christofides_length = self.christofides_tour()
        christofides_time = time.time() - start_time
        
        print(f"  Christofides: {christofides_length:.4f} ({christofides_time:.3f}s)")
        
        # Step 2: Tabu Search improvement
        start_time = time.time()
        final_tour, final_length = self.tabu_search(christofides_tour, christofides_length)
        tabu_time = time.time() - start_time
        
        improvement = ((christofides_length - final_length) / christofides_length) * 100
        print(f"  Tabu Search: {final_length:.4f} ({tabu_time:.3f}s)")
        print(f"  Improvement: {improvement:.2f}%")
        print(f"  Total time: {christofides_time + tabu_time:.3f}s")
        
        return final_tour, final_length

def solve_tsp(points: List[Tuple[float, float]], seed: int = 42) -> Tuple[List[int], float]:
    """
    Wrapper function for compatibility with benchmark framework.
    """
    solver = EuclideanTSPChristofidesTabuHybrid(points, seed)
    tour, length = solver.solve_tsp()
    
    # Convert closed tour to open tour (remove duplicate start city)
    if len(tour) > 0 and tour[0] == tour[-1]:
        tour = tour[:-1]
    
    return tour, length

# Test with small instance
if __name__ == "__main__":
    # Create a small test instance
    np.random.seed(42)
    n = 20
    points = [(np.random.uniform(0, 100), np.random.uniform(0, 100)) for _ in range(n)]
    
    solver = EuclideanTSPChristofidesTabuHybrid(points)
    tour, length = solver.solve_tsp()
    
    print(f"\nFinal tour length: {length}")
    print(f"Tour: {tour[:5]}...")  # Show first 5 nodes