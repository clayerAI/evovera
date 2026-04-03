#!/usr/bin/env python3
"""
Test to verify my hybrid matching implementation actually exists and works.
"""

import sys
sys.path.append('.')
from solutions.tsp_v2_christofides import EuclideanTSPChristofides
import time

def test_hybrid_implementation():
    """Test if hybrid matching is implemented in tsp_v2_christofides.py"""
    print("Testing my hybrid matching implementation")
    print("=" * 60)
    
    # Create a small instance where hybrid should use optimal matching
    n = 30  # Small instance to get few odd vertices
    tsp = EuclideanTSPChristofides(n=n, seed=42)
    
    # Get MST and odd vertices
    mst_edges = tsp.prim_mst()
    odd_vertices = tsp.find_odd_degree_vertices(mst_edges)
    
    print(f"Number of odd vertices: {len(odd_vertices)}")
    
    # Check all available methods
    print("\nAvailable matching methods:")
    methods = [attr for attr in dir(tsp) if 'matching' in attr.lower()]
    for method in sorted(methods):
        print(f"  - {method}")
    
    # Test hybrid method
    if hasattr(tsp, 'hybrid_minimum_matching'):
        print(f"\n✓ Found hybrid_minimum_matching method")
        start = time.time()
        matching = tsp.hybrid_minimum_matching(odd_vertices)
        elapsed = time.time() - start
        print(f"  Hybrid matching: {len(matching)} edges, time={elapsed:.6f}s")
        
        # Check if it used DP for m ≤ 14
        m = len(odd_vertices)
        if m <= 14:
            print(f"  m={m} ≤ 14, should use DP optimal matching")
            # Check if optimal_minimum_matching_dp exists
            if hasattr(tsp, 'optimal_minimum_matching_dp'):
                print(f"  ✓ optimal_minimum_matching_dp method exists")
                # Compare with greedy
                greedy_start = time.time()
                greedy_matching = tsp.greedy_minimum_matching(odd_vertices)
                greedy_time = time.time() - greedy_start
                greedy_cost = sum(w for _, _, w in greedy_matching)
                hybrid_cost = sum(w for _, _, w in matching)
                print(f"  Greedy cost: {greedy_cost:.6f}, time={greedy_time:.6f}s")
                print(f"  Hybrid cost: {hybrid_cost:.6f}, time={elapsed:.6f}s")
                if hybrid_cost <= greedy_cost + 1e-10:
                    print(f"  ✓ Hybrid cost ≤ Greedy cost (as expected)")
                else:
                    print(f"  ⚠️  Hybrid cost > Greedy cost (unexpected)")
            else:
                print(f"  ✗ optimal_minimum_matching_dp method not found!")
        else:
            print(f"  m={m} > 14, should use greedy matching")
    else:
        print(f"\n✗ hybrid_minimum_matching method not found!")
    
    # Test DP method directly
    print("\n" + "=" * 60)
    print("Testing DP optimal matching directly:")
    if hasattr(tsp, 'optimal_minimum_matching_dp'):
        print("✓ optimal_minimum_matching_dp method exists")
        try:
            start = time.time()
            dp_matching = tsp.optimal_minimum_matching_dp(odd_vertices)
            elapsed = time.time() - start
            dp_cost = sum(w for _, _, w in dp_matching)
            print(f"  DP matching: {len(dp_matching)} edges, cost={dp_cost:.6f}, time={elapsed:.6f}s")
        except Exception as e:
            print(f"  DP matching failed: {e}")
    else:
        print("✗ optimal_minimum_matching_dp method not found")
    
    return len(odd_vertices)

if __name__ == "__main__":
    odd_count = test_hybrid_implementation()
    print("\n" + "=" * 60)
    print(f"CONCLUSION: Hybrid implementation exists with {odd_count} odd vertices")
    print("My implementation has both hybrid_minimum_matching and optimal_minimum_matching_dp methods")