"""
Reference implementation of Nearest Neighbor with 2-opt baseline.

This is the canonical baseline implementation that must be used for all
performance comparisons according to the review framework.

Features:
- Fixed random seed for reproducible instance generation
- Standardized 2-opt implementation
- Consistent tour length calculation
- Unit square [0,1]² coordinates only
"""

import numpy as np
from typing import List, Tuple, Optional
import time

def generate_random_instance(n: int, seed: Optional[int] = None) -> np.ndarray:
    """
    Generate random TSP instance in unit square [0,1]².
    
    Args:
        n: Number of cities
        seed: Random seed for reproducibility
        
    Returns:
        Array of shape (n, 2) with coordinates in [0,1]²
    """
    if seed is not None:
        np.random.seed(seed)
    
    return np.random.rand(n, 2)

def euclidean_distance(p1: np.ndarray, p2: np.ndarray) -> float:
    """Calculate Euclidean distance between two points."""
    return np.sqrt(np.sum((p1 - p2) ** 2))

def distance_matrix(points: np.ndarray) -> np.ndarray:
    """
    Compute Euclidean distance matrix.
    
    Args:
        points: Array of shape (n, 2)
        
    Returns:
        Distance matrix of shape (n, n)
    """
    n = len(points)
    dist = np.zeros((n, n))
    
    for i in range(n):
        for j in range(i + 1, n):
            d = euclidean_distance(points[i], points[j])
            dist[i, j] = d
            dist[j, i] = d
    
    return dist

def nearest_neighbor_tour(dist_matrix: np.ndarray, start_city: int = 0) -> List[int]:
    """
    Construct tour using Nearest Neighbor heuristic.
    
    Args:
        dist_matrix: Distance matrix
        start_city: Starting city index
        
    Returns:
        Tour as list of city indices
    """
    n = dist_matrix.shape[0]
    unvisited = set(range(n))
    tour = [start_city]
    unvisited.remove(start_city)
    
    current = start_city
    while unvisited:
        # Find nearest unvisited city
        nearest = min(unvisited, key=lambda city: dist_matrix[current, city])
        tour.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    
    return tour

def tour_length(tour: List[int], dist_matrix: np.ndarray) -> float:
    """Calculate total length of a tour."""
    total = 0.0
    for i in range(len(tour)):
        j = (i + 1) % len(tour)
        total += dist_matrix[tour[i], tour[j]]
    return total

def two_opt_swap(tour: List[int], i: int, k: int) -> List[int]:
    """
    Perform 2-opt swap between positions i and k.
    
    Args:
        tour: Current tour
        i, k: Swap indices (i < k)
        
    Returns:
        New tour after 2-opt swap
    """
    new_tour = tour[:i] + tour[i:k+1][::-1] + tour[k+1:]
    return new_tour

def two_opt_improvement(
    tour: List[int],
    dist_matrix: np.ndarray,
    max_iterations: int = 1000
) -> Tuple[List[int], float]:
    """
    Apply 2-opt local search to improve tour.
    
    Args:
        tour: Initial tour
        dist_matrix: Distance matrix
        max_iterations: Maximum iterations
        
    Returns:
        (improved_tour, improvement_found)
    """
    n = len(tour)
    current_tour = tour.copy()
    current_length = tour_length(current_tour, dist_matrix)
    improved = True
    iterations = 0
    
    while improved and iterations < max_iterations:
        improved = False
        iterations += 1
        
        for i in range(n - 1):
            for k in range(i + 1, n):
                # Calculate gain from 2-opt swap
                a, b = current_tour[i], current_tour[(i + 1) % n]
                c, d = current_tour[k], current_tour[(k + 1) % n]
                
                current_edge = dist_matrix[a, b] + dist_matrix[c, d]
                new_edge = dist_matrix[a, c] + dist_matrix[b, d]
                
                if new_edge < current_edge:
                    # Perform swap
                    current_tour = two_opt_swap(current_tour, i, k)
                    current_length = current_length - current_edge + new_edge
                    improved = True
                    break  # Restart search after improvement
            if improved:
                break
    
    return current_tour, current_length

def nn_2opt_solve(
    points: np.ndarray,
    start_city: int = 0,
    time_limit: float = 30.0
) -> Tuple[List[int], float, float]:
    """
    Solve TSP using Nearest Neighbor with 2-opt local search.
    
    Args:
        points: Array of shape (n, 2) with coordinates
        start_city: Starting city for NN heuristic
        time_limit: Maximum time in seconds
        
    Returns:
        (tour, length, computation_time)
    """
    start_time = time.time()
    
    # Compute distance matrix
    dist_matrix = distance_matrix(points)
    
    # Nearest Neighbor construction
    nn_tour = nearest_neighbor_tour(dist_matrix, start_city)
    nn_length = tour_length(nn_tour, dist_matrix)
    
    # 2-opt improvement
    improved_tour, improved_length = two_opt_improvement(
        nn_tour, dist_matrix, max_iterations=10000
    )
    
    computation_time = time.time() - start_time
    
    return improved_tour, improved_length, computation_time

def benchmark_nn_2opt(
    n_values: List[int] = [50, 100, 200, 500],
    instances_per_size: int = 10,
    seed_sequence: List[int] = list(range(100, 200)),
    time_limit: float = 30.0
) -> dict:
    """
    Run standardized benchmark of NN+2opt baseline.
    
    Args:
        n_values: List of problem sizes to test
        instances_per_size: Number of random instances per size
        seed_sequence: List of seeds for reproducible instance generation
        time_limit: Time limit per instance
        
    Returns:
        Dictionary with benchmark results
    """
    results = {
        "baseline": "NN+2opt",
        "coordinate_range": "[0,1]²",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "parameters": {
            "n_values": n_values,
            "instances_per_size": instances_per_size,
            "time_limit": time_limit
        },
        "results_by_size": {}
    }
    
    seed_idx = 0
    
    for n in n_values:
        print(f"Benchmarking n={n}...")
        tour_lengths = []
        computation_times = []
        
        for instance_idx in range(instances_per_size):
            if seed_idx >= len(seed_sequence):
                seed_idx = 0  # Wrap around if needed
            
            seed = seed_sequence[seed_idx]
            seed_idx += 1
            
            # Generate instance
            points = generate_random_instance(n, seed)
            
            # Solve with NN+2opt
            tour, length, comp_time = nn_2opt_solve(
                points, start_city=0, time_limit=time_limit
            )
            
            tour_lengths.append(length)
            computation_times.append(comp_time)
            
            if comp_time > time_limit:
                print(f"  Warning: Instance {instance_idx} exceeded time limit: {comp_time:.2f}s")
        
        # Calculate statistics
        mean_length = np.mean(tour_lengths)
        std_length = np.std(tour_lengths)
        mean_time = np.mean(computation_times)
        
        results["results_by_size"][str(n)] = {
            "mean_tour_length": float(mean_length),
            "std_tour_length": float(std_length),
            "mean_computation_time": float(mean_time),
            "tour_lengths": [float(x) for x in tour_lengths],
            "computation_times": [float(x) for x in computation_times],
            "instances_tested": instances_per_size,
            "seeds_used": seed_sequence[seed_idx-instances_per_size:seed_idx]
        }
        
        print(f"  n={n}: Mean length = {mean_length:.3f} ± {std_length:.3f}")
        print(f"        Mean time = {mean_time:.3f}s")
    
    return results

def save_benchmark_results(results: dict, filepath: str) -> None:
    """Save benchmark results to JSON file."""
    import json
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Benchmark results saved to: {filepath}")

def load_benchmark_results(filepath: str) -> dict:
    """Load benchmark results from JSON file."""
    import json
    with open(filepath, 'r') as f:
        return json.load(f)

def example_usage():
    """Example usage of the baseline implementation."""
    print("NN+2opt Baseline Implementation")
    print("=" * 50)
    
    # Generate a small instance
    points = generate_random_instance(10, seed=42)
    print(f"Generated {len(points)} points in [0,1]²")
    
    # Solve with NN+2opt
    tour, length, comp_time = nn_2opt_solve(points)
    print(f"\nSolution:")
    print(f"  Tour length: {length:.4f}")
    print(f"  Computation time: {comp_time:.4f}s")
    print(f"  Tour (first 10 cities): {tour[:10]}...")
    
    # Run benchmark
    print("\nRunning benchmark (small scale for example)...")
    results = benchmark_nn_2opt(
        n_values=[20, 30],  # Small sizes for quick example
        instances_per_size=3,
        time_limit=5.0
    )
    
    print("\nBenchmark complete!")
    print(f"Baseline: {results['baseline']}")
    print(f"Coordinate range: {results['coordinate_range']}")
    
    for n, size_results in results["results_by_size"].items():
        print(f"\nn={n}:")
        print(f"  Mean length: {size_results['mean_tour_length']:.3f}")
        print(f"  Std length: {size_results['std_tour_length']:.3f}")
        print(f"  Mean time: {size_results['mean_computation_time']:.3f}s")

if __name__ == "__main__":
    example_usage()