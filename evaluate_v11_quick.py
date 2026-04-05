#!/usr/bin/env python3
"""
Quick TSPLIB evaluation for v11 algorithm.
Runs 3 seeds per instance for quick assessment.
"""

import sys
import os
import time
import numpy as np
from datetime import datetime
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tsplib_parser import TSPLIBParser
from solutions.tsp_v19_optimized_fixed_v11_proper import ChristofidesHybridStructuralOptimizedV11 as V11Solver

# Configuration
SEEDS = 3  # Quick assessment
INSTANCES = [
    ("eil51", "data/tsplib/eil51.tsp", 426),
    ("kroA100", "data/tsplib/kroA100.tsp", 21282),
    ("a280", "data/tsplib/a280.tsp", 2579),
]

def evaluate_instance(instance_name, filepath, optimal):
    """Evaluate instance with multiple seeds."""
    print(f"\n{'='*50}")
    print(f"Evaluating {instance_name} (optimal={optimal})")
    
    # Parse instance
    parser = TSPLIBParser(filepath)
    if not parser.parse():
        print(f"❌ Failed to parse {instance_name}")
        return None
    
    distance_matrix = parser.get_distance_matrix()
    n = distance_matrix.shape[0]
    print(f"n={n}")
    
    results = []
    
    for seed_idx in range(SEEDS):
        seed = 42 + seed_idx * 100
        print(f"  Seed {seed_idx+1}/{SEEDS}...", end=" ", flush=True)
        
        np.random.seed(seed)
        solver = V11Solver(distance_matrix=distance_matrix)
        
        start_time = time.time()
        try:
            tour, length, runtime = solver.solve()
            elapsed = time.time() - start_time
            
            # Validate
            if len(tour) == n + 1 and tour[0] == tour[-1]:
                unique = len(set(tour[:-1]))
                if unique == n:
                    gap = ((length - optimal) / optimal) * 100
                    print(f"✅ Gap={gap:.2f}%, Time={elapsed:.2f}s")
                    results.append({
                        "seed": seed,
                        "length": float(length),
                        "gap": float(gap),
                        "time": elapsed
                    })
                else:
                    print(f"❌ Invalid tour")
            else:
                print(f"❌ Invalid structure")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Summary
    if results:
        gaps = [r["gap"] for r in results]
        print(f"  Summary: Mean gap={np.mean(gaps):.2f}% ± {np.std(gaps):.2f}%")
        return {
            "instance": instance_name,
            "n": n,
            "optimal": optimal,
            "mean_gap": float(np.mean(gaps)),
            "std_gap": float(np.std(gaps)),
            "results": results
        }
    return None

def main():
    print("TSPLIB Phase 2: Quick v11 Evaluation")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Seeds per instance: {SEEDS}")
    
    all_results = {}
    
    for instance_name, filepath, optimal in INSTANCES:
        result = evaluate_instance(instance_name, filepath, optimal)
        if result:
            all_results[instance_name] = result
    
    # Final summary
    print("\n" + "="*50)
    print("FINAL RESULTS")
    print("="*50)
    
    for instance_name, result in all_results.items():
        print(f"{instance_name} (n={result['n']}):")
        print(f"  Gap: {result['mean_gap']:.2f}% ± {result['std_gap']:.2f}%")
        print(f"  Optimal: {result['optimal']}")
        
        # Compare to NN+2opt baseline (17.69% target)
        if result['mean_gap'] < 17.69:
            print(f"  ✅ BEATS baseline (17.69% target)")
        else:
            print(f"  ❌ Below baseline (17.69% target)")
    
    # Save results
    output_file = "reports/v11_quick_evaluation.json"
    with open(output_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": all_results,
            "baseline_target": 17.69
        }, f, indent=2)
    
    print(f"\n📁 Results saved to: {output_file}")

if __name__ == "__main__":
    main()
