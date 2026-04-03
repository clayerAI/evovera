#!/usr/bin/env python3
"""
TSP Benchmarking Framework
Evo - Algorithmic Solver
Track approximation ratio against optimal/best known solutions
"""

import numpy as np
import math
import random
import time
import json
import csv
from datetime import datetime
from typing import List, Tuple, Dict, Any, Callable
from pathlib import Path

# Import our TSP solver
from tsp_solver import EuclideanTSP


class TSPBenchmark:
    """Benchmarking framework for TSP algorithms."""
    
    def __init__(self, output_dir: str = "/workspace/tsp_benchmarks"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Known optimal/best known solutions (to be populated from research)
        # For random Euclidean TSP, we can use theoretical bounds
        self.known_solutions = {
            # Theoretical lower bound for n points in unit square
            # Beardwood-Halton-Hammersley theorem: optimal ~ β√n where β ≈ 0.721
            'theoretical_lower_bound': lambda n: 0.721 * math.sqrt(n),
            
            # Christofides algorithm guarantee: 1.5 * optimal
            'christofides_upper_bound': lambda n: 1.5 * 0.721 * math.sqrt(n),
            
            # Nearest neighbor typical performance: ~1.25 * optimal
            'nn_typical': lambda n: 1.25 * 0.721 * math.sqrt(n),
        }
    
    def generate_instance(self, n: int, seed: int) -> EuclideanTSP:
        """Generate a reproducible TSP instance."""
        return EuclideanTSP(n=n, seed=seed)
    
    def calculate_approximation_ratio(self, tour_length: float, n: int, 
                                     reference: str = 'theoretical_lower_bound') -> float:
        """
        Calculate approximation ratio relative to reference.
        
        Args:
            tour_length: Length of found tour
            n: Number of cities
            reference: Which reference to use ('theoretical_lower_bound', etc.)
            
        Returns:
            Approximation ratio (tour_length / reference_length)
        """
        if reference in self.known_solutions:
            ref_length = self.known_solutions[reference](n)
            return tour_length / ref_length if ref_length > 0 else float('inf')
        else:
            raise ValueError(f"Unknown reference: {reference}")
    
    def benchmark_algorithm(self, algorithm: Callable, algorithm_name: str,
                           n_values: List[int] = [100, 250, 500, 1000],
                           instances_per_n: int = 5,
                           seeds: List[int] = None) -> Dict[str, Any]:
        """
        Benchmark an algorithm across different problem sizes.
        
        Args:
            algorithm: Function that takes (tsp_instance) and returns (tour, length)
            algorithm_name: Name of algorithm for reporting
            n_values: List of n values to test
            instances_per_n: Number of random instances per n
            seeds: Optional list of seeds (if None, generated)
            
        Returns:
            Dictionary with benchmark results
        """
        if seeds is None:
            seeds = list(range(instances_per_n * len(n_values)))
        
        results = {
            'algorithm': algorithm_name,
            'timestamp': datetime.now().isoformat(),
            'benchmark_version': '1.0',
            'runs': []
        }
        
        seed_idx = 0
        total_time = 0.0
        
        for n in n_values:
            print(f"\nBenchmarking n={n}:")
            
            for i in range(instances_per_n):
                if seed_idx >= len(seeds):
                    seed = random.randint(0, 1000000)
                else:
                    seed = seeds[seed_idx]
                
                # Generate instance
                tsp = self.generate_instance(n, seed)
                
                # Run algorithm
                start_time = time.time()
                try:
                    tour, tour_length = algorithm(tsp)
                    runtime = time.time() - start_time
                    
                    # Calculate metrics
                    approx_ratio = self.calculate_approximation_ratio(
                        tour_length, n, 'theoretical_lower_bound'
                    )
                    
                    # Store results
                    run_result = {
                        'n': n,
                        'instance_id': i,
                        'seed': seed,
                        'tour_length': float(tour_length),
                        'runtime': runtime,
                        'approximation_ratio': float(approx_ratio),
                        'theoretical_lower_bound': float(0.721 * math.sqrt(n)),
                        'tour_sample': tour[:10] if len(tour) > 10 else tour
                    }
                    results['runs'].append(run_result)
                    
                    total_time += runtime
                    
                    print(f"  Instance {i+1}: length={tour_length:.4f}, "
                          f"ratio={approx_ratio:.4f}, time={runtime:.3f}s")
                    
                except Exception as e:
                    print(f"  Instance {i+1}: ERROR - {e}")
                    run_result = {
                        'n': n,
                        'instance_id': i,
                        'seed': seed,
                        'error': str(e)
                    }
                    results['runs'].append(run_result)
                
                seed_idx += 1
        
        # Calculate summary statistics
        successful_runs = [r for r in results['runs'] if 'tour_length' in r]
        
        if successful_runs:
            # Group by n
            by_n = {}
            for run in successful_runs:
                n = run['n']
                if n not in by_n:
                    by_n[n] = []
                by_n[n].append(run)
            
            summary = {}
            for n, runs in by_n.items():
                lengths = [r['tour_length'] for r in runs]
                ratios = [r['approximation_ratio'] for r in runs]
                times = [r['runtime'] for r in runs]
                
                summary[n] = {
                    'avg_tour_length': float(np.mean(lengths)),
                    'std_tour_length': float(np.std(lengths)),
                    'avg_approximation_ratio': float(np.mean(ratios)),
                    'std_approximation_ratio': float(np.std(ratios)),
                    'min_approximation_ratio': float(np.min(ratios)),
                    'max_approximation_ratio': float(np.max(ratios)),
                    'avg_runtime': float(np.mean(times)),
                    'num_instances': len(runs)
                }
            
            results['summary'] = summary
            results['total_runtime'] = total_time
        
        return results
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save benchmark results to JSON and CSV."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tsp_benchmark_{results['algorithm']}_{timestamp}"
        
        # Save JSON
        json_path = self.output_dir / f"{filename}.json"
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save CSV summary
        if 'summary' in results:
            csv_path = self.output_dir / f"{filename}_summary.csv"
            with open(csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['n', 'avg_tour_length', 'std_tour_length',
                               'avg_approximation_ratio', 'std_approximation_ratio',
                               'min_approximation_ratio', 'max_approximation_ratio',
                               'avg_runtime', 'num_instances'])
                
                for n, stats in results['summary'].items():
                    writer.writerow([
                        n,
                        stats['avg_tour_length'],
                        stats['std_tour_length'],
                        stats['avg_approximation_ratio'],
                        stats['std_approximation_ratio'],
                        stats['min_approximation_ratio'],
                        stats['max_approximation_ratio'],
                        stats['avg_runtime'],
                        stats['num_instances']
                    ])
        
        print(f"\nResults saved to:")
        print(f"  JSON: {json_path}")
        if 'summary' in results:
            print(f"  CSV: {csv_path}")
        
        return json_path
    
    def load_results(self, filepath: str) -> Dict[str, Any]:
        """Load benchmark results from JSON file."""
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def compare_algorithms(self, result_files: List[str], output_file: str = None):
        """Compare multiple benchmark results."""
        comparisons = {}
        
        for filepath in result_files:
            results = self.load_results(filepath)
            algo_name = results['algorithm']
            comparisons[algo_name] = results['summary'] if 'summary' in results else {}
        
        # Generate comparison report
        if output_file is None:
            output_file = self.output_dir / f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(output_file, 'w') as f:
            f.write("TSP Algorithm Comparison Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            
            for algo_name, summary in comparisons.items():
                f.write(f"\n{algo_name}:\n")
                f.write("-" * 30 + "\n")
                
                if summary:
                    for n, stats in summary.items():
                        f.write(f"  n={n}:\n")
                        f.write(f"    Avg approximation ratio: {stats['avg_approximation_ratio']:.4f}\n")
                        f.write(f"    Range: [{stats['min_approximation_ratio']:.4f}, {stats['max_approximation_ratio']:.4f}]\n")
                        f.write(f"    Avg runtime: {stats['avg_runtime']:.3f}s\n")
                else:
                    f.write("  No summary data available\n")
        
        print(f"Comparison report saved to: {output_file}")
        return comparisons


# Algorithm wrappers for benchmarking
def nearest_neighbor_algorithm(tsp: EuclideanTSP) -> Tuple[List[int], float]:
    """Wrapper for nearest neighbor algorithm."""
    return tsp.nearest_neighbor_multistart(num_starts=10)


def greedy_algorithm(tsp: EuclideanTSP) -> Tuple[List[int], float]:
    """
    Greedy algorithm (nearest insertion).
    Alternative baseline to compare with nearest neighbor.
    """
    n = tsp.n
    # Start with a tour containing just city 0
    tour = [0]
    unvisited = set(range(1, n))
    
    while unvisited:
        best_city = None
        best_position = -1
        best_increase = float('inf')
        
        # For each unvisited city
        for city in unvisited:
            # Find best position to insert in current tour
            for i in range(len(tour)):
                j = (i + 1) % len(tour)
                # Cost increase = d(tour[i], city) + d(city, tour[j]) - d(tour[i], tour[j])
                increase = (tsp.distance(tour[i], city) + 
                          tsp.distance(city, tour[j]) - 
                          tsp.distance(tour[i], tour[j]))
                
                if increase < best_increase:
                    best_increase = increase
                    best_city = city
                    best_position = i + 1  # Insert after position i
        
        # Insert the best city
        tour.insert(best_position, best_city)
        unvisited.remove(best_city)
    
    # Calculate total distance
    total = 0.0
    for i in range(n):
        total += tsp.distance(tour[i], tour[(i + 1) % n])
    
    return tour, total


def random_tour_algorithm(tsp: EuclideanTSP) -> Tuple[List[int], float]:
    """Random tour (baseline for comparison)."""
    n = tsp.n
    tour = list(range(n))
    random.shuffle(tour)
    tour.append(tour[0])  # Return to start
    
    total = 0.0
    for i in range(n):
        total += tsp.distance(tour[i], tour[i + 1])
    
    return tour, total


if __name__ == "__main__":
    print("=" * 60)
    print("Evo TSP Benchmarking Framework")
    print("=" * 60)
    
    # Initialize benchmarker
    benchmark = TSPBenchmark()
    
    # Benchmark nearest neighbor
    print("\n1. Benchmarking Nearest Neighbor algorithm...")
    nn_results = benchmark.benchmark_algorithm(
        algorithm=nearest_neighbor_algorithm,
        algorithm_name="nearest_neighbor_10starts",
        n_values=[100, 250, 500],
        instances_per_n=3
    )
    
    nn_file = benchmark.save_results(nn_results, "nearest_neighbor_baseline")
    
    # Benchmark greedy algorithm
    print("\n2. Benchmarking Greedy (Nearest Insertion) algorithm...")
    greedy_results = benchmark.benchmark_algorithm(
        algorithm=greedy_algorithm,
        algorithm_name="greedy_insertion",
        n_values=[100, 250, 500],
        instances_per_n=3,
        seeds=[i for i in range(9)]  # Same seeds for fair comparison
    )
    
    greedy_file = benchmark.save_results(greedy_results, "greedy_insertion")
    
    # Benchmark random tours (baseline)
    print("\n3. Benchmarking Random Tours (baseline)...")
    random_results = benchmark.benchmark_algorithm(
        algorithm=random_tour_algorithm,
        algorithm_name="random_tour",
        n_values=[100, 250, 500],
        instances_per_n=3,
        seeds=[i for i in range(9)]
    )
    
    random_file = benchmark.save_results(random_results, "random_tour")
    
    # Compare algorithms
    print("\n4. Comparing algorithms...")
    comparisons = benchmark.compare_algorithms([nn_file, greedy_file, random_file])
    
    # Print summary
    print("\n5. Summary of approximation ratios (n=500):")
    for algo_name, summary in comparisons.items():
        if 500 in summary:
            stats = summary[500]
            print(f"  {algo_name}:")
            print(f"    Avg ratio: {stats['avg_approximation_ratio']:.4f}")
            print(f"    Best ratio: {stats['min_approximation_ratio']:.4f}")
            print(f"    Target: <1.15 (impressive), <1.10 (remarkable)")
            
            # Check against targets
            best_ratio = stats['min_approximation_ratio']
            if best_ratio < 1.10:
                print(f"    STATUS: REMARKABLE! (<1.10)")
            elif best_ratio < 1.15:
                print(f"    STATUS: IMPRESSIVE! (<1.15)")
            else:
                print(f"    STATUS: Needs improvement (>{best_ratio:.4f})")
            print()
    
    print("\n" + "=" * 60)
    print("Benchmarking complete! Next steps:")
    print("1. Research actual optimal solutions for benchmarks")
    print("2. Implement Christofides algorithm (1.5x guarantee)")
    print("3. Implement 2-opt local search improvement")
    print("4. Try more sophisticated algorithms (Lin-Kernighan, etc.)")
    print("=" * 60)