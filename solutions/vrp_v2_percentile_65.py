#!/usr/bin/env python3
"""
Vehicle Routing Problem (VRP) Solver - Version 2: Clarke-Wright + Structural Hybrid Algorithm
Evo - Algorithmic Solver
Novel hybrid: Clarke-Wright savings enhanced with TSP structural methods (community detection, edge centrality, path-based optimization) adapted for VRP capacity constraints.

Implements the classic Clarke-Wright (1964) savings algorithm for the
Capacitated Vehicle Routing Problem (CVRP) with single depot.
"""

import numpy as np
import math
import random
import time
from typing import List, Tuple, Dict, Set, Optional
import json
import heapq


class CapacitatedVRPStructuralHybrid:
    """Capacitated Vehicle Routing Problem with single depot"""
    
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
        self.n_customers = n_customers
        self.n = n_customers + 1  # Including depot (index 0)
        self.capacity = capacity
        self.seed = seed
        
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
        
        # Generate random points in unit square [0,1] x [0,1]
        # Depot is point 0, customers are points 1..n_customers
        self.points = np.random.rand(self.n, 2)
        
        if depot_at_center:
            self.points[0] = np.array([0.5, 0.5])
        
        # Generate random demands for customers (depot demand = 0)
        self.demands = np.zeros(self.n)
        # Customer demands between 1 and capacity/4 (reasonable for routing)
        self.demands[1:] = np.random.randint(1, int(capacity / 4) + 1, size=n_customers)
        
        # Precompute distance matrix
        self.dist_matrix = self._compute_distance_matrix()
    
    

    def _build_mst(self) -> List[List[Tuple[int, float]]]:
        """
        Build Minimum Spanning Tree (MST) of customer locations (excluding depot).
        Uses Prim's algorithm.
        
        Returns:
            MST adjacency list
        """
        import heapq
        from typing import Tuple, List
        
        n_customers = self.n - 1  # Exclude depot
        mst_adj = [[] for _ in range(n_customers + 1)]  # Index 0 is unused, customers start at 1
        
        if n_customers <= 1:
            return mst_adj
        
        # Build complete graph distances between customers
        # Note: We use customer indices 1..n, not including depot
        visited = [False] * (n_customers + 1)
        min_edge = [(float('inf'), -1, -1)] * (n_customers + 1)
        
        # Start from customer 1
        min_edge[1] = (0, -1, -1)
        mst_edges = []
        
        for _ in range(n_customers):
            # Find minimum edge to unvisited vertex
            v = -1
            for i in range(1, n_customers + 1):
                if not visited[i] and (v == -1 or min_edge[i][0] < min_edge[v][0]):
                    v = i
            
            if v == -1:
                break
                
            visited[v] = True
            
            # Add edge to MST if not the first vertex
            if min_edge[v][1] != -1:
                u = min_edge[v][1]
                weight = min_edge[v][0]
                mst_adj[u].append((v, weight))
                mst_adj[v].append((u, weight))
                mst_edges.append((u, v, weight))
            
            # Update min_edge for neighbors
            for to in range(1, n_customers + 1):
                if not visited[to]:
                    # Distance between customers v and to
                    dist = self.distance(v, to)
                    if dist < min_edge[to][0]:
                        min_edge[to] = (dist, v, to)
        
        return mst_adj
    
    def _detect_customer_communities(self, mst_adj: List[List[Tuple[int, float]]], 
                                     percentile_threshold: float = 65) -> Dict[int, int]:
        """
        Detect communities among customers using MST analysis.
        
        Removes heavy MST edges above percentile threshold, then finds connected components.
        Customers in same community are likely to be served in same route.
        
        Args:
            mst_adj: MST adjacency list (customers only, depot excluded)
            percentile_threshold: Percentile for edge weight cutoff (0-100)
            
        Returns:
            Dictionary mapping customer index to community ID
        """
        import numpy as np
        from typing import Dict, Tuple, List
        
        n_customers = self.n - 1
        
        if n_customers <= 1:
            return {i: 0 for i in range(1, n_customers + 1)}
        
        # Collect all MST edge weights
        edge_weights = []
        for u in range(1, n_customers + 1):
            for v, weight in mst_adj[u]:
                if u < v:  # Count each edge once
                    edge_weights.append(weight)
        
        if not edge_weights:
            # All customers in same community
            return {i: 0 for i in range(1, n_customers + 1)}
        
        # Calculate cutoff weight at given percentile
        cutoff = np.percentile(edge_weights, percentile_threshold)
        
        # Build graph without edges above cutoff
        filtered_adj = [[] for _ in range(n_customers + 1)]
        for u in range(1, n_customers + 1):
            for v, weight in mst_adj[u]:
                if weight <= cutoff:
                    filtered_adj[u].append(v)
        
        # Find connected components (communities)
        visited = [False] * (n_customers + 1)
        community_id = 0
        communities = {}
        
        for i in range(1, n_customers + 1):
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
        
        return communities
    
    def _compute_savings_with_community_boost(self, communities: Dict[int, int], 
                                             base_savings: float, i: int, j: int) -> float:
        """
        Adjust savings value based on community membership.
        
        Customers in same community get boosted savings (more likely to be connected).
        Customers in different communities get penalized savings.
        
        Args:
            communities: Community mapping
            base_savings: Original Clarke-Wright savings
            i, j: Customer indices
            
        Returns:
            Adjusted savings value
        """
        if i not in communities or j not in communities:
            return base_savings
        
        if communities[i] == communities[j]:
            # Same community: boost savings by 20%
            return base_savings * 1.2
        else:
            # Different communities: reduce savings by 10%
            return base_savings * 0.9
    
    def clarke_wright_structural_hybrid(self, community_aware: bool = True) -> List[List[int]]:
        """
        Clarke-Wright savings algorithm enhanced with structural methods.
        
        Args:
            community_aware: Whether to use community detection for savings adjustment
            
        Returns:
            List of routes
        """
        # Build MST for community detection if needed
        communities = {}
        if community_aware:
            mst_adj = self._build_mst()
            communities = self._detect_customer_communities(mst_adj)
        
        # Step 1: Initialize n separate routes: 0 -> i -> 0
        routes = [[i] for i in range(1, self.n)]  # Each customer in own route
        route_demands = [self.demands[i] for i in range(1, self.n)]
        
        # Step 2: Calculate savings for all pairs (i, j)
        savings = []
        for i in range(1, self.n):
            for j in range(i + 1, self.n):
                s = self.distance(0, i) + self.distance(0, j) - self.distance(i, j)
                
                # Adjust savings based on community membership if enabled
                if community_aware:
                    s = self._compute_savings_with_community_boost(communities, s, i, j)
                
                savings.append((s, i, j))
        
        # Step 3: Sort savings in descending order
        savings.sort(reverse=True, key=lambda x: x[0])
        
        # Step 4: Process savings in order (same as original)
        for s, i, j in savings:
            # Find routes containing i and j
            route_i_idx = route_j_idx = -1
            for idx, route in enumerate(routes):
                if i in route:
                    route_i_idx = idx
                if j in route:
                    route_j_idx = idx
            
            # Skip if same route
            if route_i_idx == route_j_idx:
                continue
            
            # Check if i and j are endpoints in their routes
            route_i = routes[route_i_idx]
            route_j = routes[route_j_idx]
            
            # Check if i is first or last in route_i
            i_is_endpoint = (route_i[0] == i or route_i[-1] == i)
            # Check if j is first or last in route_j
            j_is_endpoint = (route_j[0] == j or route_j[-1] == j)
            
            if not (i_is_endpoint and j_is_endpoint):
                continue
            
            # Check capacity constraint
            combined_demand = route_demands[route_i_idx] + route_demands[route_j_idx]
            if combined_demand > self.capacity:
                continue
            
            # Merge routes (same as original)
            if route_i[-1] == i:
                if route_j[0] == j:
                    new_route = route_i + route_j
                else:  # route_j[-1] == j
                    new_route = route_i + route_j[::-1]
            else:  # route_i[0] == i
                if route_j[0] == j:
                    new_route = route_j[::-1] + route_i
                else:  # route_j[-1] == j
                    new_route = route_j + route_i
            
            # Update routes and demands
            idx1, idx2 = sorted([route_i_idx, route_j_idx], reverse=True)
            del routes[idx1]
            del routes[idx2]
            del route_demands[idx1]
            del route_demands[idx2]
            
            routes.append(new_route)
            route_demands.append(combined_demand)
        
        return routes
    def _compute_distance_matrix(self) -> np.ndarray:
        """Compute Euclidean distance matrix between all points."""
        dist = np.zeros((self.n, self.n))
        for i in range(self.n):
            for j in range(i + 1, self.n):
                d = math.sqrt(((self.points[i] - self.points[j]) ** 2).sum())
                dist[i, j] = d
                dist[j, i] = d
        return dist
    def distance(self, i: int, j: int) -> float:
        """Get distance between two points."""
        return self.dist_matrix[i, j]
    def total_demand(self, customers: List[int]) -> float:
        """Calculate total demand for a list of customer indices."""
        return sum(self.demands[c] for c in customers)
    def clarke_wright_savings_sequential(self) -> List[List[int]]:
        """
        Clarke-Wright savings algorithm (sequential version).
        
        Returns:
            List of routes, each route as list of customer indices (excluding depot).
            Depot is implied at start and end of each route.
        """
        # Step 1: Initialize n separate routes: 0 -> i -> 0
        routes = [[i] for i in range(1, self.n)]  # Each customer in own route
        route_demands = [self.demands[i] for i in range(1, self.n)]
        
        # Step 2: Calculate savings for all pairs (i, j)
        savings = []
        for i in range(1, self.n):
            for j in range(i + 1, self.n):
                s = self.distance(0, i) + self.distance(0, j) - self.distance(i, j)
                savings.append((s, i, j))
        
        # Step 3: Sort savings in descending order
        savings.sort(reverse=True, key=lambda x: x[0])
        
        # Step 4: Process savings in order
        for s, i, j in savings:
            # Find routes containing i and j
            route_i_idx = route_j_idx = -1
            for idx, route in enumerate(routes):
                if i in route:
                    route_i_idx = idx
                if j in route:
                    route_j_idx = idx
            
            # Skip if same route
            if route_i_idx == route_j_idx:
                continue
            
            # Check if i and j are endpoints in their routes
            route_i = routes[route_i_idx]
            route_j = routes[route_j_idx]
            
            # Check if i is first or last in route_i
            i_is_endpoint = (route_i[0] == i or route_i[-1] == i)
            # Check if j is first or last in route_j
            j_is_endpoint = (route_j[0] == j or route_j[-1] == j)
            
            if not (i_is_endpoint and j_is_endpoint):
                continue
            
            # Check capacity constraint
            combined_demand = route_demands[route_i_idx] + route_demands[route_j_idx]
            if combined_demand > self.capacity:
                continue
            
            # Merge routes
            # Determine orientation for merging
            if route_i[-1] == i:
                # i is at end of route_i
                if route_j[0] == j:
                    # j is at start of route_j: route_i + route_j
                    new_route = route_i + route_j
                else:  # route_j[-1] == j
                    # j is at end of route_j: route_i + route_j reversed
                    new_route = route_i + route_j[::-1]
            else:  # route_i[0] == i
                # i is at start of route_i
                if route_j[0] == j:
                    # j is at start of route_j: route_j reversed + route_i
                    new_route = route_j[::-1] + route_i
                else:  # route_j[-1] == j
                    # j is at end of route_j: route_j + route_i
                    new_route = route_j + route_i
            
            # Update routes and demands
            # Remove old routes (remove larger index first to avoid shifting issues)
            idx1, idx2 = sorted([route_i_idx, route_j_idx], reverse=True)
            # Delete in correct order
            del routes[idx1]
            del routes[idx2]
            del route_demands[idx1]
            del route_demands[idx2]
            
            # Add new route
            routes.append(new_route)
            route_demands.append(combined_demand)
        
        return routes
    
    def clarke_wright_savings_parallel(self) -> List[List[int]]:
        """
        Clarke-Wright savings algorithm (parallel version).
        
        Parallel version considers all possible merges simultaneously,
        typically produces better solutions than sequential version.
        
        Returns:
            List of routes, each route as list of customer indices.
        """
        # Step 1: Initialize n separate routes: 0 -> i -> 0
        routes = [[i] for i in range(1, self.n)]
        route_demands = [self.demands[i] for i in range(1, self.n)]
        
        # Track endpoints of each route
        # Each route is represented as (start, end, route_index_in_list)
        route_endpoints = [(i, i, idx) for idx, i in enumerate(range(1, self.n))]
        
        # Step 2: Calculate and sort savings
        savings = []
        for i in range(1, self.n):
            for j in range(i + 1, self.n):
                s = self.distance(0, i) + self.distance(0, j) - self.distance(i, j)
                savings.append((s, i, j))
        
        savings.sort(reverse=True, key=lambda x: x[0])
        
        # Step 3: Process savings
        for s, i, j in savings:
            # Find routes containing i and j as endpoints
            route_i_info = route_j_info = None
            for start, end, idx in route_endpoints:
                if start == i or end == i:
                    route_i_info = (start, end, idx)
                if start == j or end == j:
                    route_j_info = (start, end, idx)
            
            if not route_i_info or not route_j_info:
                continue
            
            start_i, end_i, idx_i = route_i_info
            start_j, end_j, idx_j = route_j_info
            
            # Skip if same route
            if idx_i == idx_j:
                continue
            
            # Check capacity
            combined_demand = route_demands[idx_i] + route_demands[idx_j]
            if combined_demand > self.capacity:
                continue
            
            # Determine merge orientation
            new_start = new_end = None
            new_route = []
            
            if end_i == i:
                # i is at end of route_i
                if start_j == j:
                    # j is at start of route_j: route_i + route_j
                    new_route = routes[idx_i] + routes[idx_j]
                    new_start = start_i
                    new_end = end_j
                elif end_j == j:
                    # j is at end of route_j: route_i + route_j reversed
                    new_route = routes[idx_i] + routes[idx_j][::-1]
                    new_start = start_i
                    new_end = start_j
            elif start_i == i:
                # i is at start of route_i
                if start_j == j:
                    # j is at start of route_j: route_j reversed + route_i
                    new_route = routes[idx_j][::-1] + routes[idx_i]
                    new_start = end_j
                    new_end = end_i
                elif end_j == j:
                    # j is at end of route_j: route_j + route_i
                    new_route = routes[idx_j] + routes[idx_i]
                    new_start = start_j
                    new_end = end_i
            
            if not new_route:
                continue
            
            # Update data structures
            # Remove old routes (remove larger index first)
            idx1, idx2 = sorted([idx_i, idx_j], reverse=True)
            del routes[idx1]
            del routes[idx2]
            del route_demands[idx1]
            del route_demands[idx2]
            
            # Remove old endpoints and adjust indices
            new_endpoints = []
            for start, end, idx in route_endpoints:
                if idx == idx_i or idx == idx_j:
                    continue  # Skip deleted routes
                # Adjust index for deleted routes
                if idx > idx1:
                    idx -= 2
                elif idx > idx2:
                    idx -= 1
                new_endpoints.append((start, end, idx))
            
            route_endpoints = new_endpoints
            
            # Add new route
            routes.append(new_route)
            route_demands.append(combined_demand)
            new_idx = len(routes) - 1
            route_endpoints.append((new_start, new_end, new_idx))
        
        return routes
    
    def route_cost(self, route: List[int]) -> float:
        """Calculate total distance for a route (including depot at start and end)."""
        if not route:
            return 0.0
        
        cost = self.distance(0, route[0])  # Depot to first customer
        for k in range(len(route) - 1):
            cost += self.distance(route[k], route[k + 1])
        cost += self.distance(route[-1], 0)  # Last customer to depot
        return cost
    def two_opt_route(self, route: List[int]) -> List[int]:
        """
        Apply 2-opt local search to improve a single route.
        
        Args:
            route: List of customer indices
            
        Returns:
            Improved route
        """
        if len(route) < 4:
            return route[:]  # Too short for 2-opt
        
        best_route = route[:]
        best_cost = self.route_cost(best_route)
        improved = True
        
        while improved:
            improved = False
            for i in range(len(best_route) - 1):
                for j in range(i + 2, len(best_route)):
                    # Try 2-opt swap: reverse segment between i+1 and j
                    new_route = best_route[:]
                    new_route[i+1:j+1] = reversed(new_route[i+1:j+1])
                    
                    new_cost = self.route_cost(new_route)
                    if new_cost < best_cost - 1e-10:  # Small tolerance
                        best_route = new_route
                        best_cost = new_cost
                        improved = True
                        break  # Restart search after improvement
                if improved:
                    break
        
        return best_route
    
    def two_opt_all_routes(self, routes: List[List[int]]) -> List[List[int]]:
        """Apply 2-opt to all routes."""
        return [self.two_opt_route(route) for route in routes]
    def total_cost(self, routes: List[List[int]]) -> float:
        """Calculate total distance for all routes."""
        return sum(self.route_cost(route) for route in routes)
    def solve_cvrp(self, method: str = 'structural_hybrid', apply_2opt: bool = True) -> Dict:
        """
        Solve CVRP using specified method.
        
        Args:
            method: 'sequential', 'parallel', or 'structural_hybrid'
            apply_2opt: Whether to apply 2-opt local search to each route
            
        Returns:
            Dictionary with solution details
        """
        start_time = time.time()
        
        if method == 'sequential':
            routes = self.clarke_wright_savings_sequential()
        elif method == 'parallel':
            routes = self.clarke_wright_savings_parallel()
        elif method == 'structural_hybrid':
            routes = self.clarke_wright_structural_hybrid(community_aware=True)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        computation_time = time.time() - start_time
        
        if apply_2opt:
            routes = self.two_opt_all_routes(routes)
        
        # Calculate route statistics
        route_lengths = [self.route_cost(route) for route in routes]
        route_demands = [self.total_demand(route) for route in routes]
        
        # Check capacity violations
        capacity_violations = []
        has_capacity_violations = False
        for idx, demand in enumerate(route_demands):
            if demand > self.capacity:
                has_capacity_violations = True
                capacity_violations.append({
                    'route_idx': idx,
                    'demand': demand,
                    'capacity': self.capacity,
                    'excess': demand - self.capacity
                })
        
        return {
            'routes': routes,
            'total_distance': sum(route_lengths),
            'num_routes': len(routes),
            'computation_time': computation_time,
            'route_lengths': route_lengths,
            'route_demands': route_demands,
            'has_capacity_violations': has_capacity_violations,
            'capacity_violations': capacity_violations,
            'method_used': method
        }
    def benchmark(self, n_trials: int = 10, method: str = "parallel") -> Dict:
        """
        Run benchmark tests.
        
        Args:
            n_trials: Number of random instances to test
            method: 'sequential' or 'parallel'
            
        Returns:
            Benchmark statistics
        """
        distances = []
        times = []
        vehicles = []
        
        for trial in range(n_trials):
            # Create new instance with different seed
            instance = CapacitatedVRPStructuralHybrid(
                n_customers=self.n_customers,
                capacity=self.capacity,
                seed=trial * 1000 + 42,
                depot_at_center=True
            )
            
            result = instance.solve_cvrp(method=method)
            distances.append(result['total_distance'])
            times.append(result['computation_time'])
            vehicles.append(result['num_routes'])
        
        return {
            'avg_distance': np.mean(distances),
            'std_distance': np.std(distances),
            'avg_time': np.mean(times),
            'std_time': np.std(times),
            'avg_vehicles': np.mean(vehicles),
            'std_vehicles': np.std(vehicles),
            'min_distance': np.min(distances),
            'max_distance': np.max(distances),
            'n_trials': n_trials,
            'method': method,
            'n_customers': self.n_customers,
            'capacity': self.capacity
        }


    def solve_vrp(points: np.ndarray, demands: np.ndarray, capacity: float, 
              method: str = 'parallel', apply_2opt: bool = True) -> Dict:
        """
        Wrapper function for adversarial testing framework.
    
        Args:
        points: Array of shape (n, 2) with coordinates (first point is depot)
        demands: Array of length n with demands (depot demand should be 0)
        capacity: Vehicle capacity
        method: 'sequential' or 'parallel'
        apply_2opt: Whether to apply 2-opt intra-route improvement
        
        Returns:
        Dictionary with solution
        """
        n = len(points)
        n_customers = n - 1
    
        # Create VRP instance
        vrp = CapacitatedVRPStructuralHybrid(n_customers=n_customers, capacity=capacity, seed=None)
    
        # Override generated points and demands with provided ones
        vrp.points = points.copy()
        vrp.demands = demands.copy()
        vrp.n = n
        vrp.n_customers = n_customers
    
        # Recompute distance matrix
        vrp.dist_matrix = vrp._compute_distance_matrix()
    
        # Solve
        return vrp.solve_cvrp(method=method, apply_2opt=apply_2opt)


if __name__ == "__main__":
    # Example usage and benchmark
    print("Vehicle Routing Problem (VRP) - Clarke-Wright Savings Algorithm")
    print("=" * 60)
    
    # Create instance
    vrp = CapacitatedVRPStructuralHybrid(n_customers=100, capacity=100.0, seed=42)
    
    print(f"Problem: {vrp.n_customers} customers, capacity = {vrp.capacity}")
    print(f"Total demand: {sum(vrp.demands[1:]):.1f}")
    print(f"Min demand: {min(vrp.demands[1:]):.1f}, Max demand: {max(vrp.demands[1:]):.1f}")
    print()
    
    # Test sequential method
    print("Sequential Clarke-Wright:")
    result_seq = vrp.solve_cvrp(method='sequential')
    print(f"  Distance: {result_seq['total_distance']:.4f}")
    print(f"  Vehicles: {result_seq['num_vehicles']}")
    print(f"  Time: {result_seq['computation_time']:.4f}s")
    print()
    
    # Test parallel method
    print("Parallel Clarke-Wright:")
    result_par = vrp.solve_cvrp(method='parallel')
    print(f"  Distance: {result_par['total_distance']:.4f}")
    print(f"  Vehicles: {result_par['num_vehicles']}")
    print(f"  Time: {result_par['computation_time']:.4f}s")
    print()
    
    # Run benchmark
    print("Running benchmark (10 trials, parallel method)...")
    benchmark = vrp.benchmark(n_trials=10, method='parallel')
    
    print(f"Average distance: {benchmark['avg_distance']:.4f} ± {benchmark['std_distance']:.4f}")
    print(f"Average vehicles: {benchmark['avg_vehicles']:.1f} ± {benchmark['std_vehicles']:.1f}")
    print(f"Average time: {benchmark['avg_time']:.4f}s ± {benchmark['std_time']:.4f}s")
    print(f"Distance range: [{benchmark['min_distance']:.4f}, {benchmark['max_distance']:.4f}]")
    
    # Save benchmark results
    with open('/workspace/evovera/solutions/vrp_clarke_wright_benchmark.json', 'w') as f:
        json.dump(benchmark, f, indent=2, default=str)
    
    print("\nBenchmark saved to vrp_clarke_wright_benchmark.json")