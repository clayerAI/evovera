#!/usr/bin/env python3
"""
Traveling Salesman Problem (TSP) Solver
Evo - Algorithmic Solver
Baseline: Nearest Neighbor heuristic for Euclidean TSP
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
        
        # Try random starting cities
        starts = random.sample(range(self.n), min(num_starts, self.n))
        
        for start in starts:
            tour, distance = self.nearest_neighbor(start)
            if distance < best_distance:
                best_tour = tour
                best_distance = distance
        
        return best_tour, best_distance
    
    def tour_length(self, tour: List[int]) -> float:
        """Calculate total length of a tour."""
        total = 0.0
        for i in range(len(tour) - 1):
            total += self.distance(tour[i], tour[i + 1])
        return total
    
    def plot_tour(self, tour: List[int], title: str = "TSP Tour", save_path: str = None):
        """Plot the TSP tour (stub - would require matplotlib)."""
        print(f"Plot functionality would require matplotlib. Tour length: {self.tour_length(tour):.4f}")
        if save_path:
            print(f"Would save plot to {save_path}")
        # In a full implementation, this would generate a visualization


def benchmark_nearest_neighbor(num_instances: int = 10, n: int = 500, 
                              num_starts: int = 10) -> Dict:
    """
    Benchmark nearest neighbor algorithm on multiple instances.
    
    Args:
        num_instances: Number of random instances to test
        n: Number of cities per instance
        num_starts: Number of random starts for multistart NN
        
    Returns:
        Dictionary with benchmark results
    """
    results = {
        'algorithm': 'nearest_neighbor_multistart',
        'n': n,
        'num_instances': num_instances,
        'num_starts': num_starts,
        'instances': []
    }
    
    total_time = 0.0
    
    for i in range(num_instances):
        print(f"Instance {i+1}/{num_instances}...")
        
        # Create TSP instance
        tsp = EuclideanTSP(n=n, seed=i)
        
        # Run algorithm
        start_time = time.time()
        tour, distance = tsp.nearest_neighbor_multistart(num_starts=num_starts)
        elapsed = time.time() - start_time
        
        total_time += elapsed
        
        # Store results
        instance_result = {
            'instance_id': i,
            'seed': i,
            'tour_length': float(distance),
            'runtime': elapsed,
            'tour': tour[:20] + ['...'] if len(tour) > 20 else tour  # Truncate for storage
        }
        results['instances'].append(instance_result)
        
        print(f"  Tour length: {distance:.4f}, Time: {elapsed:.3f}s")
    
    # Summary statistics
    lengths = [inst['tour_length'] for inst in results['instances']]
    runtimes = [inst['runtime'] for inst in results['instances']]
    
    results['summary'] = {
        'avg_tour_length': float(np.mean(lengths)),
        'std_tour_length': float(np.std(lengths)),
        'min_tour_length': float(np.min(lengths)),
        'max_tour_length': float(np.max(lengths)),
        'avg_runtime': float(np.mean(runtimes)),
        'total_runtime': total_time
    }
    
    return results


if __name__ == "__main__":
    print("=" * 60)
    print("Evo TSP Solver - Nearest Neighbor Baseline")
    print("=" * 60)
    
    # Quick test with small instance
    print("\n1. Quick test with n=20:")
    tsp_small = EuclideanTSP(n=20, seed=42)
    tour_small, dist_small = tsp_small.nearest_neighbor_multistart(num_starts=5)
    print(f"   Tour length: {dist_small:.4f}")
    
    # Benchmark with 500 nodes
    print("\n2. Benchmarking with n=500 (3 instances):")
    results = benchmark_nearest_neighbor(num_instances=3, n=500, num_starts=10)
    
    print("\n3. Summary:")
    summary = results['summary']
    print(f"   Average tour length: {summary['avg_tour_length']:.4f}")
    print(f"   Min tour length: {summary['min_tour_length']:.4f}")
    print(f"   Max tour length: {summary['max_tour_length']:.4f}")
    print(f"   Average runtime: {summary['avg_runtime']:.3f}s")
    
    # Save results
    output_file = "/workspace/tsp_nn_baseline_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_file}")
    
    # Generate one plot
    print("\n4. Generating example plot...")
    tsp_plot = EuclideanTSP(n=100, seed=123)  # Smaller for visualization
    tour_plot, _ = tsp_plot.nearest_neighbor_multistart(num_starts=5)
    tsp_plot.plot_tour(tour_plot, title="Nearest Neighbor TSP Tour (n=100)", 
                      save_path="/workspace/tsp_nn_example.png")
    
    print("\n" + "=" * 60)
    print("Baseline implementation complete!")
    print("=" * 60)