"""
Modified version of tsp_v19_christofides_hybrid_structural_fixed.py
with configurable max_iterations for 2-opt.
"""
import numpy as np
import random
from typing import List, Tuple, Optional, Union, Set
import math

class ChristofidesHybridStructuralModified:
    """Christofides hybrid with structural improvements (modified for TSPLIB)."""
    
    def __init__(self, points: Optional[List[Tuple[float, float]]] = None,
                 distance_matrix: Optional[Union[List[List[float]], np.ndarray]] = None,
                 seed: Optional[int] = None,
                 max_iterations: int = 100):  # Reduced from 1000
        """
        Initialize solver.
        
        Args:
            points: List of (x, y) coordinate tuples
            distance_matrix: Precomputed distance matrix (list of lists or numpy array)
            seed: Random seed for reproducibility
            max_iterations: Maximum iterations for 2-opt (reduced for large instances)
        """
        if points is None and distance_matrix is None:
            raise ValueError("Must provide either points or distance_matrix")
        
        self.points = points
        self.distance_matrix = distance_matrix
        self.seed = seed
        self.max_iterations = max_iterations
        
        if seed is not None:
            random.seed(seed)
    
    def _compute_distance(self, i: int, j: int) -> float:
        """Compute distance between nodes i and j."""
        if self.distance_matrix is not None:
            return self.distance_matrix[i][j]
        else:
            x1, y1 = self.points[i]
            x2, y2 = self.points[j]
            return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    
    def _compute_tour_length(self, tour: List[int]) -> float:
        """Compute total length of a tour."""
        total = 0.0
        for i in range(len(tour) - 1):
            total += self._compute_distance(tour[i], tour[i + 1])
        return total
    
    def _nearest_neighbor(self, start: int) -> List[int]:
        """Nearest neighbor heuristic from given start node."""
        n = len(self.points) if self.points is not None else len(self.distance_matrix)
        unvisited = set(range(n))
        unvisited.remove(start)
        tour = [start]
        current = start
        
        while unvisited:
            # Find nearest unvisited node
            nearest = min(unvisited, key=lambda node: self._compute_distance(current, node))
            tour.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        # Return to start
        tour.append(start)
        return tour
    
    def _mst_prim(self) -> List[Set[int]]:
        """Prim's algorithm for Minimum Spanning Tree."""
        n = len(self.points) if self.points is not None else len(self.distance_matrix)
        visited = [False] * n
        mst = [set() for _ in range(n)]
        
        # Start from node 0
        visited[0] = True
        
        for _ in range(n - 1):
            min_dist = float('inf')
            u, v = -1, -1
            
            for i in range(n):
                if visited[i]:
                    for j in range(n):
                        if not visited[j]:
                            dist = self._compute_distance(i, j)
                            if dist < min_dist:
                                min_dist = dist
                                u, v = i, j
            
            if u != -1 and v != -1:
                visited[v] = True
                mst[u].add(v)
                mst[v].add(u)
        
        return mst
    
    def _find_odd_degree_vertices(self, mst: List[Set[int]]) -> List[int]:
        """Find vertices with odd degree in MST."""
        odd_vertices = []
        for i, neighbors in enumerate(mst):
            if len(neighbors) % 2 == 1:
                odd_vertices.append(i)
        return odd_vertices
    
    def _minimum_weight_perfect_matching(self, odd_vertices: List[int]) -> List[Tuple[int, int]]:
        """Greedy minimum weight perfect matching for odd-degree vertices."""
        vertices = odd_vertices.copy()
        random.shuffle(vertices)
        matching = []
        
        while vertices:
            u = vertices.pop()
            # Find closest unmatched vertex
            min_dist = float('inf')
            v_idx = -1
            
            for idx, candidate in enumerate(vertices):
                dist = self._compute_distance(u, candidate)
                if dist < min_dist:
                    min_dist = dist
                    v_idx = idx
            
            if v_idx != -1:
                v = vertices.pop(v_idx)
                matching.append((u, v))
        
        return matching
    
    def _eulerian_circuit(self, multigraph: List[Set[int]], start: int) -> List[int]:
        """Hierholzer's algorithm for Eulerian circuit."""
        circuit = []
        stack = [start]
        
        while stack:
            v = stack[-1]
            if multigraph[v]:
                u = multigraph[v].pop()
                multigraph[u].remove(v)
                stack.append(u)
            else:
                circuit.append(stack.pop())
        
        return circuit[::-1]
    
    def _hamiltonian_cycle(self, eulerian: List[int]) -> List[int]:
        """Convert Eulerian circuit to Hamiltonian cycle (skip visited nodes)."""
        visited = set()
        hamiltonian = []
        
        for node in eulerian:
            if node not in visited:
                visited.add(node)
                hamiltonian.append(node)
        
        # Return to start
        hamiltonian.append(hamiltonian[0])
        return hamiltonian
    
    def _two_opt(self, tour: List[int]) -> Tuple[List[int], float]:
        """Apply 2-opt local optimization with configurable max_iterations."""
        n = len(tour) - 1  # Exclude closing vertex
        best_tour = tour.copy()
        best_length = self._compute_tour_length(best_tour)
        
        improved = True
        iterations = 0
        
        while improved and iterations < self.max_iterations:
            improved = False
            iterations += 1
            
            for i in range(1, n - 1):
                for j in range(i + 1, n):
                    if j - i == 1:
                        continue  # No gain
                    
                    # Try 2-opt swap
                    new_tour = best_tour[:i] + best_tour[i:j+1][::-1] + best_tour[j+1:]
                    
                    # Ensure tour is closed
                    if new_tour[-1] != new_tour[0]:
                        new_tour.append(new_tour[0])
                    
                    new_length = self._compute_tour_length(new_tour)
                    
                    if new_length < best_length:
                        best_tour = new_tour
                        best_length = new_length
                        improved = True
                        break
                if improved:
                    break
        
        return best_tour, best_length
    
    def solve(self, points: Optional[List[Tuple[float, float]]] = None,
              distance_matrix: Optional[Union[List[List[float]], np.ndarray]] = None) -> Tuple[List[int], float]:
        """
        Solve TSP using Christofides hybrid with structural improvements.
        
        Returns:
            Tuple of (tour, tour_length)
        """
        if points is not None:
            self.points = points
        if distance_matrix is not None:
            self.distance_matrix = distance_matrix
        
        n = len(self.points) if self.points is not None else len(self.distance_matrix)
        
        # Step 1: Build MST
        mst = self._mst_prim()
        
        # Step 2: Find odd-degree vertices
        odd_vertices = self._find_odd_degree_vertices(mst)
        
        # Step 3: Minimum weight perfect matching
        matching = self._minimum_weight_perfect_matching(odd_vertices)
        
        # Step 4: Create multigraph (MST + matching)
        multigraph = [set() for _ in range(n)]
        for i in range(n):
            multigraph[i] = mst[i].copy()
        
        for u, v in matching:
            multigraph[u].add(v)
            multigraph[v].add(u)
        
        # Step 5: Find Eulerian circuit
        eulerian = self._eulerian_circuit(multigraph, 0)
        
        # Step 6: Convert to Hamiltonian cycle
        tour = self._hamiltonian_cycle(eulerian)
        
        # Step 7: Apply 2-opt optimization
        optimized_tour, tour_length = self._two_opt(tour)
        
        return optimized_tour, tour_length

def solve_tsp(points: np.ndarray, distance_matrix: Optional[np.ndarray] = None,
              seed: Optional[int] = None, max_iterations: int = 100) -> Tuple[List[int], float]:
    """
    Wrapper function for compatibility with evaluation framework.
    
    Args:
        points: Numpy array of shape (n, 2) with coordinates
        distance_matrix: Optional precomputed distance matrix
        seed: Random seed
        max_iterations: Maximum iterations for 2-opt
    
    Returns:
        Tuple of (tour, tour_length)
    """
    # Convert numpy array to list of tuples
    points_list = [(float(p[0]), float(p[1])) for p in points]
    
    solver = ChristofidesHybridStructuralModified(
        points=points_list,
        distance_matrix=distance_matrix,
        seed=seed,
        max_iterations=max_iterations
    )
    
    return solver.solve()
