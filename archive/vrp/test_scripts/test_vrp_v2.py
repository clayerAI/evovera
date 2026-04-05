#!/usr/bin/env python3
"""
Test script for VRP v2 structural hybrid algorithm.
"""

import sys
sys.path.insert(0, '/workspace/evovera/solutions')

from vrp_v2_clarke_wright_structural_hybrid import CapacitatedVRPStructuralHybrid
import time
import json

def test_vrp_v2():
    """Test VRP v2 algorithm on synthetic instance."""
    print("Testing VRP v2: Clarke-Wright + Structural Hybrid")
    print("=" * 60)
    
    # Create a VRP instance
    n_customers = 20
    capacity = 50
    seed = 42
    
    print(f"Creating VRP instance: {n_customers} customers, capacity={capacity}")
    vrp = CapacitatedVRPStructuralHybrid(
        n_customers=n_customers,
        capacity=capacity,
        seed=seed,
        depot_at_center=True
    )
    
    # Test different methods
    methods = ['sequential', 'parallel', 'structural_hybrid']
    
    results = {}
    for method in methods:
        print(f"\nTesting method: {method}")
        start_time = time.time()
        
        solution = vrp.solve_cvrp(method=method, apply_2opt=True)
        
        elapsed = time.time() - start_time
        
        print(f"  Total distance: {solution['total_distance']:.2f}")
        print(f"  Number of routes: {solution['num_routes']}")
        print(f"  Computation time: {solution['computation_time']:.4f}s")
        print(f"  Has capacity violations: {solution['has_capacity_violations']}")
        
        if solution['has_capacity_violations']:
            print(f"  Capacity violations: {len(solution['capacity_violations'])}")
        
        results[method] = {
            'total_distance': solution['total_distance'],
            'num_routes': solution['num_routes'],
            'computation_time': solution['computation_time'],
            'has_capacity_violations': solution['has_capacity_violations']
        }
    
    # Compare results
    print("\n" + "=" * 60)
    print("COMPARISON:")
    
    baseline_distance = results['parallel']['total_distance']
    for method, data in results.items():
        improvement = 0
        if method != 'parallel':
            improvement = ((baseline_distance - data['total_distance']) / baseline_distance) * 100
        
        print(f"{method:20s}: {data['total_distance']:8.2f} | "
              f"Routes: {data['num_routes']:2d} | "
              f"Time: {data['computation_time']:6.4f}s | "
              f"Violations: {data['has_capacity_violations']} | "
              f"Improvement: {improvement:+.2f}%")
    
    # Test community detection
    print("\n" + "=" * 60)
    print("Testing community detection:")
    
    mst_adj = vrp._build_mst()
    communities = vrp._detect_customer_communities(mst_adj)
    
    # Count customers per community
    community_counts = {}
    for customer, comm_id in communities.items():
        community_counts[comm_id] = community_counts.get(comm_id, 0) + 1
    
    print(f"Detected {len(community_counts)} communities:")
    for comm_id, count in sorted(community_counts.items()):
        print(f"  Community {comm_id}: {count} customers")
    
    return results

if __name__ == "__main__":
    test_vrp_v2()
