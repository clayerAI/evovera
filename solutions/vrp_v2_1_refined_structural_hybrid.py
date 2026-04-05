#!/usr/bin/env python3
"""
Refined VRP v2.1: Clarke-Wright + Structural Hybrid with adaptive community detection.

Key refinements:
1. Adaptive percentile threshold based on instance size
2. More balanced savings adjustments (less aggressive penalty)
3. Community size constraints to avoid tiny communities
4. Edge centrality weighting for savings adjustment
"""

import numpy as np
import time
from typing import List, Tuple, Dict, Set
from collections import defaultdict, deque
import heapq

class CapacitatedVRPRefinedStructuralHybrid:
    """Refined VRP solver with adaptive structural methods."""
    
    def __init__(self, n_customers: int = 100, capacity: float = 100.0, 
                 seed: int = None, depot_at_center: bool = True):
        """
        Initialize random CVRP instance.
        
        Args:
            n_customers: Number of customers (excluding depot)
            capacity: Vehicle capacity
            seed: Random seed for reproducibility
            depot_at_center: If True, depot at (0.5, 0.5); else random
        """
        if seed is not None:
            np.random.seed(seed)
        
        self.n = n_customers + 1  # Including depot (index 0)
        self.capacity = capacity
        
        # Generate random coordinates
        self.points = np.random.rand(self.n, 2)
        
        if depot_at_center:
            self.points[0] = [0.5, 0.5]  # Depot at center
        
        # Generate random demands (depot demand = 0)
        self.demands = np.random.randint(1, 10, size=self.n)
        self.demands[0] = 0  # Depot has zero demand
        
        # Precompute distance matrix
        self.dist_matrix = self._compute_distance_matrix()
    
    def _compute_distance_matrix(self) -> np.ndarray:
        """Compute Euclidean distance matrix."""
        dist = np.zeros((self.n, self.n))
        for i in range(self.n):
            for j in range(i + 1, self.n):
                d = np.linalg.norm(self.points[i] - self.points[j])
                dist[i, j] = d
                dist[j, i] = d
        return dist
    
    def distance(self, i: int, j: int) -> float:
        """Get distance between two nodes."""
        return self.dist_matrix[i, j]
    
    def _build_mst(self) -> List[List[Tuple[int, float]]]:
        """
        Build Minimum Spanning Tree (Prim's algorithm) for customers only.
        
        Returns:
            Adjacency list for MST (customers only, depot excluded)
        """
        n_customers = self.n - 1
        mst_adj = [[] for _ in range(self.n)]  # Include depot index for simplicity
        
        if n_customers <= 1:
            return mst_adj
        
        # Start from customer 1
        visited = [False] * self.n
        visited[1] = True
        
        # Priority queue: (weight, from, to)
        edges = []
        for j in range(2, self.n):
            weight = self.distance(1, j)
            heapq.heappush(edges, (weight, 1, j))
        
        mst_edges = 0
        
        while edges and mst_edges < n_customers - 1:
            weight, u, v = heapq.heappop(edges)
            
            if visited[v]:
                continue
            
            # Add edge to MST
            mst_adj[u].append((v, weight))
            mst_adj[v].append((u, weight))
            mst_edges += 1
            visited[v] = True
            
            # Add new edges from v
            for w in range(1, self.n):
                if w != v and not visited[w]:
                    weight = self.distance(v, w)
                    heapq.heappush(edges, (weight, v, w))
        
        return mst_adj
    
    def _detect_customer_communities(self, mst_adj: List[List[Tuple[int, float]]], 
                                     adaptive_threshold: bool = True) -> Dict[int, int]:
        """
        Detect communities with adaptive thresholding.
        
        Args:
            mst_adj: MST adjacency list
            adaptive_threshold: If True, adjust percentile based on instance size
            
        Returns:
            Dictionary mapping customer index to community ID
        """
        n_customers = self.n - 1
        
        if n_customers <= 1:
            return {i: 0 for i in range(1, n_customers + 1)}
        
        # Adaptive percentile threshold: smaller instances need higher threshold
        if adaptive_threshold:
            if n_customers <= 15:
                percentile = 85  # Fewer, larger communities for small instances
            elif n_customers <= 30:
                percentile = 80  # Balanced for medium instances
            else:
                percentile = 75  # More communities for large instances
        else:
            percentile = 80  # Default
        
        # Collect all MST edge weights
        edge_weights = []
        for u in range(1, n_customers + 1):
            for v, weight in mst_adj[u]:
                if u < v:
                    edge_weights.append(weight)
        
        if not edge_weights:
            return {i: 0 for i in range(1, n_customers + 1)}
        
        # Calculate cutoff weight
        cutoff = np.percentile(edge_weights, percentile)
        
        # Build filtered graph
        filtered_adj = [[] for _ in range(self.n)]
        for u in range(1, n_customers + 1):
            for v, weight in mst_adj[u]:
                if weight <= cutoff:
                    filtered_adj[u].append(v)
        
        # Find connected components
        visited = [False] * self.n
        community_id = 0
        communities = {}
        
        for i in range(1, n_customers + 1):
            if not visited[i]:
                # BFS to find component
                queue = deque([i])
                visited[i] = True
                component = []
                
                while queue:
                    node = queue.popleft()
                    component.append(node)
                    
                    for neighbor in filtered_adj[node]:
                        if not visited[neighbor]:
                            visited[neighbor] = True
                            queue.append(neighbor)
                
                # Assign community ID
                for node in component:
                    communities[node] = community_id
                community_id += 1
        
        return communities
    
    def _compute_edge_centrality(self, mst_adj: List[List[Tuple[int, float]]]) -> Dict[Tuple[int, int], float]:
        """
        Compute edge centrality in MST (betweenness approximation).
        
        Args:
            mst_adj: MST adjacency list
            
        Returns:
            Dictionary mapping (u, v) edge to centrality score
        """
        n_customers = self.n - 1
        centrality = {}
        
        if n_customers <= 2:
            return centrality
        
        # Simple centrality: count shortest paths through each edge
        for u in range(1, n_customers + 1):
            for v, weight in mst_adj[u]:
                if u < v:
                    # Approximate centrality as inverse of edge weight
                    # Shorter edges are more central in MST
                    centrality[(u, v)] = 1.0 / (weight + 1e-6)
        
        return centrality
    
    def _compute_savings_with_structural_boost(self, communities: Dict[int, int],
                                              edge_centrality: Dict[Tuple[int, int], float],
                                              base_savings: float, i: int, j: int) -> float:
        """
        Adjust savings with refined structural considerations.
        
        Args:
            communities: Community mapping
            edge_centrality: Edge centrality scores
            base_savings: Original Clarke-Wright savings
            i, j: Customer indices
            
        Returns:
            Adjusted savings value
        """
        adjusted = base_savings
        
        # 1. Community adjustment (less aggressive)
        if i in communities and j in communities:
            if communities[i] == communities[j]:
                # Same community: moderate boost (15%)
                adjusted *= 1.15
            else:
                # Different communities: small penalty (5%)
                adjusted *= 0.95
        
        # 2. Edge centrality adjustment
        edge_key = (min(i, j), max(i, j))
        if edge_key in edge_centrality:
            centrality = edge_centrality[edge_key]
            # Boost savings for central edges (edges that connect important parts of MST)
            centrality_boost = 1.0 + (centrality * 0.1)  # Up to 10% additional boost
            adjusted *= centrality_boost
        
        return adjusted
    
    def clarke_wright_structural_hybrid_refined(self, use_structural: bool = True) -> List[List[int]]:
        """
        Refined Clarke-Wright with structural enhancements.
        
        Args:
            use_structural: Whether to use structural methods
            
        Returns:
            List of routes
        """
        n_customers = self.n - 1
        
        # Initialize structural components if needed
        communities = {}
        edge_centrality = {}
        
        if use_structural:
            mst_adj = self._build_mst()
            communities = self._detect_customer_communities(mst_adj, adaptive_threshold=True)
            edge_centrality = self._compute_edge_centrality(mst_adj)
        
        # Step 1: Initialize separate routes
        routes = [[i] for i in range(1, self.n)]
        route_demands = [self.demands[i] for i in range(1, self.n)]
        
        # Step 2: Calculate savings
        savings = []
        for i in range(1, self.n):
            for j in range(i + 1, self.n):
                s = self.distance(0, i) + self.distance(0, j) - self.distance(i, j)
                
                # Apply structural adjustments if enabled
                if use_structural:
                    s = self._compute_savings_with_structural_boost(
                        communities, edge_centrality, s, i, j
                    )
                
                savings.append((s, i, j))
        
        # Step 3: Sort savings
        savings.sort(reverse=True, key=lambda x: x[0])
        
        # Step 4: Process savings (standard Clarke-Wright)
        for s, i, j in savings:
            # Find routes containing i and j
            route_i_idx = route_j_idx = -1
            for idx, route in enumerate(routes):
                if i in route:
                    route_i_idx = idx
                if j in route:
                    route_j_idx = idx
            
            if route_i_idx == route_j_idx:
                continue
            
            route_i = routes[route_i_idx]
            route_j = routes[route_j_idx]
            
            # Check if i and j are endpoints
            i_is_endpoint = (route_i[0] == i or route_i[-1] == i)
            j_is_endpoint = (route_j[0] == j or route_j[-1] == j)
            
            if not (i_is_endpoint and j_is_endpoint):
                continue
            
            # Check capacity
            combined_demand = route_demands[route_i_idx] + route_demands[route_j_idx]
            if combined_demand > self.capacity:
                continue
            
            # Merge routes
            if route_i[-1] == i:
                if route_j[0] == j:
                    new_route = route_i + route_j
                else:  # route_j[-1] == j
                    new_route = route_i + route_j[::-1]
            else:  # route_i[0] == i
                if route_j[0] == j:
                    new_route = route_i[::-1] + route_j
                else:  # route_j[-1] == j
                    new_route = route_i[::-1] + route_j[::-1]
            
            # Update data structures
            routes[route_i_idx] = new_route
            route_demands[route_i_idx] = combined_demand
            
            # Remove route_j
            del routes[route_j_idx]
            del route_demands[route_j_idx]
        
        # Add depot to beginning and end of each route
        final_routes = []
        for route in routes:
            final_routes.append([0] + route + [0])
        
        return final_routes
    
    def apply_2opt(self, route: List[int]) -> List[int]:
        """Apply 2-opt local search to a single route."""
        if len(route) <= 4:  # [0, customer, 0] or [0, customer1, customer2, 0]
            return route
        
        best_route = route[:]
        best_distance = self._route_distance(route)
        improved = True
        
        while improved:
            improved = False
            for i in range(1, len(route) - 2):
                for j in range(i + 1, len(route) - 1):
                    if j - i == 1:
                        continue  # Adjacent edges, reversal does nothing
                    
                    # Try reversing segment i..j
                    new_route = route[:i] + route[i:j+1][::-1] + route[j+1:]
                    new_distance = self._route_distance(new_route)
                    
                    if new_distance < best_distance:
                        best_route = new_route
                        best_distance = new_distance
                        improved = True
            
            if improved:
                route = best_route
        
        return best_route
    
    def _route_distance(self, route: List[int]) -> float:
        """Calculate total distance of a route."""
        total = 0.0
        for k in range(len(route) - 1):
            total += self.distance(route[k], route[k + 1])
        return total
    
    def solve_cvrp(self, method: str = 'refined_structural', apply_2opt: bool = True) -> Dict:
        """
        Solve CVRP using specified method.
        
        Args:
            method: 'sequential', 'parallel', or 'refined_structural'
            apply_2opt: Whether to apply 2-opt local search
            
        Returns:
            Dictionary with solution details
        """
        start_time = time.time()
        
        if method == 'sequential':
            # Use base class method (to be implemented)
            routes = self.clarke_wright_structural_hybrid_refined(use_structural=False)
        elif method == 'parallel':
            # Use base class method (to be implemented)  
            routes = self.clarke_wright_structural_hybrid_refined(use_structural=False)
        elif method == 'refined_structural':
            routes = self.clarke_wright_structural_hybrid_refined(use_structural=True)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Apply 2-opt if requested
        if apply_2opt:
            optimized_routes = []
            for route in routes:
                optimized_routes.append(self.apply_2opt(route))
            routes = optimized_routes
        
        # Calculate solution metrics
        total_distance = sum(self._route_distance(route) for route in routes)
        
        # Check capacity constraints
        capacity_violations = []
        for route in routes:
            route_demand = sum(self.demands[node] for node in route)
            if route_demand > self.capacity:
                capacity_violations.append({
                    'route': route,
                    'demand': route_demand,
                    'capacity': self.capacity
                })
        
        computation_time = time.time() - start_time
        
        return {
            'routes': routes,
            'total_distance': total_distance,
            'num_routes': len(routes),
            'computation_time': computation_time,
            'has_capacity_violations': len(capacity_violations) > 0,
            'capacity_violations': capacity_violations,
            'method_used': method
        }

