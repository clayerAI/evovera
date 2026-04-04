#!/usr/bin/env python3
"""
Test script for multi-seed benchmark framework.
Runs a quick test with small problem sizes to verify functionality.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmarks.multi_seed_benchmark_framework import (
    generate_random_points,
    calculate_tour_length,
    run_2opt,
    nn_2opt_baseline,
    run_benchmark
)

def test_basic_functions():
    """Test basic framework functions."""
    print("Testing basic framework functions...")
    
    # Test 1: Generate random points
    points = generate_random_points(10, seed=42)
    assert len(points) == 10
    assert all(len(p) == 2 for p in points)
    print("✓ Random point generation works")
    
    # Test 2: Calculate tour length
    tour = list(range(10))
    length = calculate_tour_length(points, tour)
    assert isinstance(length, float) and length > 0
    print("✓ Tour length calculation works")
    
    # Test 3: 2-opt improvement
    improved_tour = run_2opt(points, tour, max_iterations=10)
    assert len(improved_tour) == 10
    improved_length = calculate_tour_length(points, improved_tour)
    assert improved_length <= length  # Should not make it worse
    print("✓ 2-opt improvement works")
    
    # Test 4: NN+2opt baseline
    baseline_length = nn_2opt_baseline(points, seed=42)
    assert isinstance(baseline_length, float) and baseline_length > 0
    print("✓ NN+2opt baseline works")
    
    print("\nAll basic tests passed!")

def test_import_algorithms():
    """Test that we can import algorithm implementations."""
    print("\nTesting algorithm imports...")
    
    try:
        from solutions.tsp_v1_nearest_neighbor import solve_tsp as nn_solve
        print("✓ Imported v1 (Nearest Neighbor)")
    except ImportError as e:
        print(f"✗ Failed to import v1: {e}")
    
    try:
        from solutions.tsp_v2_christofides import solve_tsp as christofides_solve
        print("✓ Imported v2 (Christofides)")
    except ImportError as e:
        print(f"✗ Failed to import v2: {e}")
    
    try:
        from solutions.tsp_v8_christofides_ils_hybrid_fixed import solve_tsp as v8_solve
        print("✓ Imported v8 (Christofides-ILS)")
    except ImportError as e:
        print(f"✗ Failed to import v8: {e}")
    
    try:
        from solutions.tsp_v19_christofides_hybrid_structural import solve_tsp as v19_solve
        print("✓ Imported v19 (Hybrid Structural)")
    except ImportError as e:
        print(f"✗ Failed to import v19: {e}")
    
    print("\nAlgorithm import test completed.")

def run_quick_benchmark():
    """Run a quick benchmark to verify the framework works."""
    print("\nRunning quick benchmark test...")
    
    # Import the main function
    from benchmarks.multi_seed_benchmark_framework import run_multi_seed_experiment
    
    # Run with small parameters for quick test
    problem_sizes = [20, 30]  # Very small for quick test
    num_seeds = 3  # Small for quick test (normally ≥10)
    
    print(f"Running quick test with n={problem_sizes}, seeds={num_seeds}")
    print("This may take a minute...")
    
    try:
        results = run_multi_seed_experiment(problem_sizes, num_seeds)
        
        # Check results structure
        assert 'metadata' in results
        assert 'by_algorithm' in results
        assert 'by_problem_size' in results
        
        print("\n✓ Benchmark framework executed successfully")
        print(f"  Problem sizes tested: {results['metadata']['problem_sizes']}")
        print(f"  Algorithms tested: {list(results['by_algorithm'].keys())}")
        
        # Print quick summary
        for n in problem_sizes:
            if n in results['by_problem_size']:
                print(f"\n  n={n}:")
                for alg_name, test_data in results['by_problem_size'][n].items():
                    if 'improvement_pct' in test_data:
                        sig = "✓" if test_data['statistically_significant'] else "✗"
                        print(f"    {alg_name}: {test_data['improvement_pct']:+.2f}% {sig}")
        
        return True
        
    except Exception as e:
        print(f"✗ Benchmark test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Multi-Seed Benchmark Framework Test Suite")
    print("=" * 60)
    
    all_passed = True
    
    # Test 1: Basic functions
    try:
        test_basic_functions()
    except Exception as e:
        print(f"✗ Basic functions test failed: {e}")
        all_passed = False
    
    # Test 2: Algorithm imports
    try:
        test_import_algorithms()
    except Exception as e:
        print(f"✗ Algorithm import test failed: {e}")
        all_passed = False
    
    # Test 3: Quick benchmark
    try:
        if not run_quick_benchmark():
            all_passed = False
    except Exception as e:
        print(f"✗ Quick benchmark test failed: {e}")
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("Multi-seed benchmark framework is ready for use.")
        print("\nNext steps:")
        print("1. Run full benchmark with ≥10 seeds and larger problem sizes")
        print("2. Integrate real TSPLIB instances")
        print("3. Add statistical analysis reporting")
    else:
        print("❌ SOME TESTS FAILED")
        print("Check the errors above and fix before proceeding.")
    
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())