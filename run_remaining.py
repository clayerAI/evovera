#!/usr/bin/env python3
"""Run remaining TSPLIB instances."""

import sys
import os
import json
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from evaluate_v11_tsplib_complete_fixed_optimized import evaluate_instance

def main():
    # Remaining instances to evaluate
    instances = [
        ("lin318", "data/tsplib/lin318.tsp", 42029),
        ("pr439", "data/tsplib/pr439.tsp", 107217)
    ]
    
    print("=" * 80)
    print("RUNNING REMAINING TSPLIB INSTANCES")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    all_results = {}
    
    for instance_name, filepath, optimal in instances:
        print(f"\n{'='*80}")
        print(f"STARTING: {instance_name.upper()}")
        print(f"{'='*80}")
        
        start_time = time.time()
        results = evaluate_instance(instance_name, filepath, optimal, seeds=10)
        elapsed = time.time() - start_time
        
        all_results[instance_name] = results
        print(f"\nCompleted {instance_name} in {elapsed:.1f}s")
    
    # Save results
    output_file = "v11_tsplib_phase2_remaining_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n{'='*80}")
    print("REMAINING INSTANCES COMPLETED")
    print(f"Results saved to: {output_file}")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
