#!/usr/bin/env python3
"""
Traveling Salesman Problem (TSP) Solver - Version 1: Nearest Neighbor with 2-opt
Evo - Algorithmic Solver
Baseline: Nearest Neighbor heuristic for Euclidean TSP with 2-opt local search

Includes solve_tsp() wrapper for adversarial testing framework.
"""

import numpy as np
import math
import random
import time
from typing import List, Tuple, Dict
import json


class EuclideanTSP:
    """Euclidean TSP with points in unit square [0,1] x [0,1]"""
    
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
        """Get distance between cities i and j."""
        return self.dist_matrix[i, j]
    
    def nearest_neighbor(self, start_city: int = None) -> Tuple[List[int], float]:
        """
        Nearest neighbor heuristic for TSP.
        
        Args:
            start_city: Starting city index (None for random)
            
        Returns:
            tour: List of city indices in visitation order
            total_distance: Total tour length
        """
        if start_city is None:
            start_city = random.randint(0, self.n - 1)
        
        unvisited = set(range(self.n))
        tour = [start_city]
        unvisited.remove(start_city)
        
        current = start_city
        total_distance = 0.0
        
        while unvisited:
            # Find nearest unvisited city
            nearest = min(unvisited, key=lambda city: self.distance(current, city))
            total_distance += self.distance(current, nearest)
            
            tour.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        # Return to starting city
        total_distance += self.distance(current, start_city)
        tour.append(start_city)
        
        return tour, total_distance
    
    def nearest_neighbor_multistart(self, num_starts: int = 10) -> Tuple[List[int], float]:
        """
        Run nearest neighbor from multiple starting cities and return best tour.
        
        Args:
            num_starts: Number of random starting cities to try
            
        Returns:
            best_tour: Best tour found
            best_distance: Distance of best tour
        """
        best_tour = None
        best_distance = float('inf')
        
        for _ in range(num_starts):
            tour, distance = self.nearest_neighbor()
            if distance < best_distance:
                best_tour = tour
                best_distance = distance
        
        return best_tour, best_distance
    
    def tour_distance(self, tour: List[int]) -> float:
        """Calculate total distance of a tour."""
        distance = 0.0
        for i in range(len(tour) - 1):
            distance += self.distance(tour[i], tour[i + 1])
        return distance
    
    def two_opt(self, tour: List[int], max_iterations: int = 1000) -> Tuple[List[int], float]:
        """
        Improve tour using 2-opt local search.
        
        Args:
            tour: Initial tour (must start and end at same vertex)
            max_iterations: Maximum number of iterations
            
        Returns:
            Improved tour and its distance
        """
        if len(tour) < 4 or tour[0] != tour[-1]:
            return tour, self.tour_distance(tour)
        
        # Remove duplicate start/end for processing
        tour = tour[:-1]
        n = len(tour)
        best_tour = tour[:]
        best_distance = self.tour_distance(tour + [tour[0]])
        
        improved = True
        iterations = 0
        
        while improved and iterations < max_iterations:
            improved = False
            iterations += 1
            
            for i in range(n):
                for j in range(i + 2, n):
                    if j == n - 1 and i == 0:
                        continue  # Don't swap first and last
                    
                    # Calculate gain from 2-opt swap
                    a, b = tour[i], tour[(i + 1) % n]
                    c, d = tour[j], tour[(j + 1) % n]
                    
                    old_distance = self.distance(a, b) + self.distance(c, d)
                    new_distance = self.distance(a, c) + self.distance(b, d)
                    
                    if new_distance < old_distance:
                        # Perform 2-opt swap
                        new_tour = tour[:i+1] + tour[i+1:j+1][::-1] + tour[j+1:]
                        new_tour_distance = self.tour_distance(new_tour + [new_tour[0]])
                        
                        if new_tour_distance < best_distance:
                            best_tour = new_tour[:]
                            best_distance = new_tour_distance
                            tour = new_tour[:]
                            improved = True
                            break  # Restart search after improvement
                
                if improved:
                    break
        
        # Add closing vertex
        best_tour.append(best_tour[0])
        return best_tour, best_distance
    
    def nearest_neighbor_with_2opt(self, num_starts: int = 10, two_opt_iterations: int = 500) -> Tuple[List[int], float]:
        """
        Nearest neighbor with 2-opt local search improvement.
        
        Args:
            num_starts: Number of random starts for nearest neighbor
            two_opt_iterations: Maximum iterations for 2-opt
            
        Returns:
            tour: Improved tour
            distance: Total tour length
        """
        # Get initial tour from nearest neighbor
        tour, distance = self.nearest_neighbor_multistart(num_starts)
        
        # Apply 2-opt improvement
        tour, distance = self.two_opt(tour, max_iterations=two_opt_iterations)
        
        return tour, distance


def solve_tsp(points):
    """
    Standard interface for TSP algorithms.
    
    Args:
        points: numpy array of shape (n, 2) with (x, y) coordinates
        
    Returns:
        tuple: (tour, length) where tour is list of indices, length is float
    """
    n = len(points)
    
    # Create a custom TSP instance with these points
    class CustomTSP:
        def __init__(self, points):
            self.n = len(points)
            self.points = points
            self.dist_matrix = self._compute_distance_matrix()
        
        def _compute_distance_matrix(self):
            dist = np.zeros((self.n, self.n))
            for i in range(self.n):
                for j in range(i + 1, self.n):
                    d = np.linalg.norm(self.points[i] - self.points[j])
                    dist[i, j] = d
                    dist[j, i] = d
            return dist
        
        def distance(self, i, j):
            return self.dist_matrix[i, j]
        
        def nearest_neighbor(self, start_city=0):
            unvisited = set(range(self.n))
            tour = [start_city]
            unvisited.remove(start_city)
            
            current = start_city
            
            while unvisited:
                nearest = min(unvisited, key=lambda city: self.distance(current, city))
                tour.append(nearest)
                unvisited.remove(nearest)
                current = nearest
            
            # Return to starting city
            tour.append(start_city)
            return tour
        
        def tour_distance(self, tour):
            distance = 0.0
            for i in range(len(tour) - 1):
                distance += self.distance(tour[i], tour[i + 1])
            return distance
        
        def two_opt(self, tour, max_iterations=1000):
            if len(tour) < 4 or tour[0] != tour[-1]:
                return tour
            
            tour = tour[:-1]
            n = len(tour)
            improved = True
            iteration = 0
            
            while improved and iteration < max_iterations:
                improved = False
                for i in range(n - 1):
                    for j in range(i + 2, n):
                        # Calculate current distance for edges (i, i+1) and (j, j+1)
                        current = (self.distance(tour[i], tour[(i + 1) % n]) +
                                  self.distance(tour[j], tour[(j + 1) % n]))
                        # Calculate new distance if we reverse segment between i+1 and j
                        new = (self.distance(tour[i], tour[j]) +
                              self.distance(tour[(i + 1) % n], tour[(j + 1) % n]))
                        
                        if new < current:
                            # Reverse the segment
                            tour[i + 1:j + 1] = reversed(tour[i + 1:j + 1])
                            improved = True
                            break
                    if improved:
                        break
                iteration += 1
            
            # Add back the starting city
            tour.append(tour[0])
            return tour
    
    # Create TSP instance and solve
    tsp = CustomTSP(points)
    tour = tsp.nearest_neighbor(start_city=0)
    tour = tsp.two_opt(tour, max_iterations=1000)
    length = tsp.tour_distance(tour)
    
    # Convert closed tour to open tour (remove duplicate start city)
    if len(tour) > 0 and tour[0] == tour[-1]:
        tour = tour[:-1]
    
    return tour, length


def benchmark_nearest_neighbor():
    """Benchmark nearest neighbor algorithm with 2-opt."""
    print("Benchmarking Nearest Neighbor with 2-opt for Euclidean TSP (n=500)")
    print("=" * 70)
    
    results = []
    num_instances = 10
    total_time = 0.0
    
    for i in range(num_instances):
        print(f"\nInstance {i+1}/{num_instances}:")
        
        # Create TSP instance
        tsp = EuclideanTSP(n=500, seed=i)
        
        # Time the algorithm
        start_time = time.time()
        tour, distance = tsp.nearest_neighbor_with_2opt(num_starts=10, two_opt_iterations=500)
        end_time = time.time()
        
        instance_time = end_time - start_time
        total_time += instance_time
        
        print(f"  Tour length: {distance:.4f}")
        print(f"  Time: {instance_time:.3f} seconds")
        
        results.append({
            "instance": i,
            "seed": i,
            "tour_length": distance,
            "time": instance_time,
            "algorithm": "nearest_neighbor_2opt"
        })
    
    # Calculate statistics
    tour_lengths = [r["tour_length"] for r in results]
    avg_length = np.mean(tour_lengths)
    std_length = np.std(tour_lengths)
    avg_time = total_time / num_instances
    
    print("\n" + "=" * 70)
    print("SUMMARY:")
    print(f"  Number of instances: {num_instances}")
    print(f"  Average tour length: {avg_length:.4f}")
    print(f"  Standard deviation: {std_length:.4f}")
    print(f"  Average time per instance: {avg_time:.3f} seconds")
    
    # Save results
    output = {
        "algorithm": "nearest_neighbor_with_2opt",
        "n": 500,
        "num_instances": num_instances,
        "average_tour_length": avg_length,
        "std_tour_length": std_length,
        "average_time": avg_time,
        "results": results
    }
    
    with open("nearest_neighbor_2opt_benchmarks.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("\nResults saved to 'nearest_neighbor_2opt_benchmarks.json'")


if __name__ == "__main__":
    benchmark_nearest_neighbor()