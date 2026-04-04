#!/usr/bin/env python3
"""
Test Christofides matching boundary conditions.
Specifically tests the transition between optimal matching (m ≤ 14) and greedy matching (m > 14).
"""

import sys
import os
sys.path.append('/workspace/evovera/solutions')

import numpy as np
import math
import random
import time
from typing import List, Tuple

# Import Christofides solution
try:
    from tsp_v2_christofides import solve_tsp as solve_christofides
    print("✓ Loaded Christofides solution")
except ImportError as e:
    print(f"✗ Failed to load Christofides: {e}")
    solve_christofides = None

# Try to import the actual Christofides class to inspect matching methods
try:
    from tsp_v2_christofides import ChristofidesTSP
    print("✓ Loaded ChristofidesTSP class for inspection")
    can_inspect = True
except ImportError:
    print("✗ Could not load ChristofidesTSP class directly")
    can_inspect = False


def create_points_for_m_odd_vertices(n_points: int, m_odd: int) -> np.ndarray:
    """
    Create point set that should result in approximately m odd-degree vertices in MST.
    This is heuristic - creating exact m odd vertices is complex.
    Strategy: Create m/2 pairs of closely spaced points (likely leaves in MST).
    """
    points = []
    
    # Create pairs for potential leaves (odd-degree vertices)
    pairs = m_odd // 2
    for _ in range(pairs):
        center = np.array([random.random() * 0.8 + 0.1, random.random() * 0.8 + 0.1])
        # Two points very close together - likely connected in MST, making them leaves
        for _ in range(2):
            offset = np.random.randn(2) * 0.01
            point = center + offset
            point = np.clip(point, 0, 1)
            points.append(point)
    
    # Add remaining points randomly
    while len(points) < n_points:
        points.append([random.random(), random.random()])
    
    return np.array(points[:n_points])


def test_matching_boundary():
    """Test Christofides algorithm at the m=14 boundary."""
    print("=" * 70)
    print("Testing Christofides Matching Boundary (m = 14)")
    print("Optimal matching should be used for m ≤ 14, greedy for m > 14")
    print("=" * 70)
    
    if not solve_christofides:
        print("Cannot run tests - Christofides solution not loaded")
        return
    
    test_cases = [
        ("Small m (≈10 odd vertices)", 20, 10),   # Should use optimal matching
        ("Boundary m=14", 25, 14),                # Should use optimal matching
        ("Boundary m=15", 30, 15),                # Should switch to greedy matching
        ("Large m (≈20 odd vertices)", 40, 20),   # Should use greedy matching
    ]
    
    for test_name, n_points, target_m in test_cases:
        print(f"\n{'='*40}")
        print(f"Test: {test_name}")
        print(f"  n={n_points}, target m={target_m}")
        print(f"{'='*40}")
        
        # Generate points
        points = create_points_for_m_odd_vertices(n_points, target_m)
        points_list = [(float(p[0]), float(p[1])) for p in points]
        
        # Run Christofides
        try:
            start_time = time.time()
            tour = solve_christofides(points_list)
            end_time = time.time()
            
            # Validate tour
            if len(tour) != n_points or len(set(tour)) != n_points:
                print(f"  ✗ Invalid tour produced")
                continue
            
            # Calculate tour length
            total = 0.0
            for i in range(len(tour) - 1):
                p1 = points[tour[i]]
                p2 = points[tour[i + 1]]
                total += math.sqrt(((p1 - p2) ** 2).sum())
            # Close the tour
            p1 = points[tour[-1]]
            p2 = points[tour[0]]
            total += math.sqrt(((p1 - p2) ** 2).sum())
            
            print(f"  ✓ Valid tour, length: {total:.4f}, time: {end_time-start_time:.3f}s")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Try to inspect the implementation if possible
    if can_inspect:
        print(f"\n{'='*70}")
        print("Inspecting Christofides implementation...")
        print(f"{'='*70}")
        
        # Check for hybrid_minimum_matching method
        import inspect
        methods = [name for name, _ in inspect.getmembers(ChristofidesTSP, predicate=inspect.isfunction)]
        
        print("Key methods found in ChristofidesTSP class:")
        matching_methods = [m for m in methods if 'matching' in m.lower()]
        for method in matching_methods:
            print(f"  • {method}")
        
        # Check for optimal_minimum_matching_dp
        if 'optimal_minimum_matching_dp' in methods:
            print(f"\n✓ Found optimal_minimum_matching_dp() method")
            # Try to get source
            try:
                source = inspect.getsource(ChristofidesTSP.optimal_minimum_matching_dp)
                lines = source.split('\n')
                print(f"  Method length: {len(lines)} lines")
                # Check for m ≤ 14 condition
                for i, line in enumerate(lines[:10]):
                    if '14' in line or 'm <=' in line or 'm <' in line:
                        print(f"  Line {i+1}: {line.strip()}")
            except:
                print(f"  Could not inspect source")
        
        if 'hybrid_minimum_matching' in methods:
            print(f"\n✓ Found hybrid_minimum_matching() method")
            try:
                source = inspect.getsource(ChristofidesTSP.hybrid_minimum_matching)
                lines = source.split('\n')
                print(f"  Method length: {len(lines)} lines")
                # Look for boundary condition
                for i, line in enumerate(lines[:15]):
                    if '14' in line or 'm <=' in line or 'optimal' in line.lower() or 'greedy' in line.lower():
                        print(f"  Line {i+1}: {line.strip()}")
            except:
                print(f"  Could not inspect source")
    
    print(f"\n{'='*70}")
    print("TESTING COMPLETE")
    print(f"{'='*70}")
    print("\nObservations:")
    print("1. Christofides algorithm should use optimal DP matching for m ≤ 14")
    print("2. For m > 14, it should use greedy matching")
    print("3. The hybrid approach balances optimality vs computational cost")
    print("\nIf performance issues are found at the boundary (m=14 vs m=15),")
    print("this could indicate problems with the matching implementation.")


if __name__ == "__main__":
    test_matching_boundary()