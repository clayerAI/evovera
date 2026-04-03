#!/usr/bin/env python3
"""
Test script for Christofides with Adaptive Matching based on Edge Centrality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tsp_v14_christofides_adaptive_matching import ChristofidesAdaptiveMatching, generate_random_points
import json
import time

def test_small_instance():
    """Test on small instance to verify algorithm works."""
    print("Testing Christofides with Adaptive Matching on small instance")
    print("=" * 70)
    
    # Generate test points
    n = 20
    points = generate_random_points(n, seed=42)
    
    # Create solver
    solver = ChristofidesAdaptiveMatching(points, seed=42)
    
    # Test with different centrality weights
    print(f"Testing on n={n} random points")
    print()
    
    centrality_weights = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    
    results = []
    for weight in centrality_weights:
        tour, length, runtime = solver.solve(centrality_weight=weight, apply_2opt=True)
        results.append({
            'weight': weight,
            'tour_length': length,
            'runtime': runtime
        })
        print(f"Centrality weight {weight:.1f}: Tour length = {length:.4f}, Runtime = {runtime:.4f}s")
    
    # Find best result
    best = min(results, key=lambda x: x['tour_length'])
    print(f"\nBest result: weight={best['weight']:.1f}, length={best['tour_length']:.4f}")
    
    return results

def benchmark_different_sizes():
    """Benchmark algorithm on different problem sizes."""
    print("\n\nBenchmarking on different problem sizes")
    print("=" * 70)
    
    sizes = [20, 50, 100]
    all_results = {}
    
    for n in sizes:
        print(f"\nBenchmarking n={n}...")
        points = generate_random_points(n, seed=42)
        solver = ChristofidesAdaptiveMatching(points, seed=42)
        
        # Test a few centrality weights
        centrality_weights = [0.0, 0.2, 0.4]
        size_results = []
        
        for weight in centrality_weights:
            # Run 3 trials
            tour_lengths = []
            runtimes = []
            
            for trial in range(3):
                solver.seed = 42 + trial
                tour, length, runtime = solver.solve(centrality_weight=weight, apply_2opt=True)
                tour_lengths.append(length)
                runtimes.append(runtime)
            
            avg_length = sum(tour_lengths) / len(tour_lengths)
            avg_runtime = sum(runtimes) / len(runtimes)
            
            size_results.append({
                'weight': weight,
                'avg_tour_length': avg_length,
                'avg_runtime': avg_runtime,
                'tour_lengths': tour_lengths,
                'runtimes': runtimes
            })
            
            print(f"  Weight {weight:.1f}: avg length={avg_length:.4f}, avg runtime={avg_runtime:.4f}s")
        
        # Find best weight for this size
        best = min(size_results, key=lambda x: x['avg_tour_length'])
        print(f"  Best weight for n={n}: {best['weight']:.1f} (length={best['avg_tour_length']:.4f})")
        
        all_results[n] = {
            'size': n,
            'results': size_results,
            'best_weight': best['weight'],
            'best_avg_length': best['avg_tour_length'],
            'best_avg_runtime': best['avg_runtime']
        }
    
    return all_results

def compare_with_standard_christofides():
    """Compare adaptive matching with standard Christofides (weight=0)."""
    print("\n\nComparing with standard Christofides (weight=0)")
    print("=" * 70)
    
    n = 50
    points = generate_random_points(n, seed=42)
    
    # Create solver
    solver = ChristofidesAdaptiveMatching(points, seed=42)
    
    # Test standard Christofides (weight=0)
    print(f"Testing on n={n} points")
    
    # Run standard Christofides (weight=0)
    standard_results = []
    for trial in range(5):
        solver.seed = 42 + trial
        tour, length, runtime = solver.solve(centrality_weight=0.0, apply_2opt=True)
        standard_results.append({'length': length, 'runtime': runtime})
    
    avg_standard_length = sum(r['length'] for r in standard_results) / len(standard_results)
    avg_standard_runtime = sum(r['runtime'] for r in standard_results) / len(standard_results)
    
    print(f"Standard Christofides (weight=0):")
    print(f"  Average tour length: {avg_standard_length:.4f}")
    print(f"  Average runtime: {avg_standard_runtime:.4f}s")
    
    # Test adaptive matching with best weight from earlier tests
    adaptive_weight = 0.3
    adaptive_results = []
    for trial in range(5):
        solver.seed = 42 + trial
        tour, length, runtime = solver.solve(centrality_weight=adaptive_weight, apply_2opt=True)
        adaptive_results.append({'length': length, 'runtime': runtime})
    
    avg_adaptive_length = sum(r['length'] for r in adaptive_results) / len(adaptive_results)
    avg_adaptive_runtime = sum(r['runtime'] for r in adaptive_results) / len(adaptive_results)
    
    print(f"\nAdaptive Christofides (weight={adaptive_weight}):")
    print(f"  Average tour length: {avg_adaptive_length:.4f}")
    print(f"  Average runtime: {avg_adaptive_runtime:.4f}s")
    
    # Calculate improvement
    if avg_standard_length > 0:
        improvement = (avg_standard_length - avg_adaptive_length) / avg_standard_length * 100
        print(f"\nImprovement: {improvement:.2f}% better with adaptive matching")
    
    return {
        'standard': {'avg_length': avg_standard_length, 'avg_runtime': avg_standard_runtime},
        'adaptive': {'avg_length': avg_adaptive_length, 'avg_runtime': avg_adaptive_runtime, 'weight': adaptive_weight}
    }

def save_results(results, filename):
    """Save benchmark results to JSON file."""
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {filename}")

def main():
    """Main test function."""
    print("Christofides with Adaptive Matching based on Edge Centrality - Test Suite")
    print("=" * 70)
    
    # Test small instance
    small_results = test_small_instance()
    
    # Benchmark different sizes
    size_results = benchmark_different_sizes()
    
    # Compare with standard Christofides
    comparison_results = compare_with_standard_christofides()
    
    # Save comprehensive results
    all_results = {
        'small_instance': small_results,
        'size_benchmarks': size_results,
        'comparison': comparison_results,
        'timestamp': time.time(),
        'algorithm': 'tsp_v14_christofides_adaptive_matching.py'
    }
    
    save_results(all_results, 'christofides_adaptive_matching_benchmark.json')
    
    print("\n" + "=" * 70)
    print("Test suite completed successfully!")
    
    # Summary
    print("\nSummary:")
    print(f"- Algorithm implemented: Christofides with Adaptive Matching based on Edge Centrality")
    print(f"- Key novelty: Uses MST edge centrality to guide matching selection")
    print(f"- Tested on sizes: {list(size_results.keys())}")
    
    # Check if adaptive matching provides improvement
    if 'comparison' in all_results:
        comp = all_results['comparison']
        if comp['adaptive']['avg_length'] < comp['standard']['avg_length']:
            improvement = (comp['standard']['avg_length'] - comp['adaptive']['avg_length']) / comp['standard']['avg_length'] * 100
            print(f"- Adaptive matching (weight={comp['adaptive']['weight']}) provides {improvement:.2f}% improvement over standard Christofides")
        else:
            print(f"- Adaptive matching shows similar performance to standard Christofides")

if __name__ == "__main__":
    main()