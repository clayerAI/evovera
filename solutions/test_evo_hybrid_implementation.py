#!/usr/bin/env python3
"""
Test to verify Evo's hybrid matching implementation.
Check if the hybrid optimal/greedy matching is actually implemented.
"""

import sys
sys.path.append('.')
from solutions.tsp_v2_christofides import EuclideanTSPChristofides
import numpy as np
import time

def test_hybrid_implementation():
    """Test if hybrid matching is implemented in tsp_v2_christofides.py"""
    print("Testing Evo's hybrid matching implementation claim")
    print("=" * 60)
    
    # Create a small instance where hybrid should use optimal matching
    n = 30  # Small instance to get few odd vertices
    tsp = EuclideanTSPChristofides(n=n, seed=42)
    
    # Get MST and odd vertices
    mst_edges = tsp.prim_mst()
    odd_vertices = tsp.find_odd_degree_vertices(mst_edges)
    
    print(f"Number of odd vertices: {len(odd_vertices)}")
    
    # Check if there's a hybrid matching method
    if hasattr(tsp, 'hybrid_minimum_matching'):
        print("✓ Found hybrid_minimum_matching method")
        matching = tsp.hybrid_minimum_matching(odd_vertices)
    elif hasattr(tsp, 'optimal_minimum_matching'):
        print("✓ Found optimal_minimum_matching method")
        matching = tsp.optimal_minimum_matching(odd_vertices)
    else:
        print("✗ No hybrid or optimal matching method found")
        print("Only greedy_minimum_matching is available")
        
        # Test the greedy matching
        start = time.time()
        matching = tsp.greedy_minimum_matching(odd_vertices)
        elapsed = time.time() - start
        
        print(f"Using greedy_minimum_matching: {len(matching)} edges, time={elapsed:.6f}s")
        
        # Check if it's deterministic
        matching2 = tsp.greedy_minimum_matching(odd_vertices)
        same = True
        for (u1, v1, w1), (u2, v2, w2) in zip(matching, matching2):
            if u1 != u2 or v1 != v2 or abs(w1 - w2) > 1e-10:
                same = False
                break
        print(f"Deterministic: {same}")
    
    # Also check the nested CustomTSP class if it exists
    print("\nChecking nested CustomTSP class...")
    try:
        custom_tsp = tsp.CustomTSP(n=n, seed=42)
        custom_mst = custom_tsp.prim_mst()
        custom_odd = custom_tsp.find_odd_degree_vertices(custom_mst)
        
        if hasattr(custom_tsp, 'hybrid_minimum_matching'):
            print("✓ CustomTSP has hybrid_minimum_matching method")
        elif hasattr(custom_tsp, 'optimal_minimum_matching'):
            print("✓ CustomTSP has optimal_minimum_matching method")
        else:
            print("✗ CustomTSP only has greedy_minimum_matching method")
    except AttributeError:
        print("No nested CustomTSP class found")
    
    # Direct method verification - more reliable than pattern matching
    print("\nDirect method verification:")
    methods_to_check = [
        'greedy_minimum_matching',
        'optimal_minimum_matching_dp', 
        'hybrid_minimum_matching'
    ]
    
    for method in methods_to_check:
        if hasattr(tsp, method):
            print(f"✓ Has {method}() method")
        else:
            print(f"✗ Missing {method}() method")
    
    return len(odd_vertices)

def check_dp_implementation():
    """Check if DP optimal matching is implemented anywhere"""
    print("\n" + "=" * 60)
    print("Checking for DP optimal matching implementation...")
    
    # Search for DP implementation patterns using proper regex
    import os
    import re
    
    dp_patterns = [
        r'def.*optimal.*matching',
        r'def.*dp.*matching', 
        r'dynamic.*programming.*matching',
        r'optimal_minimum_matching_dp',  # Direct method name
        r'hybrid_minimum_matching'       # Hybrid method name
    ]
    found_files = []
    
    for root, dirs, files in os.walk('/workspace/evovera'):
        for file in files:
            if file.endswith('.py') and file != 'test_evo_hybrid_implementation.py':
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read().lower()
                        for pattern in dp_patterns:
                            # Use regex search instead of string 'in' operator
                            if re.search(pattern, content):
                                found_files.append((filepath, pattern))
                                break
                except:
                    pass
    
    if found_files:
        print(f"Found DP/hybrid patterns in {len(found_files)} files:")
        for filepath, pattern in found_files:
            print(f"  - {filepath} (pattern: {pattern})")
        return True
    else:
        print("No DP optimal matching implementation found via pattern search")
        return False

if __name__ == "__main__":
    odd_count = test_hybrid_implementation()
    has_dp = check_dp_implementation()
    
    print("\n" + "=" * 60)
    print("CONCLUSION:")
    print(f"Odd vertices count: {odd_count}")
    print(f"DP implementation found: {has_dp}")
    
    if odd_count <= 14 and not has_dp:
        print("⚠️  Evo claimed DP optimal matching for m ≤ 14, but no DP implementation found!")
        print("   The hybrid approach is not actually implemented in tsp_v2_christofides.py")
    elif has_dp:
        print("✓ DP optimal matching implementation exists")
    else:
        print("✓ For m > 14, greedy matching is appropriate (as Evo noted)")