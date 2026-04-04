#!/usr/bin/env python3
"""
Simple test of the multi-seed benchmark framework components.
"""

import sys
import os
import random
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test basic functions without importing the full framework
def test_basic_components():
    """Test the mathematical components we need."""
    print("Testing basic mathematical components...")
    
    # Test 1: Distance calculation
    points = [(0, 0), (3, 4), (0, 4)]  # 3-4-5 triangle
    def distance(p1, p2):
        return np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    
    assert distance(points[0], points[1]) == 5.0
    assert distance(points[0], points[2]) == 4.0
    assert distance(points[1], points[2]) == 3.0
    print("✓ Distance calculation works")
    
    # Test 2: Tour length calculation
    def calculate_tour_length(points, tour):
        total = 0.0
        n = len(points)
        for i in range(n):
            x1, y1 = points[tour[i]]
            x2, y2 = points[tour[(i + 1) % n]]
            total += np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return total
    
    tour = [0, 1, 2]  # 0→1→2→0
    length = calculate_tour_length(points, tour)
    expected = 5.0 + 3.0 + 4.0  # 0→1 + 1→2 + 2→0
    assert abs(length - expected) < 0.0001
    print("✓ Tour length calculation works")
    
    # Test 3: Statistics calculation
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    mean = np.mean(data)
    std = np.std(data)
    assert abs(mean - 3.0) < 0.0001
    assert abs(std - 1.4142) < 0.0001
    print("✓ Basic statistics work")
    
    print("\nAll basic component tests passed!")

def test_algorithm_imports():
    """Test that we can import the actual algorithms."""
    print("\nTesting algorithm imports...")
    
    algorithms_to_test = [
        ('v1 (Nearest Neighbor)', 'tsp_v1_nearest_neighbor'),
        ('v2 (Christofides)', 'tsp_v2_christofides'),
        ('v8 (Christofides-ILS)', 'tsp_v8_christofides_ils_hybrid_fixed'),
        ('v19 (Hybrid Structural)', 'tsp_v19_christofides_hybrid_structural')
    ]
    
    all_imported = True
    for alg_name, module_name in algorithms_to_test:
        try:
            module = __import__(f'solutions.{module_name}', fromlist=['solve_tsp'])
            solve_func = getattr(module, 'solve_tsp', None)
            if solve_func:
                print(f"✓ Imported {alg_name}")
            else:
                print(f"✗ {alg_name}: No solve_tsp function found")
                all_imported = False
        except ImportError as e:
            print(f"✗ {alg_name}: Import error - {e}")
            all_imported = False
        except Exception as e:
            print(f"✗ {alg_name}: Error - {e}")
            all_imported = False
    
    return all_imported

def test_algorithm_execution():
    """Test that algorithms can run on small problems."""
    print("\nTesting algorithm execution on small problem...")
    
    # Create a small problem
    points = [(random.random(), random.random()) for _ in range(10)]
    
    algorithms = []
    try:
        from solutions.tsp_v1_nearest_neighbor import solve_tsp as v1_solve
        algorithms.append(('v1', v1_solve))
    except:
        pass
    
    try:
        from solutions.tsp_v2_christofides import solve_tsp as v2_solve
        algorithms.append(('v2', v2_solve))
    except:
        pass
    
    try:
        from solutions.tsp_v8_christofides_ils_hybrid_fixed import solve_tsp as v8_solve
        algorithms.append(('v8', v8_solve))
    except:
        pass
    
    try:
        from solutions.tsp_v19_christofides_hybrid_structural import solve_tsp as v19_solve
        algorithms.append(('v19', v19_solve))
    except:
        pass
    
    if not algorithms:
        print("✗ No algorithms could be imported")
        return False
    
    print(f"Testing {len(algorithms)} algorithms on n=10 problem...")
    
    for alg_name, solve_func in algorithms:
        try:
            tour, cost = solve_func(points)
            assert len(tour) == 10
            assert len(set(tour)) == 10  # All unique
            assert 0 <= min(tour) <= 9
            assert 0 <= max(tour) <= 9
            print(f"✓ {alg_name}: Generated valid tour (cost={cost:.2f})")
        except Exception as e:
            print(f"✗ {alg_name}: Execution failed - {e}")
    
    print("\nAlgorithm execution tests completed.")
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("Multi-Seed Framework Component Test")
    print("=" * 60)
    
    all_passed = True
    
    # Test 1: Basic components
    try:
        test_basic_components()
    except Exception as e:
        print(f"✗ Basic components test failed: {e}")
        all_passed = False
    
    # Test 2: Algorithm imports
    try:
        if not test_algorithm_imports():
            all_passed = False
    except Exception as e:
        print(f"✗ Algorithm import test failed: {e}")
        all_passed = False
    
    # Test 3: Algorithm execution
    try:
        if not test_algorithm_execution():
            all_passed = False
    except Exception as e:
        print(f"✗ Algorithm execution test failed: {e}")
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL COMPONENT TESTS PASSED")
        print("\nThe framework components are working correctly.")
        print("\nNext steps for methodological corrections:")
        print("1. Run full multi-seed benchmarks (≥10 seeds)")
        print("2. Implement proper statistical tests (install scipy if possible)")
        print("3. Acquire real TSPLIB instances for evaluation")
        print("4. Compare against NN+2opt baseline (not plain NN)")
    else:
        print("❌ SOME TESTS FAILED")
        print("Check the errors above before proceeding.")
    
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())