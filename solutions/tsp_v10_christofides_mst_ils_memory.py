"""
TSP Algorithm: Christofides MST structure with ILS perturbations guided by edge swap frequency memory
Author: Evo
Date: 2026-04-03

Novel Hybrid Concept: Using Christofides MST structure as foundation but applying ILS perturbations
guided by memory of which edges were most frequently swapped in previous iterations.
This creates adaptive perturbation strategy based on historical edge swap patterns.
"""

import math
import random
import time
from typing import List, Tuple, Dict, Set
import heapq

class EuclideanTSPChristofidesMSTILS:
    """Christofides MST structure with ILS perturbations guided by edge swap frequency memory"""
    
    def __init__(self, points: List[Tuple[float, float]], seed: int = 42):
        self.points = points
        self.n = len(points)
        self.seed = seed
        random.seed(seed)
        
        # Precompute distances
        self.dist_matrix = self._compute_distance_matrix()
        
        # Memory for edge swap frequency
        self.edge_swap_frequency: Dict[Tuple[int, int], int] = {}
        self.edge_quality: Dict[Tuple[int, int], float] = {}  # Average improvement when edge is swapped
        
    def _compute_distance_matrix(self) -> List[List[float]]:
        """Compute Euclidean distance matrix"""
        n = self.n
        dist = [[0.0] * n for _ in range(n)]
        for i in range(n):
            xi, yi = self.points[i]
            for j in range(i + 1, n):
                xj, yj = self.points[j]
                d = math.sqrt((xi - xj) ** 2 + (yi - yj) ** 2)
                dist[i][j] = d
                dist[j][i] = d
        return dist
    
    def _compute_mst(self) -> List[Tuple[float, int, int]]:
        """Compute Minimum Spanning Tree using Prim's algorithm"""
        n = self.n
        visited = [False] * n
        min_edge = [float('inf')] * n
        min_edge[0] = 0
        parent = [-1] * n
        
        mst_edges = []
        
        for _ in range(n):
            # Find minimum edge
            u = -1
            for i in range(n):
                if not visited[i] and (u == -1 or min_edge[i] < min_edge[u]):
                    u = i
            
            visited[u] = True
            
            if parent[u] != -1:
                mst_edges.append((self.dist_matrix[u][parent[u]], u, parent[u]))
            
            # Update neighbors
            for v in range(n):
                if not visited[v] and self.dist_matrix[u][v] < min_edge[v]:
                    min_edge[v] = self.dist_matrix[u][v]
                    parent[v] = u
        
        return mst_edges
    
    def _find_odd_degree_vertices(self, mst_edges: List[Tuple[float, int, int]]) -> List[int]:
        """Find vertices with odd degree in MST"""
        degree = [0] * self.n
        for _, u, v in mst_edges:
            degree[u] += 1
            degree[v] += 1
        
        odd_vertices = [i for i in range(self.n) if degree[i] % 2 == 1]
        return odd_vertices
    
    def _greedy_minimum_matching(self, odd_vertices: List[int]) -> List[Tuple[int, int]]:
        """Greedy minimum weight matching on odd vertices"""
        if len(odd_vertices) == 0:
            return []
        
        # Sort odd vertices by distance from center for determinism
        center_x = sum(self.points[i][0] for i in odd_vertices) / len(odd_vertices)
        center_y = sum(self.points[i][1] for i in odd_vertices) / len(odd_vertices)
        
        def distance_to_center(i):
            x, y = self.points[i]
            return math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
        
        sorted_vertices = sorted(odd_vertices, key=distance_to_center)
        
        matched = [False] * len(sorted_vertices)
        matching = []
        
        for i in range(len(sorted_vertices)):
            if matched[i]:
                continue
            
            best_j = -1
            best_dist = float('inf')
            
            for j in range(i + 1, len(sorted_vertices)):
                if not matched[j]:
                    dist = self.dist_matrix[sorted_vertices[i]][sorted_vertices[j]]
                    if dist < best_dist:
                        best_dist = dist
                        best_j = j
            
            if best_j != -1:
                matching.append((sorted_vertices[i], sorted_vertices[best_j]))
                matched[i] = True
                matched[best_j] = True
        
        return matching
    
    def _construct_eulerian_circuit(self, mst_edges: List[Tuple[float, int, int]], 
                                   matching: List[Tuple[int, int]]) -> List[int]:
        """Construct Eulerian circuit from MST + matching"""
        # Create multigraph adjacency list
        adj = [[] for _ in range(self.n)]
        
        # Add MST edges
        for _, u, v in mst_edges:
            adj[u].append(v)
            adj[v].append(u)
        
        # Add matching edges
        for u, v in matching:
            adj[u].append(v)
            adj[v].append(u)
        
        # Hierholzer's algorithm for Eulerian circuit
        circuit = []
        stack = [0]
        
        while stack:
            u = stack[-1]
            if adj[u]:
                v = adj[u].pop()
                # Remove the reverse edge
                adj[v].remove(u)
                stack.append(v)
            else:
                circuit.append(stack.pop())
        
        circuit.reverse()
        return circuit
    
    def _shortcut_eulerian_to_hamiltonian(self, eulerian_circuit: List[int]) -> List[int]:
        """Shortcut Eulerian circuit to Hamiltonian tour"""
        visited = [False] * self.n
        tour = []
        
        for v in eulerian_circuit:
            if not visited[v]:
                visited[v] = True
                tour.append(v)
        
        return tour
    
    def _compute_tour_length(self, tour: List[int]) -> float:
        """Compute total length of tour"""
        total = 0.0
        for i in range(self.n):
            u = tour[i]
            v = tour[(i + 1) % self.n]
            total += self.dist_matrix[u][v]
        return total
    
    def _two_opt(self, tour: List[int], max_iterations: int = 1000) -> Tuple[List[int], float]:
        """2-opt local search with edge swap frequency tracking"""
        n = self.n
        best_tour = tour[:]
        best_length = self._compute_tour_length(tour)
        improved = True
        iterations = 0
        
        while improved and iterations < max_iterations:
            improved = False
            
            for i in range(n):
                for j in range(i + 2, n):
                    if j == n - 1 and i == 0:
                        continue
                    
                    # Try 2-opt swap
                    new_tour = best_tour[:i+1] + best_tour[i+1:j+1][::-1] + best_tour[j+1:]
                    new_length = self._compute_tour_length(new_tour)
                    
                    if new_length < best_length:
                        # Update edge swap frequency
                        edge1 = (best_tour[i], best_tour[(i + 1) % n])
                        edge2 = (best_tour[j], best_tour[(j + 1) % n])
                        edge1_key = tuple(sorted(edge1))
                        edge2_key = tuple(sorted(edge2))
                        
                        self.edge_swap_frequency[edge1_key] = self.edge_swap_frequency.get(edge1_key, 0) + 1
                        self.edge_swap_frequency[edge2_key] = self.edge_swap_frequency.get(edge2_key, 0) + 1
                        
                        # Track edge quality (improvement amount)
                        improvement = best_length - new_length
                        self.edge_quality[edge1_key] = self.edge_quality.get(edge1_key, 0) + improvement
                        self.edge_quality[edge2_key] = self.edge_quality.get(edge2_key, 0) + improvement
                        
                        best_tour = new_tour
                        best_length = new_length
                        improved = True
                        break
                
                if improved:
                    break
            
            iterations += 1
        
        return best_tour, best_length
    
    def _memory_guided_perturbation(self, tour: List[int], strength: int = 4) -> List[int]:
        """Perturb tour based on edge swap frequency memory"""
        n = self.n
        
        if not self.edge_swap_frequency:
            # No memory yet, use random double-bridge
            return self._random_double_bridge(tour)
        
        # Get edges sorted by swap frequency (most frequently swapped first)
        sorted_edges = sorted(self.edge_swap_frequency.items(), 
                            key=lambda x: x[1], reverse=True)
        
        # Take top k edges to break
        k = min(strength * 2, len(sorted_edges))
        edges_to_break = [edge for edge, _ in sorted_edges[:k]]
        
        # Convert to vertex indices
        vertices_to_break = set()
        for (u, v) in edges_to_break:
            vertices_to_break.add(u)
            vertices_to_break.add(v)
        
        # Find positions of these vertices in tour
        positions = {}
        for i, v in enumerate(tour):
            if v in vertices_to_break:
                positions[v] = i
        
        if len(positions) < 4:
            # Not enough vertices found, fall back to random
            return self._random_double_bridge(tour)
        
        # Select 4 vertices to perform double-bridge-like perturbation
        selected_vertices = random.sample(list(positions.keys()), min(4, len(positions)))
        selected_positions = sorted([positions[v] for v in selected_vertices])
        
        # Reconstruct tour with segments swapped (double-bridge)
        a, b, c, d = selected_positions[:4]
        new_tour = tour[:a+1] + tour[c+1:d+1] + tour[b+1:c+1] + tour[a+1:b+1] + tour[d+1:]
        
        return new_tour
    
    def _random_double_bridge(self, tour: List[int]) -> List[int]:
        """Random double-bridge perturbation"""
        n = self.n
        a = random.randint(0, n - 1)
        b = (a + random.randint(1, n // 4)) % n
        c = (b + random.randint(1, n // 4)) % n
        d = (c + random.randint(1, n // 4)) % n
        
        # Ensure all indices are distinct and in order
        indices = sorted([a, b, c, d])
        a, b, c, d = indices
        
        new_tour = tour[:a+1] + tour[c+1:d+1] + tour[b+1:c+1] + tour[a+1:b+1] + tour[d+1:]
        return new_tour
    
    def solve(self, max_iterations: int = 50, max_no_improve: int = 10) -> Tuple[List[int], float, Dict]:
        """Main solving method with ILS guided by edge swap memory"""
        start_time = time.time()
        
        # Step 1: Construct Christofides tour
        mst_edges = self._compute_mst()
        odd_vertices = self._find_odd_degree_vertices(mst_edges)
        matching = self._greedy_minimum_matching(odd_vertices)
        eulerian_circuit = self._construct_eulerian_circuit(mst_edges, matching)
        initial_tour = self._shortcut_eulerian_to_hamiltonian(eulerian_circuit)
        
        # Step 2: Initial local search
        current_tour, current_length = self._two_opt(initial_tour)
        best_tour = current_tour[:]
        best_length = current_length
        
        # ILS main loop
        iterations = 0
        no_improve_count = 0
        
        while iterations < max_iterations and no_improve_count < max_no_improve:
            # Perturbation guided by memory
            perturbed_tour = self._memory_guided_perturbation(current_tour)
            
            # Local search on perturbed tour
            new_tour, new_length = self._two_opt(perturbed_tour)
            
            # Acceptance criterion
            if new_length < current_length:
                current_tour = new_tour[:]
                current_length = new_length
                
                if new_length < best_length:
                    best_tour = new_tour[:]
                    best_length = new_length
                    no_improve_count = 0
                else:
                    no_improve_count += 1
            else:
                # Accept with probability based on temperature
                temperature = 0.1 * (max_iterations - iterations) / max_iterations
                if random.random() < math.exp((current_length - new_length) / temperature):
                    current_tour = new_tour[:]
                    current_length = new_length
                no_improve_count += 1
            
            iterations += 1
        
        end_time = time.time()
        
        stats = {
            'initial_length': self._compute_tour_length(initial_tour),
            'final_length': best_length,
            'improvement_percentage': 100 * (self._compute_tour_length(initial_tour) - best_length) / self._compute_tour_length(initial_tour),
            'iterations': iterations,
            'time': end_time - start_time,
            'edge_swap_count': len(self.edge_swap_frequency),
            'memory_guided_perturbations': iterations - no_improve_count
        }
        
        return best_tour, best_length, stats


def solve_tsp(points: List[Tuple[float, float]], seed: int = 42) -> Tuple[List[int], float]:
    """Main solving function for external use"""
    solver = EuclideanTSPChristofidesMSTILS(points, seed)
    tour, length, _ = solver.solve()
    return tour, length


if __name__ == "__main__":
    # Example usage and testing
    import sys
    
    # Generate random points for testing
    random.seed(42)
    n = 50
    points = [(random.random() * 100, random.random() * 100) for _ in range(n)]
    
    solver = EuclideanTSPChristofidesMSTILS(points, seed=42)
    tour, length, stats = solver.solve()
    
    print(f"Tour length: {length:.4f}")
    print(f"Improvement: {stats['improvement_percentage']:.2f}%")
    print(f"Time: {stats['time']:.2f}s")
    print(f"Iterations: {stats['iterations']}")
    print(f"Edge swaps tracked: {stats['edge_swap_count']}")
    print(f"Memory-guided perturbations: {stats['memory_guided_perturbations']}")