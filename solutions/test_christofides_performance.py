#!/usr/bin/env python3
"""
Performance test for Christofides algorithm
"""

import sys
import os
sys.path.append('solutions/tsp-500-euclidean-christofides')

from solution import EuclideanTSP
import time
import numpy as np

def test_performance():
    print("Testing Christofides algorithm performance...")
    
    # Test with different sizes
    sizes = [50, 100, 200, 300, 400, 500]
    
    for n in sizes:
        print(f"\n{'='*60}")
        print(f"Testing n = {n}")
        print(f"{'='*60}")
        
        # Create instance
        tsp = EuclideanTSP(n=n, seed=42)
        
        # Time individual components
        start = time.time()
        mst_edges = tsp.prim_mst()
        mst_time = time.time() - start
        
        odd_vertices = tsp.get_odd_degree_vertices(mst_edges)
        print(f"  Odd vertices: {len(odd_vertices)} ({(len(odd_vertices)/n)*100:.1f}% of n)")
        
        start = time.time()
        matching_edges = tsp.minimum_weight_perfect_matching(odd_vertices)
        matching_time = time.time() - start
        
        start = time.time()
        tour, distance = tsp.christofides(apply_two_opt=False)  # Without 2-opt for fair comparison
        total_time = time.time() - start
        
        print(f"  MST time: {mst_time:.3f}s")
        print(f"  Matching time: {matching_time:.3f}s")
        print(f"  Total Christofides time: {total_time:.3f}s")
        
        # Estimate complexity
        m = len(odd_vertices)
        print(f"  m (odd vertices) = {m}")
        print(f"  Matching time / m^3: {matching_time/(m**3):.6f}")
        print(f"  Matching time / m^4: {matching_time/(m**4):.6f}")
        
        # Run full algorithm with 2-opt
        start = time.time()
        tour, distance = tsp.christofides(apply_two_opt=True)
        full_time = time.time() - start
        print(f"  Full algorithm with 2-opt: {full_time:.3f}s")

if __name__ == "__main__":
    test_performance()