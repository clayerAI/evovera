#!/usr/bin/env python3
"""Run full TSPLIB Phase 2 evaluation on all 5 required instances."""

import sys
import os
import json
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from evaluate_v11_tsplib_complete_fixed_optimized import evaluate_instance, TSPLIB_INSTANCES

def main():
    print("=" * 80)
    print("FULL TSPLIB PHASE 2 EVALUATION - OPTIMIZED V11 ALGORITHM")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    all_results = {}
    total_start = time.time()
    
    # Run evaluation for each instance
    for instance_name, config in TSPLIB_INSTANCES.items():
        print(f"\n{'='*80}")
        print(f"STARTING: {instance_name.upper()}")
        print(f"{'='*80}")
        
        instance_start = time.time()
        results = evaluate_instance(
            instance_name, 
            config["file"], 
            config["optimal"],
            seeds=10
        )
        instance_time = time.time() - instance_start
        
        all_results[instance_name] = results
        all_results[instance_name]["evaluation_time"] = instance_time
        
        print(f"\nCompleted {instance_name} in {instance_time:.1f}s")
    
    total_time = time.time() - total_start
    
    # Save results
    output_file = "v11_tsplib_phase2_complete_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    # Generate summary
    print(f"\n{'='*80}")
    print("EVALUATION COMPLETE - SUMMARY")
    print(f"{'='*80}")
    print(f"Total evaluation time: {total_time:.1f}s")
    print(f"Results saved to: {output_file}")
    
    print("\nInstance Performance Summary:")
    print("-" * 80)
    print(f"{'Instance':<10} {'Nodes':<6} {'Avg Gap %':<12} {'Avg Time (s)':<15} {'Success %':<10}")
    print("-" * 80)
    
    for instance_name, results in all_results.items():
        if "error" in results:
            print(f"{instance_name:<10} {'N/A':<6} {'ERROR':<12} {'N/A':<15} {'0%':<10}")
            print(f"  Error: {results['error']}")
        else:
            print(f"{instance_name:<10} {results.get('n_nodes', 'N/A'):<6} "
                  f"{results.get('avg_gap_pct', 0):.2f}%{'':<5} "
                  f"{results.get('avg_runtime', 0):.2f}{'':<8} "
                  f"{results.get('success_rate', 0):.0f}%")
    
    print(f"\n{'='*80}")
    print("FULL EVALUATION COMPLETED")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
