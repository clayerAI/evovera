#!/usr/bin/env python3
"""
Test original v19 baseline quality for comparison with optimized versions.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import random
import time
from typing import List, Tuple
import numpy as np

# Import original v19
from tsp_v19_christofides_hybrid_structural_corrected import ChristofidesHybridStructuralCorrected

def generate_random_points(n: int, seed: int = 42) -> List[Tuple[float, float]]:
    """Generate n random points in [0, 1000] x [0, 1000]."""
    random.seed(seed)
    return [(random.uniform(0, 1000), random.uniform(0, 1000)) for _ in range(n)]

def test_quality_baseline(n_values: List[int] = [10, 20, 30, 50], seeds: List[int] = [42, 123, 456, 789, 999]):
    """Test original v19 quality across different sizes and seeds."""
    results = {}
    
    for n in n_values:
        print(f"\n=== Testing n={n} ===")
        n_results = []
        
        for seed in seeds:
            points = generate_random_points(n, seed)
            
            # Run original v19
            solver = ChristofidesHybridStructuralCorrected(points=points, seed=seed)
            start_time = time.time()
            tour, length, runtime = solver.solve()
            elapsed = time.time() - start_time
            
            n_results.append({
                'seed': seed,
                'length': length,
                'time': elapsed,
                'runtime': runtime
            })
            
            print(f"  Seed {seed}: length={length:.2f}, time={elapsed:.3f}s, runtime={runtime:.3f}s")
        
        # Calculate statistics
        lengths = [r['length'] for r in n_results]
        avg_length = np.mean(lengths)
        std_length = np.std(lengths)
        
        results[n] = {
            'avg_length': avg_length,
            'std_length': std_length,
            'min_length': min(lengths),
            'max_length': max(lengths),
            'samples': n_results
        }
        
        print(f"  Summary: avg={avg_length:.2f} ± {std_length:.2f}, range=[{min(lengths):.2f}, {max(lengths):.2f}]")
    
    return results

if __name__ == "__main__":
    print("Testing original v19 baseline quality...")
    results = test_quality_baseline()
    
    # Save results for comparison
    import json
    with open('/workspace/evovera/solutions/v19_baseline_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nBaseline results saved to v19_baseline_results.json")
