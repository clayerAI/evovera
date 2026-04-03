#!/usr/bin/env python3
"""
Traveling Salesman Problem (TSP) Solver - Version 3: Lin-Kernighan Heuristic
Evo - Algorithmic Solver
Lin-Kernighan heuristic for high-quality TSP solutions
"""

import numpy as np
import math
import random
import time
import heapq
from typing import List, Tuple, Dict, Set, Optional
import json


class EuclideanTSPLinKernighan:
    """Euclidean TSP with Lin-Kernighan heuristic implementation"""
    
    def __init__(self, n: int = 500, seed: int = None):
        """
        Initialize random Euclidean TSP instance.
        
        Args:
            n: Number of cities
            seed: Random seed for reproducibility
        """
        self.n = n
        self.seed = seed
        
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
        
        # Generate random points in unit square
        self.points = np.random.rand(n, 2)
        
        # Precompute distance matrix
        self.dist_matrix = self._compute_distance_matrix()
        
        # Precompute nearest neighbor lists for efficiency
        self.nearest_neighbors = self._compute_nearest_neighbors(k=50)
    
    def _compute_distance_matrix(self) -> np.ndarray:
        """Compute Euclidean distance matrix between all points."""
        dist = np.zeros((self.n, self.n))
        for i in range(self.n):
            for j in range(i + 1, self.n):
                d = math.sqrt(((self.points[i] - self.points[j]) ** 2).sum())
                dist[i, j] = d
                dist[j, i] = d
        return dist
    
    def _compute_nearest_neighbors(self, k: int = 50) -> List[List[int]]:
        """Compute k nearest neighbors for each city for efficient LK search."""
        neighbors = []
        for i in range(self.n):
            # Get distances to all other cities
            distances = [(self.dist_matrix[i, j], j) for j in range(self.n) if j != i]
            # Sort by distance
            distances.sort()
            # Take k nearest
            neighbors.append([j for _, j in distances[:k]])
        return neighbors
    
    def nearest_neighbor_tour(self, start: int = 0) -> List[int]:
        """Construct tour using nearest neighbor heuristic."""
        unvisited = set(range(self.n))
        tour = [start]
        unvisited.remove(start)
        
        current = start
        while unvisited:
            # Find nearest unvisited city
            nearest = min(unvisited, key=lambda city: self.dist_matrix[current, city])
            tour.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        return tour
    
    def tour_length(self, tour: List[int]) -> float:
        """Calculate total length of a tour."""
        total = 0.0
        for i in range(len(tour)):
            j = (i + 1) % len(tour)
            total += self.dist_matrix[tour[i], tour[j]]
        return total
    
    def two_opt_improvement(self, tour: List[int], max_iterations: int = 1000) -> List[int]:
        """Apply 2-opt local search to improve tour."""
        improved = True
        iteration = 0
        current_tour = tour.copy()
        n = len(current_tour)
        
        while improved and iteration < max_iterations:
            improved = False
            best_gain = 0
            best_i = best_j = -1
            
            # Search for best 2-opt move
            for i in range(n - 1):
                for k in range(i + 2, n):
                    if k == n - 1 and i == 0:
                        continue  # Skip invalid move
                    
                    # Calculate gain from swapping edges (i, i+1) and (k, k+1)
                    a, b = current_tour[i], current_tour[(i + 1) % n]
                    c, d = current_tour[k], current_tour[(k + 1) % n]
                    
                    gain = (self.dist_matrix[a, b] + self.dist_matrix[c, d]) - \
                           (self.dist_matrix[a, c] + self.dist_matrix[b, d])
                    
                    if gain > best_gain:
                        best_gain = gain
                        best_i, best_j = i, k
                        improved = True
            
            # Apply best move if found
            if improved:
                # Reverse segment between i+1 and k
                i, j = best_i, best_j
                current_tour[i + 1:j + 1] = reversed(current_tour[i + 1:j + 1])
                iteration += 1
            else:
                break
        
        return current_tour
    
    def lin_kernighan_improvement(self, initial_tour: List[int], max_k: int = 5, 
                                  max_iterations: int = 100) -> List[int]:
        """
        Apply Lin-Kernighan-style heuristic to improve tour.
        
        This implements an iterative local search with:
        1. Multiple random restarts
        2. Aggressive 2-opt with limited neighborhood
        3. Kick moves to escape local optima
        
        Args:
            initial_tour: Starting tour
            max_k: Maximum k for k-opt moves (unused in this simplified version)
            max_iterations: Maximum iterations
        
        Returns:
            Improved tour
        """
        best_tour = initial_tour.copy()
        best_length = self.tour_length(best_tour)
        n = len(best_tour)
        
        for iteration in range(max_iterations):
            # Start from current best tour
            current_tour = best_tour.copy()
            
            # Apply aggressive 2-opt with limited neighborhood search
            current_tour = self._aggressive_two_opt(current_tour, neighborhood_size=50)
            current_length = self.tour_length(current_tour)
            
            # Apply double-bridge kick to escape local optimum
            if iteration % 5 == 0 and iteration > 0:
                current_tour = self._double_bridge_kick(current_tour)
                current_tour = self._aggressive_two_opt(current_tour, neighborhood_size=50)
                current_length = self.tour_length(current_tour)
            
            # Check if improvement found
            if current_length < best_length:
                best_tour = current_tour
                best_length = current_length
        
        return best_tour
    
    def _aggressive_two_opt(self, tour: List[int], neighborhood_size: int = 50) -> List[int]:
        """
        Apply aggressive 2-opt search using limited neighborhood.
        
        Args:
            tour: Input tour
            neighborhood_size: Number of nearest neighbors to consider for each city
        
        Returns:
            Improved tour
        """
        n = len(tour)
        current_tour = tour.copy()
        improved = True
        iteration = 0
        
        # Create position mapping
        position = {city: idx for idx, city in enumerate(current_tour)}
        
        while improved and iteration < 100:
            improved = False
            best_gain = 0
            best_i = best_j = -1
            
            # Search for best 2-opt move using limited neighborhood
            for i in range(n):
                city_i = current_tour[i]
                # Consider only nearest neighbors of city_i
                for neighbor_idx in self.nearest_neighbors[city_i][:neighborhood_size]:
                    j = position[neighbor_idx]
                    
                    # Ensure valid move (edges not adjacent)
                    if abs(i - j) <= 1 or (i == 0 and j == n - 1) or (j == 0 and i == n - 1):
                        continue
                    
                    # Calculate gain
                    a, b = current_tour[i], current_tour[(i + 1) % n]
                    c, d = current_tour[j], current_tour[(j + 1) % n]
                    
                    gain = (self.dist_matrix[a, b] + self.dist_matrix[c, d]) - \
                           (self.dist_matrix[a, c] + self.dist_matrix[b, d])
                    
                    if gain > best_gain:
                        best_gain = gain
                        best_i, best_j = i, j
                        improved = True
            
            # Apply best move if found
            if improved:
                i, j = best_i, best_j
                # Reverse segment between i+1 and j
                if i < j:
                    current_tour[i + 1:j + 1] = reversed(current_tour[i + 1:j + 1])
                else:
                    # Handle wrap-around
                    segment = current_tour[i + 1:] + current_tour[:j + 1]
                    segment.reverse()
                    current_tour[i + 1:] = segment[:n - i - 1]
                    current_tour[:j + 1] = segment[n - i - 1:]
                
                # Update position mapping
                position = {city: idx for idx, city in enumerate(current_tour)}
                iteration += 1
        
        return current_tour
    
    def _double_bridge_kick(self, tour: List[int]) -> List[int]:
        """
        Apply double-bridge move (4-opt) to escape local optima.
        
        The double-bridge move cuts the tour into 4 segments and reconnects them
        in a different order, creating a large perturbation.
        
        Args:
            tour: Input tour
        
        Returns:
            Perturbed tour
        """
        n = len(tour)
        if n < 8:
            return tour.copy()
        
        # Choose 4 random cut points
        cuts = sorted(random.sample(range(1, n - 1), 4))
        a, b, c, d = cuts
        
        # Create new tour by reordering segments: [0:a], [c:d], [b:c], [a:b], [d:]
        new_tour = tour[:a] + tour[c:d] + tour[b:c] + tour[a:b] + tour[d:]
        
        return new_tour
    
    def solve_tsp(self, algorithm: str = "lin_kernighan", **kwargs) -> Tuple[List[int], float, float]:
        """
        Solve TSP using specified algorithm.
        
        Args:
            algorithm: "nearest_neighbor", "two_opt", or "lin_kernighan"
            **kwargs: Algorithm-specific parameters
        
        Returns:
            Tuple of (tour, tour_length, runtime_seconds)
        """
        start_time = time.time()
        
        if algorithm == "nearest_neighbor":
            tour = self.nearest_neighbor_tour()
        elif algorithm == "two_opt":
            nn_tour = self.nearest_neighbor_tour()
            tour = self.two_opt_improvement(nn_tour, **kwargs)
        elif algorithm == "lin_kernighan":
            nn_tour = self.nearest_neighbor_tour()
            two_opt_tour = self.two_opt_improvement(nn_tour)
            tour = self.lin_kernighan_improvement(two_opt_tour, **kwargs)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        runtime = time.time() - start_time
        length = self.tour_length(tour)
        
        return tour, length, runtime
    
    def benchmark(self, algorithms: List[str] = None, n_runs: int = 5) -> Dict:
        """
        Benchmark different algorithms on this TSP instance.
        
        Args:
            algorithms: List of algorithm names to benchmark
            n_runs: Number of runs per algorithm
        
        Returns:
            Dictionary with benchmark results
        """
        if algorithms is None:
            algorithms = ["nearest_neighbor", "two_opt", "lin_kernighan"]
        
        results = {
            "instance_info": {
                "n": self.n,
                "seed": self.seed,
                "points_hash": hash(str(self.points.tobytes()))
            },
            "algorithms": {}
        }
        
        for algo in algorithms:
            algo_results = {
                "tour_lengths": [],
                "runtimes": [],
                "tours": []
            }
            
            for run in range(n_runs):
                if algo == "nearest_neighbor":
                    tour, length, runtime = self.solve_tsp("nearest_neighbor")
                elif algo == "two_opt":
                    tour, length, runtime = self.solve_tsp("two_opt", max_iterations=1000)
                elif algo == "lin_kernighan":
                    tour, length, runtime = self.solve_tsp("lin_kernighan", max_k=3, max_iterations=50)
                
                algo_results["tour_lengths"].append(length)
                algo_results["runtimes"].append(runtime)
                if run == 0:  # Save only first tour to avoid large output
                    algo_results["tours"].append(tour)
            
            # Calculate statistics
            algo_results["avg_length"] = np.mean(algo_results["tour_lengths"])
            algo_results["std_length"] = np.std(algo_results["tour_lengths"])
            algo_results["avg_runtime"] = np.mean(algo_results["runtimes"])
            algo_results["std_runtime"] = np.std(algo_results["runtimes"])
            algo_results["best_length"] = min(algo_results["tour_lengths"])
            
            results["algorithms"][algo] = algo_results
        
        return results


def solve_tsp(points: np.ndarray) -> Tuple[List[int], float]:
    """
    Wrapper function for adversarial testing framework.
    
    Args:
        points: Nx2 array of city coordinates
    
    Returns:
        Tuple of (tour, tour_length)
    """
    n = len(points)
    solver = EuclideanTSPLinKernighan(n=n, seed=42)
    solver.points = points  # Use provided points
    solver.dist_matrix = solver._compute_distance_matrix()  # Recompute distances
    solver.nearest_neighbors = solver._compute_nearest_neighbors(k=50)
    
    # Use LK algorithm
    tour, length, _ = solver.solve_tsp("lin_kernighan", max_k=3, max_iterations=50)
    return tour, length


if __name__ == "__main__":
    # Example usage and self-test
    print("=== TSP Solver v3: Lin-Kernighan Heuristic ===")
    
    # Create instance
    solver = EuclideanTSPLinKernighan(n=100, seed=42)  # Smaller for quick test
    
    # Test algorithms
    print("\nTesting algorithms on 100-city instance:")
    
    # Nearest Neighbor
    nn_tour, nn_length, nn_time = solver.solve_tsp("nearest_neighbor")
    print(f"Nearest Neighbor: {nn_length:.4f} ({nn_time:.3f}s)")
    
    # 2-opt
    two_opt_tour, two_opt_length, two_opt_time = solver.solve_tsp("two_opt", max_iterations=500)
    print(f"2-opt: {two_opt_length:.4f} ({two_opt_time:.3f}s)")
    print(f"  Improvement: {((nn_length - two_opt_length) / nn_length * 100):.2f}%")
    
    # Lin-Kernighan
    lk_tour, lk_length, lk_time = solver.solve_tsp("lin_kernighan", max_k=3, max_iterations=20)
    print(f"Lin-Kernighan: {lk_length:.4f} ({lk_time:.3f}s)")
    print(f"  Improvement over 2-opt: {((two_opt_length - lk_length) / two_opt_length * 100):.2f}%")
    
    # Run benchmark
    print("\nRunning benchmark...")
    benchmark_results = solver.benchmark(n_runs=3)
    
    # Save results
    with open("lin_kernighan_benchmark.json", "w") as f:
        json.dump(benchmark_results, f, indent=2)
    
    print("Benchmark results saved to lin_kernighan_benchmark.json")
    
    # Verify solve_tsp wrapper
    print("\nTesting solve_tsp wrapper for adversarial testing...")
    test_tour, test_length = solve_tsp(solver.points)
    print(f"Wrapper result: {test_length:.4f}")
    print(f"Matches direct call: {abs(test_length - lk_length) < 0.001}")