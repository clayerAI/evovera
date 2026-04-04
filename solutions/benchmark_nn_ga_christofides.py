"""
Benchmark NN-GA with Christofides-Inspired Crossover Hybrid
Compare against Nearest Neighbor + 2-opt baseline
"""

import random
import math
import time
import json
from typing import List, Tuple
import numpy as np
from solutions.tsp_v9_nn_ga_christofides_crossover import (
    distance_matrix, 
    nearest_neighbor_tour,
    two_opt_improvement,
    tour_length,
    nn_ga_christofides_crossover_hybrid
)

def nn_2opt_baseline(coords: List[Tuple[float, float]]) -> Tuple[List[int], float, float]:
    """Nearest Neighbor + 2-opt baseline."""
    dist = distance_matrix(coords)
    
    # Try multiple starting points
    n = len(coords)
    best_tour = None
    best_length = float('inf')
    
    for start in range(min(5, n)):  # Try up to 5 starting points
        tour = nearest_neighbor_tour(dist, start)
        tour = two_opt_improvement(tour, dist, max_iterations=2000)
        length = tour_length(tour, dist)
        
        if length < best_length:
            best_length = length
            best_tour = tour
    
    return best_tour, best_length

def run_benchmark(instance_sizes: List[int] = [20, 50, 100], trials: int = 5):
    """Run benchmark on different instance sizes."""
    results = {}
    
    for n in instance_sizes:
        print(f"\n{'='*60}")
        print(f"Benchmarking n={n}")
        print(f"{'='*60}")
        
        nn_2opt_times = []
        nn_2opt_lengths = []
        
        hybrid_times = []
        hybrid_lengths = []
        
        for trial in range(trials):
            print(f"\nTrial {trial+1}/{trials}")
            
            # Generate random instance
            random.seed(trial * 100 + n)
            coords = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(n)]
            
            # Run NN+2opt baseline
            start_time = time.time()
            nn_tour, nn_length = nn_2opt_baseline(coords)
            nn_time = time.time() - start_time
            
            nn_2opt_times.append(nn_time)
            nn_2opt_lengths.append(nn_length)
            
            print(f"  NN+2opt: length={nn_length:.4f}, time={nn_time:.2f}s")
            
            # Run hybrid algorithm
            start_time = time.time()
            hybrid_tour = nn_ga_christofides_crossover_hybrid(
                coords,
                generations=30 if n <= 50 else 20,
                population_size=20 if n <= 50 else 15,
                crossover_rate=0.8,
                mutation_rate=0.1,
                elitism=2
            )
            hybrid_time = time.time() - start_time
            
            dist = distance_matrix(coords)
            hybrid_length = tour_length(hybrid_tour, dist)
            
            hybrid_times.append(hybrid_time)
            hybrid_lengths.append(hybrid_length)
            
            print(f"  Hybrid:  length={hybrid_length:.4f}, time={hybrid_time:.2f}s")
            
            # Calculate improvement
            if nn_length > 0:
                improvement = (nn_length - hybrid_length) / nn_length * 100
                print(f"  Improvement: {improvement:+.2f}%")
        
        # Calculate statistics
        avg_nn_length = sum(nn_2opt_lengths) / trials
        avg_nn_time = sum(nn_2opt_times) / trials
        
        avg_hybrid_length = sum(hybrid_lengths) / trials
        avg_hybrid_time = sum(hybrid_times) / trials
        
        avg_improvement = (avg_nn_length - avg_hybrid_length) / avg_nn_length * 100
        
        results[n] = {
            'nn_2opt': {
                'avg_length': avg_nn_length,
                'avg_time': avg_nn_time,
                'lengths': nn_2opt_lengths,
                'times': nn_2opt_times
            },
            'hybrid': {
                'avg_length': avg_hybrid_length,
                'avg_time': avg_hybrid_time,
                'lengths': hybrid_lengths,
                'times': hybrid_times
            },
            'improvement_percent': avg_improvement,
            'speedup_factor': avg_nn_time / avg_hybrid_time if avg_hybrid_time > 0 else 0
        }
        
        print(f"\nSummary for n={n}:")
        print(f"  NN+2opt avg: {avg_nn_length:.4f} in {avg_nn_time:.2f}s")
        print(f"  Hybrid avg:  {avg_hybrid_length:.4f} in {avg_hybrid_time:.2f}s")
        print(f"  Avg improvement: {avg_improvement:+.2f}%")
        print(f"  Speedup: {results[n]['speedup_factor']:.2f}x")
    
    return results

def save_results(results: dict, filename: str = "nn_ga_christofides_benchmark.json"):
    """Save benchmark results to JSON file."""
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {filename}")

if __name__ == "__main__":
    print("Benchmark: NN-GA with Christofides-Inspired Crossover Hybrid")
    print("Comparing against NN+2opt baseline")
    
    results = run_benchmark(instance_sizes=[20, 50], trials=3)
    save_results(results, "/workspace/evovera/nn_ga_christofides_benchmark.json")
    
    # Print final summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    
    for n in results:
        data = results[n]
        print(f"\nn={n}:")
        print(f"  NN+2opt: {data['nn_2opt']['avg_length']:.4f} ({data['nn_2opt']['avg_time']:.2f}s)")
        print(f"  Hybrid:  {data['hybrid']['avg_length']:.4f} ({data['hybrid']['avg_time']:.2f}s)")
        print(f"  Improvement: {data['improvement_percent']:+.2f}%")
        print(f"  Speedup: {data['speedup_factor']:.2f}x")