#!/usr/bin/env python3
"""
Complete TSPLIB Phase 2 evaluation for v11 algorithm with ALL required instances.
Based on Vera's notification: att532, a280, d198, lin318, pr439.
"""

import sys
import os
import time
import numpy as np
from pathlib import Path
import statistics
from typing import Dict, List, Tuple

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tsplib_parser import TSPLIBParser
from solutions.tsp_v19_optimized_fixed_v11_proper import ChristofidesHybridStructuralOptimizedV11 as V11Solver

# TSPLIB instances to evaluate (Vera's required set)
TSPLIB_INSTANCES = {
    "att532": {"file": "data/tsplib/att532.tsp", "optimal": 27686},  # ATT metric
    "a280": {"file": "data/tsplib/a280.tsp", "optimal": 2579},      # EUC_2D
    "d198": {"file": "data/tsplib/d198.tsp", "optimal": 15780},     # EUC_2D
    "lin318": {"file": "data/tsplib/lin318.tsp", "optimal": 42029}, # EUC_2D
    "pr439": {"file": "data/tsplib/pr439.tsp", "optimal": 107217},  # EUC_2D
}

# Number of seeds for statistical validation
N_SEEDS = 10

def validate_tour(tour: List[int], n: int) -> Tuple[bool, str]:
    """Validate TSP tour is Hamiltonian cycle."""
    if len(tour) != n + 1:
        return False, f"Tour length {len(tour)} != n+1 ({n+1})"
    if tour[0] != tour[-1]:
        return False, f"Tour doesn't return to start: {tour[0]} != {tour[-1]}"
    unique_nodes = set(tour[:-1])
    if len(unique_nodes) != n:
        return False, f"Tour doesn't visit all nodes: {len(unique_nodes)} unique != {n}"
    return True, "Valid Hamiltonian cycle"

def compute_tour_length(tour: List[int], distance_matrix: np.ndarray) -> float:
    """Compute total tour length from distance matrix."""
    total = 0.0
    for i in range(len(tour) - 1):
        total += distance_matrix[tour[i], tour[i+1]]
    return total

def evaluate_instance(instance_name: str, filepath: str, optimal: float, seeds: int = N_SEEDS) -> Dict:
    """Evaluate v11 on a TSPLIB instance with multiple seeds."""
    print(f"\n{'='*80}")
    print(f"Evaluating {instance_name} (optimal: {optimal:,})")
    print(f"{'='*80}")
    
    # Parse TSPLIB instance
    parser = TSPLIBParser(filepath)
    if not parser.parse():
        return {"error": f"Failed to parse {filepath}"}
    
    # Get distance matrix
    try:
        distance_matrix = parser.get_distance_matrix()
        n = parser.dimension
        print(f"✓ Loaded {instance_name}: {n} nodes, {parser.edge_weight_type} metric")
    except Exception as e:
        return {"error": f"Failed to get distance matrix: {e}"}
    
    # Run multiple seeds
    tour_lengths = []
    runtimes = []
    valid_tours = 0
    
    for seed in range(seeds):
        print(f"  Seed {seed+1}/{seeds}: ", end="", flush=True)
        
        start_time = time.time()
        try:
            # Initialize solver with distance matrix
            solver = V11Solver(distance_matrix=distance_matrix)
            
            # Run v11 algorithm
            tour, length, runtime = solver.solve()
            elapsed = time.time() - start_time
            
            # Validate tour
            is_valid, msg = validate_tour(tour, n)
            if not is_valid:
                print(f"INVALID: {msg}")
                continue
            
            # Store results
            tour_lengths.append(length)
            runtimes.append(elapsed)
            valid_tours += 1
            
            # Compute gap percentage
            gap_pct = ((length - optimal) / optimal) * 100
            
            print(f"length={length:,.0f} ({gap_pct:.2f}% gap), {elapsed:.2f}s")
            
        except Exception as e:
            print(f"ERROR: {e}")
            continue
    
    # Compute statistics
    if valid_tours == 0:
        return {"error": "No valid tours generated"}
    
    # Calculate average gap percentage
    avg_length = statistics.mean(tour_lengths)
    avg_gap_pct = ((avg_length - optimal) / optimal) * 100
    
    # Calculate standard deviation of gaps
    gap_pcts = [((length - optimal) / optimal) * 100 for length in tour_lengths]
    std_gap_pct = statistics.stdev(gap_pcts) if len(gap_pcts) > 1 else 0.0
    
    # Calculate average runtime
    avg_runtime = statistics.mean(runtimes)
    
    # Calculate success rate
    success_rate = (valid_tours / seeds) * 100
    
    # Statistical significance (t-test would require baseline comparison)
    # For now, just report confidence interval
    if len(gap_pcts) > 1:
        ci_margin = 1.96 * (std_gap_pct / np.sqrt(len(gap_pcts)))  # 95% CI
        ci_lower = avg_gap_pct - ci_margin
        ci_upper = avg_gap_pct + ci_margin
    else:
        ci_lower = ci_upper = avg_gap_pct
    
    results = {
        "instance": instance_name,
        "n_nodes": n,
        "optimal": optimal,
        "avg_length": avg_length,
        "avg_gap_pct": avg_gap_pct,
        "std_gap_pct": std_gap_pct,
        "avg_runtime": avg_runtime,
        "success_rate": success_rate,
        "valid_tours": valid_tours,
        "total_seeds": seeds,
        "ci_95_lower": ci_lower,
        "ci_95_upper": ci_upper,
        "gap_pcts": gap_pcts,
        "runtimes": runtimes,
    }
    
    print(f"\n  Summary: {avg_gap_pct:.2f}% gap (95% CI: [{ci_lower:.2f}, {ci_upper:.2f}]), {avg_runtime:.2f}s avg, {success_rate:.0f}% success")
    
    return results

def main():
    """Main evaluation function."""
    print("="*80)
    print("TSPLIB Phase 2 Complete Evaluation - v11 Algorithm")
    print("Required instances: att532, a280, d198, lin318, pr439")
    print(f"Seeds per instance: {N_SEEDS}")
    print("="*80)
    
    # Check all instance files exist
    missing_files = []
    for instance, info in TSPLIB_INSTANCES.items():
        if not os.path.exists(info["file"]):
            missing_files.append(info["file"])
    
    if missing_files:
        print(f"ERROR: Missing files: {missing_files}")
        print("Please download missing TSPLIB instances first.")
        return 1
    
    # Run evaluation for each instance
    all_results = {}
    
    for instance_name, info in TSPLIB_INSTANCES.items():
        results = evaluate_instance(instance_name, info["file"], info["optimal"], N_SEEDS)
        if "error" in results:
            print(f"ERROR evaluating {instance_name}: {results['error']}")
            continue
        
        all_results[instance_name] = results
    
    # Generate summary report
    print("\n" + "="*80)
    print("PHASE 2 COMPLETE RESULTS SUMMARY")
    print("="*80)
    
    # Table header
    print(f"{'Instance':<10} {'Nodes':<6} {'Optimal':<12} {'Avg Gap %':<12} {'Std Dev %':<12} {'Avg Time (s)':<14} {'Success %':<10}")
    print("-"*80)
    
    # Table rows
    for instance_name in TSPLIB_INSTANCES.keys():
        if instance_name in all_results:
            r = all_results[instance_name]
            print(f"{instance_name:<10} {r['n_nodes']:<6} {r['optimal']:<12,} {r['avg_gap_pct']:<12.2f} {r['std_gap_pct']:<12.2f} {r['avg_runtime']:<14.2f} {r['success_rate']:<10.0f}")
    
    # Overall statistics
    if all_results:
        avg_gap_all = statistics.mean([r["avg_gap_pct"] for r in all_results.values()])
        avg_time_all = statistics.mean([r["avg_runtime"] for r in all_results.values()])
        min_gap = min([r["avg_gap_pct"] for r in all_results.values()])
        max_gap = max([r["avg_gap_pct"] for r in all_results.values()])
        
        print("-"*80)
        print(f"{'OVERALL':<10} {'-':<6} {'-':<12} {avg_gap_all:<12.2f} {'-':<12} {avg_time_all:<14.2f} {'-':<10}")
        print(f"  Range: {min_gap:.2f}% to {max_gap:.2f}% gap")
    
    # Save results to file
    output_file = "evaluation_output_complete.txt"
    with open(output_file, "w") as f:
        f.write("TSPLIB Phase 2 Complete Evaluation Results\n")
        f.write("="*60 + "\n\n")
        
        for instance_name, results in all_results.items():
            f.write(f"Instance: {instance_name}\n")
            f.write(f"  Nodes: {results['n_nodes']}\n")
            f.write(f"  Optimal: {results['optimal']:,}\n")
            f.write(f"  Average Gap: {results['avg_gap_pct']:.2f}%\n")
            f.write(f"  Std Dev Gap: {results['std_gap_pct']:.2f}%\n")
            f.write(f"  95% CI: [{results['ci_95_lower']:.2f}%, {results['ci_95_upper']:.2f}%]\n")
            f.write(f"  Average Runtime: {results['avg_runtime']:.2f}s\n")
            f.write(f"  Success Rate: {results['success_rate']:.0f}%\n")
            f.write(f"  Individual Gaps: {', '.join([f'{g:.2f}%' for g in results['gap_pcts']])}\n")
            f.write("\n")
    
    print(f"\nResults saved to {output_file}")
    
    # Check against baseline (NN+2opt target: 17.69% gap)
    baseline_target = 17.69
    all_below_baseline = all(r["avg_gap_pct"] < baseline_target for r in all_results.values())
    
    if all_below_baseline:
        print(f"\n✅ SUCCESS: All instances beat NN+2opt baseline ({baseline_target}% gap)")
    else:
        print(f"\n⚠️  WARNING: Some instances above NN+2opt baseline ({baseline_target}% gap)")
        for instance_name, results in all_results.items():
            if results["avg_gap_pct"] >= baseline_target:
                print(f"  {instance_name}: {results['avg_gap_pct']:.2f}% gap (above baseline)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
