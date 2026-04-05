#!/usr/bin/env python3
"""Execute comprehensive Phase 2 evaluation per Vera's coordination signal."""

import sys
import os
import json
import time
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the optimized v11 algorithm from solutions directory
try:
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "solutions"))
    from tsp_v19_optimized_fixed_v11_optimized import ChristofidesHybridStructuralOptimizedV11
    print("✓ Loaded optimized v11 algorithm from solutions directory")
except ImportError as e:
    print(f"ERROR: Could not import optimized v11 algorithm: {e}")
    sys.exit(1)

# Import TSPLIB parser
try:
    from tsplib_parser import parse_tsplib_file, compute_distance_matrix
except ImportError:
    print("ERROR: Could not import TSPLIB parser")
    sys.exit(1)

# TSPLIB instances with optimal values (from tsplib_parser.py)
TSPLIB_INSTANCES = {
    "eil51": {"file": "data/tsplib/eil51.tsp", "optimal": 426, "seeds": 10},      # ≤200 nodes: 10 seeds
    "kroA100": {"file": "data/tsplib/kroA100.tsp", "optimal": 21282, "seeds": 10}, # ≤200 nodes: 10 seeds
    "d198": {"file": "data/tsplib/d198.tsp", "optimal": 15780, "seeds": 10},       # ≤200 nodes: 10 seeds
    "a280": {"file": "data/tsplib/a280.tsp", "optimal": 2579, "seeds": 5},         # >200 nodes: 5 seeds
    "lin318": {"file": "data/tsplib/lin318.tsp", "optimal": 42029, "seeds": 5},    # >200 nodes: 5 seeds
    "pr439": {"file": "data/tsplib/pr439.tsp", "optimal": 107217, "seeds": 5},     # >200 nodes: 5 seeds
    "att532": {"file": "data/tsplib/att532.tsp", "optimal": 27686, "seeds": 5},    # >200 nodes: 5 seeds
}

# Timeout settings (300s for att532 as per Vera's signal)
TIMEOUTS = {
    "att532": 300,
    "default": 180  # 3 minutes for other instances
}

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

def evaluate_instance(instance_name: str, file_path: str, optimal: int, seeds: int = 10) -> Dict[str, Any]:
    """Evaluate optimized v11 on a TSPLIB instance."""
    print(f"\n{'='*80}")
    print(f"Evaluating {instance_name} (optimal: {optimal:,})")
    print(f"{'='*80}")
    
    # Parse instance
    print(f"✓ Parsing {instance_name}...")
    try:
        nodes = parse_tsplib_file(file_path)
        n = len(nodes)
        print(f"✓ Loaded {instance_name}: {n} nodes")
    except Exception as e:
        return {"error": f"Failed to parse {instance_name}: {str(e)}"}
    
    # Compute distance matrix
    print(f"✓ Computing distance matrix...")
    try:
        distance_matrix = compute_distance_matrix(nodes)
    except Exception as e:
        return {"error": f"Failed to compute distance matrix: {str(e)}"}
    
    # Run evaluation for each seed
    tour_lengths = []
    runtimes = []
    gaps = []
    valid_tours = 0
    
    timeout = TIMEOUTS.get(instance_name, TIMEOUTS["default"])
    
    for seed in range(1, seeds + 1):
        print(f"  Seed {seed}/{seeds}: ", end="", flush=True)
        
        start_time = time.time()
        try:
            # Create solver instance with seed
            solver = ChristofidesHybridStructuralOptimizedV11(distance_matrix, seed=seed)
            
            # Run optimized v11 algorithm
            tour, tour_length = solver.solve()
            
            runtime = time.time() - start_time
            
            # Validate tour
            is_valid, validation_msg = validate_tour(tour, n)
            if not is_valid:
                print(f"INVALID TOUR: {validation_msg}")
                continue
            
            # Compute gap to optimal
            gap_pct = ((tour_length - optimal) / optimal) * 100
            
            tour_lengths.append(tour_length)
            runtimes.append(runtime)
            gaps.append(gap_pct)
            valid_tours += 1
            
            print(f"Optimized v11: n={n}, tour_length={tour_length:.2f}, runtime={runtime:.3f}s")
            print(f"  length={tour_length:,.0f} ({gap_pct:.2f}% gap), {runtime:.2f}s")
            
            # Check timeout
            if runtime > timeout:
                print(f"  WARNING: Exceeded timeout of {timeout}s")
            
        except Exception as e:
            runtime = time.time() - start_time
            print(f"ERROR: {str(e)}")
            if runtime > timeout:
                print(f"  TIMEOUT: Exceeded {timeout}s")
    
    # Compute statistics
    if valid_tours == 0:
        return {"error": f"No valid tours generated for {instance_name}"}
    
    avg_gap = np.mean(gaps)
    avg_runtime = np.mean(runtimes)
    success_rate = (valid_tours / seeds) * 100
    
    # Compute 95% confidence interval for gap
    if len(gaps) > 1:
        gap_std = np.std(gaps, ddof=1)
        gap_ci = 1.96 * gap_std / np.sqrt(len(gaps))
        ci_lower = avg_gap - gap_ci
        ci_upper = avg_gap + gap_ci
    else:
        ci_lower = ci_upper = avg_gap
    
    print(f"\n  Summary: {avg_gap:.2f}% gap (95% CI: [{ci_lower:.2f}, {ci_upper:.2f}]), "
          f"{avg_runtime:.2f}s avg, {success_rate:.0f}% success")
    
    return {
        "instance": instance_name,
        "n_nodes": n,
        "optimal": optimal,
        "avg_tour_length": float(np.mean(tour_lengths)),
        "avg_gap_pct": float(avg_gap),
        "gap_ci_lower": float(ci_lower),
        "gap_ci_upper": float(ci_upper),
        "gap_std": float(np.std(gaps, ddof=1)) if len(gaps) > 1 else 0.0,
        "avg_runtime": float(avg_runtime),
        "runtime_std": float(np.std(runtimes, ddof=1)) if len(runtimes) > 1 else 0.0,
        "success_rate": float(success_rate),
        "valid_tours": valid_tours,
        "total_seeds": seeds,
        "tour_lengths": [float(tl) for tl in tour_lengths],
        "runtimes": [float(rt) for rt in runtimes],
        "gaps": [float(g) for g in gaps]
    }

def main():
    print("=" * 80)
    print("COMPREHENSIVE TSPLIB PHASE 2 EVALUATION - OPTIMIZED V11 ALGORITHM")
    print("Per Vera's Coordination Signal: All 7 instances, proper seed counts")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    all_results = {}
    total_start = time.time()
    
    # Run evaluation for each instance in order of increasing size
    instance_order = ["eil51", "kroA100", "d198", "a280", "lin318", "pr439", "att532"]
    
    for instance_name in instance_order:
        if instance_name not in TSPLIB_INSTANCES:
            print(f"\nERROR: Instance {instance_name} not found in TSPLIB_INSTANCES")
            continue
            
        config = TSPLIB_INSTANCES[instance_name]
        
        print(f"\n{'='*80}")
        print(f"STARTING: {instance_name.upper()}")
        print(f"{'='*80}")
        
        instance_start = time.time()
        results = evaluate_instance(
            instance_name, 
            config["file"], 
            config["optimal"],
            seeds=config["seeds"]
        )
        instance_time = time.time() - instance_start
        
        all_results[instance_name] = results
        all_results[instance_name]["evaluation_time"] = instance_time
        
        print(f"\nCompleted {instance_name} in {instance_time:.1f}s")
    
    total_time = time.time() - total_start
    
    # Save results
    output_file = "v11_tsplib_phase2_comprehensive_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    # Generate summary
    print(f"\n{'='*80}")
    print("COMPREHENSIVE EVALUATION COMPLETE - SUMMARY")
    print(f"{'='*80}")
    print(f"Total evaluation time: {total_time:.1f}s")
    print(f"Results saved to: {output_file}")
    
    print("\nInstance Performance Summary:")
    print("-" * 100)
    print(f"{'Instance':<10} {'Nodes':<6} {'Seeds':<6} {'Avg Gap %':<12} {'Avg Time (s)':<15} {'Success %':<10} {'Timeout'}")
    print("-" * 100)
    
    for instance_name in instance_order:
        if instance_name not in all_results:
            continue
            
        results = all_results[instance_name]
        if "error" in results:
            print(f"{instance_name:<10} {'N/A':<6} {'N/A':<6} {'ERROR':<12} {'N/A':<15} {'0%':<10} {'N/A'}")
            print(f"  Error: {results['error']}")
        else:
            timeout = TIMEOUTS.get(instance_name, TIMEOUTS["default"])
            timeout_warning = "✓" if results["avg_runtime"] < timeout else "⏰"
            print(f"{instance_name:<10} {results.get('n_nodes', 'N/A'):<6} "
                  f"{results.get('total_seeds', 0):<6} "
                  f"{results.get('avg_gap_pct', 0):.2f}%{'':<5} "
                  f"{results.get('avg_runtime', 0):.2f}{'':<8} "
                  f"{results.get('success_rate', 0):.0f}%{'':<5} "
                  f"{timeout_warning}")
    
    print(f"\n{'='*80}")
    print("COMPREHENSIVE PHASE 2 EVALUATION COMPLETED")
    print(f"{'='*80}")
    
    # Generate comparison with NN+2opt baseline (17.69% target gap)
    print("\nComparison with NN+2opt Baseline (17.69% target gap):")
    print("-" * 80)
    baseline_gap = 17.69
    improvements = []
    
    for instance_name in instance_order:
        if instance_name in all_results and "error" not in all_results[instance_name]:
            gap = all_results[instance_name]["avg_gap_pct"]
            improvement = baseline_gap - gap
            improvements.append(improvement)
            better = "✓" if gap < baseline_gap else "✗"
            print(f"{instance_name:<10}: {gap:.2f}% gap vs {baseline_gap:.2f}% baseline "
                  f"({improvement:+.2f}% improvement) {better}")
    
    if improvements:
        avg_improvement = np.mean(improvements)
        print(f"\nAverage improvement over baseline: {avg_improvement:+.2f}%")
        print(f"All instances beat baseline: {'✓' if all(g < baseline_gap for g in improvements) else '✗'}")
    
    return all_results

if __name__ == "__main__":
    results = main()
