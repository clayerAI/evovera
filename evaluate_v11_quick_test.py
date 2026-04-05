#!/usr/bin/env python3
"""
Quick test of v11 on all required TSPLIB instances.
"""

import sys
import os
import time
import numpy as np

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

def validate_tour(tour: list, n: int) -> bool:
    """Simple tour validation."""
    return len(tour) == n + 1 and tour[0] == tour[-1] and len(set(tour[:-1])) == n

def main():
    print("Quick Test of v11 on TSPLIB Instances")
    print("="*60)
    
    results = {}
    
    for instance_name, info in TSPLIB_INSTANCES.items():
        print(f"\nTesting {instance_name}...")
        
        try:
            # Parse instance
            parser = TSPLIBParser(info["file"])
            if not parser.parse():
                print(f"  ✗ Failed to parse")
                continue
            
            # Get distance matrix
            distance_matrix = parser.get_distance_matrix()
            n = parser.dimension
            optimal = info["optimal"]
            
            print(f"  ✓ Loaded: {n} nodes, optimal={optimal:,}")
            
            # Run solver
            start_time = time.time()
            solver = V11Solver(distance_matrix=distance_matrix)
            tour, length, runtime = solver.solve()
            elapsed = time.time() - start_time
            
            # Validate
            if not validate_tour(tour, n):
                print(f"  ✗ Invalid tour")
                continue
            
            # Calculate gap
            gap_pct = ((length - optimal) / optimal) * 100
            
            print(f"  ✓ Result: {length:,.0f} ({gap_pct:.2f}% gap), {elapsed:.2f}s")
            
            results[instance_name] = {
                "n_nodes": n,
                "optimal": optimal,
                "length": length,
                "gap_pct": gap_pct,
                "runtime": elapsed,
                "valid": True
            }
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results[instance_name] = {"valid": False, "error": str(e)}
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    baseline = 17.69
    valid_results = {k: v for k, v in results.items() if v.get("valid", False)}
    
    if valid_results:
        print(f"{'Instance':<10} {'Nodes':<6} {'Gap %':<10} {'Time (s)':<10} {'Vs Baseline':<12}")
        print("-"*60)
        
        for instance_name, r in valid_results.items():
            vs_baseline = "BETTER" if r["gap_pct"] < baseline else "WORSE"
            print(f"{instance_name:<10} {r['n_nodes']:<6} {r['gap_pct']:<10.2f} {r['runtime']:<10.2f} {vs_baseline:<12}")
        
        # Overall
        avg_gap = np.mean([r["gap_pct"] for r in valid_results.values()])
        print(f"\nAverage gap: {avg_gap:.2f}% (baseline: {baseline}%)")
        
        if all(r["gap_pct"] < baseline for r in valid_results.values()):
            print(f"\n✅ ALL instances beat NN+2opt baseline ({baseline}% gap)")
        else:
            print(f"\n⚠️  Some instances above baseline ({baseline}% gap)")
    else:
        print("No valid results obtained")

if __name__ == "__main__":
    main()
