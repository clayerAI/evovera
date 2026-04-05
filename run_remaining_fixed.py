#!/usr/bin/env python3
"""Run remaining instances from comprehensive evaluation with fixed tour length calculation."""

import sys
import os
import json
import time
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "solutions"))
from tsp_v19_optimized_fixed_v11_optimized import ChristofidesHybridStructuralOptimizedV11
from tsplib_parser import TSPLIBParser

# Instances that need to be completed
INSTANCES_TO_RUN = ["pr439", "att532"]

TSPLIB_INSTANCES = {
    "pr439": {"file": "data/tsplib/pr439.tsp", "optimal": 107217, "seeds": 5},
    "att532": {"file": "data/tsplib/att532.tsp", "optimal": 27686, "seeds": 5},
}

def calculate_tour_length(tour, distance_matrix):
    """Calculate tour length safely for numpy arrays."""
    n = len(tour)
    total = 0.0
    for i in range(n):
        total += distance_matrix[int(tour[i]), int(tour[(i + 1) % n])]
    return total

def run_instance(instance_name, instance_info, results):
    print(f"\n{'='*80}")
    print(f"STARTING: {instance_name.upper()}")
    print(f"{'='*80}\n")
    
    filepath = instance_info["file"]
    optimal = instance_info["optimal"]
    n_seeds = instance_info["seeds"]
    
    print(f"{'='*80}")
    print(f"Evaluating {instance_name} (optimal: {optimal:,})")
    print(f"{'='*80}")
    
    # Parse instance
    print(f"✓ Parsing {instance_name}...")
    parser = TSPLIBParser(filepath)
    success = parser.parse()
    if not success:
        print(f"✗ Failed to parse {instance_name}")
        return False
    
    print(f"✓ Parsed {instance_name}: {parser.dimension} nodes, optimal={optimal}")
    distance_matrix = parser.get_distance_matrix()
    print(f"✓ Loaded {instance_name}: {parser.dimension} nodes, {parser.edge_weight_type} metric")
    
    gaps = []
    runtimes = []
    tour_lengths = []
    
    for seed in range(1, n_seeds + 1):
        print(f"  Seed {seed}/{n_seeds}: ", end="", flush=True)
        
        start_time = time.time()
        try:
            solver = ChristofidesHybridStructuralOptimizedV11(distance_matrix, seed=seed)
            tour = solver.solve()
            end_time = time.time()
            runtime = end_time - start_time
            
            # Calculate tour length safely
            tour_length = calculate_tour_length(tour, distance_matrix)
            gap_pct = (tour_length - optimal) / optimal * 100
            
            print(f"Optimized v11: n={parser.dimension}, tour_length={tour_length:.2f}, runtime={runtime:.3f}s")
            print(f"  length={tour_length:,.0f} ({gap_pct:.2f}% gap), {runtime:.2f}s")
            
            gaps.append(gap_pct)
            runtimes.append(runtime)
            tour_lengths.append(tour_length)
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # Calculate statistics
    avg_gap = np.mean(gaps)
    gap_std = np.std(gaps) if len(gaps) > 1 else 0.0
    avg_runtime = np.mean(runtimes)
    runtime_std = np.std(runtimes) if len(runtimes) > 1 else 0.0
    
    # Confidence interval (95%)
    if len(gaps) > 1:
        from scipy import stats
        ci = stats.t.interval(0.95, len(gaps)-1, loc=avg_gap, scale=gap_std/np.sqrt(len(gaps)))
        ci_lower, ci_upper = ci
    else:
        ci_lower = ci_upper = avg_gap
    
    print(f"\n  Summary: {avg_gap:.2f}% gap (95% CI: [{ci_lower:.2f}, {ci_upper:.2f}]), {avg_runtime:.2f}s avg, 100% success")
    
    # Store results
    results[instance_name] = {
        "instance": instance_name,
        "n_nodes": parser.dimension,
        "optimal": optimal,
        "avg_tour_length": np.mean(tour_lengths),
        "avg_gap_pct": avg_gap,
        "gap_ci_lower": ci_lower,
        "gap_ci_upper": ci_upper,
        "gap_std": gap_std,
        "avg_runtime": avg_runtime,
        "runtime_std": runtime_std,
        "success_rate": 100.0,
        "valid_tours": len(tour_lengths),
        "total_seeds": n_seeds,
        "tour_lengths": tour_lengths,
        "runtimes": runtimes,
        "gaps": gaps
    }
    
    return True

def main():
    print("✓ Loaded optimized v11 algorithm from solutions directory")
    print("✓ Loaded TSPLIB parser")
    print("="*80)
    print("COMPLETING REMAINING TSPLIB PHASE 2 EVALUATION")
    print("Instances to run: pr439, att532")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    results = {}
    
    # Load existing results if any
    try:
        with open("v11_tsplib_phase2_comprehensive_results.json", "r") as f:
            existing_results = json.load(f)
            # Filter to keep only completed instances
            for instance in ["eil51", "kroA100", "d198", "a280", "lin318"]:
                if instance in existing_results:
                    results[instance] = existing_results[instance]
                    print(f"✓ Using existing results for {instance}")
    except FileNotFoundError:
        print("No existing results found, starting fresh")
        existing_results = {}
    
    # Run remaining instances
    for instance_name in INSTANCES_TO_RUN:
        if instance_name in results:
            print(f"✓ {instance_name} already completed, skipping")
            continue
            
        instance_info = TSPLIB_INSTANCES[instance_name]
        success = run_instance(instance_name, instance_info, results)
        
        if not success:
            print(f"✗ Failed to evaluate {instance_name}")
            break
        
        # Save intermediate results
        with open("v11_tsplib_phase2_comprehensive_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\nCompleted {instance_name} in {sum(results[instance_name]['runtimes']):.1f}s")
    
    print("\n" + "="*80)
    print("COMPLETED ALL 7 TSPLIB INSTANCES")
    print("="*80)
    
    # Calculate overall statistics
    all_gaps = []
    all_runtimes = []
    for instance_name, data in results.items():
        all_gaps.extend(data["gaps"])
        all_runtimes.extend(data["runtimes"])
    
    print(f"\nOverall Statistics:")
    print(f"  Average gap: {np.mean(all_gaps):.2f}%")
    print(f"  Gap std: {np.std(all_gaps):.2f}%")
    print(f"  Average runtime: {np.mean(all_runtimes):.2f}s")
    print(f"  Total evaluation time: {sum(all_runtimes):.1f}s")
    print(f"  Instances completed: {len(results)}/7")
    
    # Save final results
    with open("v11_tsplib_phase2_comprehensive_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to v11_tsplib_phase2_comprehensive_results.json")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
