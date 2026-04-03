#!/usr/bin/env python3
"""
Minimal benchmark for v14 - just verify the key improvement claim
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from solutions.tsp_v14_christofides_adaptive_matching import ChristofidesAdaptiveMatching
import json
import time
import random

def generate_random_points(n, seed=42):
    """Generate n random points in unit square."""
    random.seed(seed)
    return [(random.random(), random.random()) for _ in range(n)]

def run_minimal_benchmark():
    """Run minimal benchmark with single instance."""
    print("MINIMAL BENCHMARK: v14 Christofides Adaptive Matching")
    print("Verifying key improvement claim")
    print("=" * 70)
    
    size = 500
    weights_to_test = [0.0, 0.3]  # Baseline vs optimal from claim
    seed = 42
    
    print(f"Testing {size}-node instance with seed {seed}")
    print(f"Weights: {weights_to_test}")
    print("-" * 50)
    
    # Generate points
    points = generate_random_points(size, seed=seed)
    
    results = {}
    
    for weight in weights_to_test:
        print(f"\nTesting weight={weight}...")
        start_time = time.time()
        
        solver = ChristofidesAdaptiveMatching(points, seed=seed)
        tour, length, runtime = solver.solve(centrality_weight=weight, apply_2opt=True)
        
        total_time = time.time() - start_time
        
        results[weight] = {
            'tour_length': length,
            'algorithm_runtime': runtime,
            'total_time': total_time
        }
        
        print(f"  Tour length: {length:.4f}")
        print(f"  Algorithm runtime: {runtime:.2f}s")
        print(f"  Total time: {total_time:.2f}s")
    
    # Calculate improvement
    baseline = results[0.0]['tour_length']
    adaptive = results[0.3]['tour_length']
    improvement = ((baseline - adaptive) / baseline * 100)
    
    print(f"\n{'='*70}")
    print("RESULTS")
    print("="*70)
    print(f"Baseline (weight=0.0): {baseline:.4f}")
    print(f"Adaptive (weight=0.3): {adaptive:.4f}")
    print(f"Improvement: {improvement:.4f}%")
    print(f"Absolute difference: {baseline - adaptive:.6f}")
    
    print(f"\n{'='*70}")
    print("VERIFICATION")
    print("="*70)
    print(f"Claimed improvement: 1.32%")
    print(f"Measured improvement: {improvement:.4f}%")
    
    if improvement > 1.32:
        print(f"✓ EXCEEDS claimed improvement by {improvement - 1.32:.4f}%")
    elif improvement >= 1.32 * 0.9:  # Within 10%
        print(f"✓ CONFIRMS claimed improvement (within 10%)")
    else:
        print(f"✗ Below claimed improvement by {1.32 - improvement:.4f}%")
    
    # Check publication threshold
    print(f"\nPublication threshold: 0.1%")
    if improvement > 0.1:
        print(f"✓ EXCEEDS publication threshold by {improvement - 0.1:.4f}%")
        print("✓ Algorithm qualifies for publication!")
    else:
        print(f"✗ Below publication threshold by {0.1 - improvement:.4f}%")
    
    # Save results
    output = {
        'size': size,
        'seed': seed,
        'results': results,
        'improvement_percent': improvement,
        'verification': {
            'claimed_improvement': 1.32,
            'measured_improvement': improvement,
            'exceeds_claim': improvement > 1.32,
            'exceeds_publication_threshold': improvement > 0.1
        },
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    output_file = f"v14_minimal_benchmark_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    
    return output

if __name__ == "__main__":
    print("Starting minimal benchmark for v14...")
    start_time = time.time()
    
    try:
        results = run_minimal_benchmark()
        total_time = time.time() - start_time
        print(f"\nTotal benchmark time: {total_time:.1f} seconds")
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user.")
    except Exception as e:
        print(f"\nError during benchmark: {e}")
        import traceback
        traceback.print_exc()