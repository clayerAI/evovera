#!/usr/bin/env python3
"""
Comprehensive multi-seed benchmark for TSP algorithms.
Runs ≥10 seeds across multiple problem sizes with statistical analysis.
"""

import sys
import os
import time
import json
import random
from typing import Dict, List, Tuple, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import TSP algorithms
try:
    from tsp_algorithms import (
        solve_tsp_nn,  # v1: Nearest Neighbor
        solve_tsp_nn_2opt,  # v2: NN + 2-opt (baseline)
        solve_tsp_christofides,  # v3: Christofides
        solve_tsp_christofides_ils,  # v8: Christofides-ILS hybrid
        solve_tsp_christofides_structural_ils,  # v19: Christofides Structural-ILS hybrid
    )
    print("✓ Successfully imported TSP algorithms")
except ImportError as e:
    print(f"✗ Error importing TSP algorithms: {e}")
    print("Make sure tsp_algorithms.py is in the same directory")
    sys.exit(1)

# Import statistical tests
try:
    from statistical_tests import statistical_summary, format_statistical_report, mean, std, confidence_interval
    print("✓ Successfully imported statistical tests")
except ImportError as e:
    print(f"✗ Error importing statistical tests: {e}")
    print("Make sure statistical_tests.py is in the same directory")
    sys.exit(1)

def generate_random_tsp_instance(n: int, seed: int) -> List[Tuple[float, float]]:
    """Generate random TSP instance with given seed."""
    random.seed(seed)
    return [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(n)]

def run_benchmark(algorithm, cities: List[Tuple[float, float]], algorithm_name: str) -> Tuple[float, float]:
    """Run single benchmark and return tour length and runtime."""
    start_time = time.time()
    try:
        tour = algorithm(cities)
        end_time = time.time()
        
        # Calculate tour length
        total_distance = 0.0
        for i in range(len(tour)):
            x1, y1 = cities[tour[i]]
            x2, y2 = cities[tour[(i + 1) % len(tour)]]
            total_distance += ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        
        runtime = end_time - start_time
        return total_distance, runtime
        
    except Exception as e:
        print(f"✗ Error running {algorithm_name}: {e}")
        return float('inf'), float('inf')

def run_multi_seed_benchmark(algorithm, algorithm_name: str, n: int, num_seeds: int = 10) -> Dict[str, Any]:
    """Run benchmark with multiple seeds and collect statistics."""
    print(f"\n{'='*60}")
    print(f"Benchmarking {algorithm_name} (n={n}, seeds={num_seeds})")
    print(f"{'='*60}")
    
    distances = []
    runtimes = []
    
    for seed in range(num_seeds):
        print(f"  Seed {seed+1}/{num_seeds}...", end=" ", flush=True)
        cities = generate_random_tsp_instance(n, seed)
        distance, runtime = run_benchmark(algorithm, cities, algorithm_name)
        
        if distance < float('inf'):
            distances.append(distance)
            runtimes.append(runtime)
            print(f"✓ Distance: {distance:.3f}, Time: {runtime:.3f}s")
        else:
            print(f"✗ Failed")
    
    if not distances:
        return {"valid": False, "error": "All runs failed"}
    
    # Calculate statistics
    return {
        "valid": True,
        "algorithm": algorithm_name,
        "n": n,
        "num_seeds": num_seeds,
        "distances_mean": mean(distances),
        "distances_std": std(distances),
        "distances_ci": confidence_interval(distances),
        "runtimes_mean": mean(runtimes),
        "runtimes_std": std(runtimes),
        "runtimes_ci": confidence_interval(runtimes),
        "distances_raw": distances,
        "runtimes_raw": runtimes,
    }

def compare_algorithms(baseline_results: Dict[str, Any], treatment_results: Dict[str, Any]) -> Dict[str, Any]:
    """Compare two algorithms statistically."""
    if not baseline_results["valid"] or not treatment_results["valid"]:
        return {"valid": False, "error": "Invalid results"}
    
    baseline_name = baseline_results["algorithm"]
    treatment_name = treatment_results["algorithm"]
    
    # Statistical comparison
    stats = statistical_summary(
        baseline_results["distances_raw"],
        treatment_results["distances_raw"],
        f"{treatment_name} vs {baseline_name} (n={baseline_results['n']})"
    )
    
    # Add runtime comparison
    runtime_improvement = ((baseline_results["runtimes_mean"] - treatment_results["runtimes_mean"]) / 
                          baseline_results["runtimes_mean"]) * 100.0
    
    stats["runtime_baseline"] = baseline_results["runtimes_mean"]
    stats["runtime_treatment"] = treatment_results["runtimes_mean"]
    stats["runtime_improvement_percent"] = runtime_improvement
    
    return stats

def save_results(results: Dict[str, Any], filename: str):
    """Save benchmark results to JSON file."""
    # Convert to serializable format
    serializable = {}
    for key, value in results.items():
        if key.endswith("_raw"):
            # Keep raw data
            serializable[key] = value
        elif isinstance(value, (int, float, str, bool, type(None))):
            serializable[key] = value
        elif isinstance(value, tuple):
            serializable[key] = list(value)
        elif isinstance(value, dict):
            # Recursively process dict
            serializable[key] = {k: v for k, v in value.items() 
                               if isinstance(v, (int, float, str, bool, type(None), list, tuple))}
        else:
            # Skip complex objects
            serializable[key] = str(value)
    
    with open(filename, 'w') as f:
        json.dump(serializable, f, indent=2)
    
    print(f"✓ Results saved to {filename}")

def main():
    """Main benchmark execution."""
    print("=" * 80)
    print("COMPREHENSIVE MULTI-SEED TSP BENCHMARK")
    print("Methodological Correction - Phase 1")
    print("=" * 80)
    
    # Configuration
    problem_sizes = [50, 100, 200]  # Start with smaller sizes for testing
    num_seeds = 10  # Minimum 10 seeds for statistical validity
    
    # Algorithms to benchmark
    algorithms = {
        "v1_nn": solve_tsp_nn,
        "v2_nn_2opt": solve_tsp_nn_2opt,  # Baseline
        "v3_christofides": solve_tsp_christofides,
        "v8_christofides_ils": solve_tsp_christofides_ils,
        "v19_christofides_structural_ils": solve_tsp_christofides_structural_ils,
    }
    
    # Results storage
    all_results = {}
    comparisons = {}
    
    # Create output directory
    output_dir = "benchmark_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Run benchmarks
    for n in problem_sizes:
        print(f"\n{'#'*80}")
        print(f"PROBLEM SIZE: n = {n}")
        print(f"{'#'*80}")
        
        size_results = {}
        
        for algo_name, algo_func in algorithms.items():
            result = run_multi_seed_benchmark(algo_func, algo_name, n, num_seeds)
            size_results[algo_name] = result
            
            # Save individual results
            if result["valid"]:
                filename = f"{output_dir}/{algo_name}_n{n}_seeds{num_seeds}.json"
                save_results(result, filename)
        
        all_results[n] = size_results
        
        # Compare against baseline (v2_nn_2opt)
        baseline = size_results.get("v2_nn_2opt")
        if baseline and baseline["valid"]:
            for algo_name, result in size_results.items():
                if algo_name != "v2_nn_2opt" and result["valid"]:
                    comparison = compare_algorithms(baseline, result)
                    if comparison["valid"]:
                        key = f"{algo_name}_vs_baseline_n{n}"
                        comparisons[key] = comparison
                        
                        # Print comparison report
                        report = format_statistical_report(comparison)
                        print(f"\n{report}")
                        
                        # Save comparison
                        filename = f"{output_dir}/comparison_{key}.json"
                        save_results(comparison, filename)
    
    # Generate summary report
    print(f"\n{'='*80}")
    print("BENCHMARK SUMMARY")
    print(f"{'='*80}")
    
    summary_file = f"{output_dir}/benchmark_summary.md"
    with open(summary_file, 'w') as f:
        f.write("# Comprehensive Multi-Seed Benchmark Results\n\n")
        f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Seeds per test:** {num_seeds}\n")
        f.write(f"**Problem sizes:** {problem_sizes}\n\n")
        
        f.write("## Key Findings\n\n")
        
        # Analyze each comparison
        for key, comparison in comparisons.items():
            if not comparison["valid"]:
                continue
            
            algo_name = key.split("_vs_")[0]
            n = int(key.split("_n")[1]) if "_n" in key else "unknown"
            
            improvement = comparison["improvement_percent"]
            p_value = comparison["t_test"]["p_value"]
            
            f.write(f"### {algo_name} (n={n})\n")
            f.write(f"- **Improvement vs NN+2opt:** {improvement:.2f}%\n")
            f.write(f"- **Statistical significance:** p = {p_value:.3f}\n")
            
            if p_value < 0.05 and improvement > 0:
                f.write(f"- **Conclusion:** ✅ Statistically significant improvement\n")
            elif p_value < 0.05 and improvement < 0:
                f.write(f"- **Conclusion:** ⚠️ Statistically significant degradation\n")
            elif improvement > 2.0:
                f.write(f"- **Conclusion:** 📊 Practically meaningful improvement (>2%)\n")
            elif improvement < -2.0:
                f.write(f"- **Conclusion:** ⚠️ Practically meaningful degradation (>2%)\n")
            else:
                f.write(f"- **Conclusion:** 📈 Minor difference (<2%)\n")
            
            f.write(f"- **Runtime:** {comparison['runtime_treatment']:.3f}s vs baseline {comparison['runtime_baseline']:.3f}s\n")
            f.write(f"- **Runtime change:** {comparison['runtime_improvement_percent']:.1f}%\n\n")
    
    print(f"✓ Summary report saved to {summary_file}")
    
    # Save all results
    master_file = f"{output_dir}/all_benchmark_results.json"
    save_results({"all_results": all_results, "comparisons": comparisons}, master_file)
    
    print(f"\n{'='*80}")
    print("BENCHMARK COMPLETE")
    print(f"{'='*80}")
    print(f"✓ {len(problem_sizes)} problem sizes benchmarked")
    print(f"✓ {num_seeds} seeds per algorithm per size")
    print(f"✓ {len(algorithms)} algorithms tested")
    print(f"✓ Results saved to {output_dir}/")
    print(f"✓ Statistical analysis completed")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
