#!/usr/bin/env python3
"""
Run multi-seed benchmarks for TSP algorithms.
Implements methodological corrections: ≥10 seeds, statistical tests, NN+2opt baseline.

Author: Evo
Date: April 4, 2026
Status: CRITICAL - Methodological correction implementation
"""

import sys
import os
import time
import json
import argparse

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmarks.multi_seed_benchmark_framework import (
    run_multi_seed_experiment,
    generate_report,
    save_results,
    SCIPY_AVAILABLE
)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Run multi-seed TSP benchmarks with statistical tests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Methodological Requirements (per owner's verification):
1. ≥10 seeds per problem size
2. Statistical significance tests (p < 0.05)
3. Comparison against NN+2opt baseline (not plain NN)
4. Mean and standard deviation reporting

Example:
  %(prog)s --sizes 50 100 200 --seeds 10 --output results.json
        """
    )
    
    parser.add_argument('--sizes', type=int, nargs='+', default=[50, 100, 200],
                       help='Problem sizes to test (default: 50 100 200)')
    parser.add_argument('--seeds', type=int, default=10,
                       help='Number of random seeds per size (default: 10, minimum: 10)')
    parser.add_argument('--output', type=str, default=None,
                       help='Output JSON file for results (default: auto-generated)')
    parser.add_argument('--report', type=str, default=None,
                       help='Output text report file (default: auto-generated)')
    parser.add_argument('--quick', action='store_true',
                       help='Quick test with smaller sizes and fewer seeds')
    
    return parser.parse_args()

def validate_args(args):
    """Validate command line arguments."""
    if args.quick:
        print("⚠️  Quick mode enabled - using smaller parameters for testing")
        if args.seeds > 3:
            args.seeds = 3
        if max(args.sizes) > 100:
            args.sizes = [min(s, 100) for s in args.sizes]
    
    # Ensure minimum 10 seeds for non-quick mode
    if not args.quick and args.seeds < 10:
        print(f"⚠️  Warning: Owner requires ≥10 seeds. Increasing from {args.seeds} to 10.")
        args.seeds = 10
    
    # Check for scipy
    if not SCIPY_AVAILABLE:
        print("⚠️  WARNING: scipy not available. Statistical tests will be simplified.")
        print("   Install scipy for proper p-value calculations: pip install scipy")
    
    return args

def print_configuration(args):
    """Print benchmark configuration."""
    print("=" * 70)
    print("MULTI-SEED TSP BENCHMARK CONFIGURATION")
    print("=" * 70)
    print(f"Problem sizes: {args.sizes}")
    print(f"Seeds per size: {args.seeds} {'(QUICK MODE)' if args.quick else '(≥10 required)'}")
    print(f"Total algorithm runs: {len(args.sizes) * args.seeds * 4}")
    print(f"Statistical tests: {'Available' if SCIPY_AVAILABLE else 'Simplified (no scipy)'}")
    print(f"Baseline: NN+2opt (corrected methodology)")
    print(f"Algorithms: NN+2opt, Christofides, v8 (Christofides-ILS), v19 (Hybrid Structural)")
    print("=" * 70)
    print()

def main():
    """Main function to run multi-seed benchmarks."""
    args = parse_args()
    args = validate_args(args)
    
    print_configuration(args)
    
    # Ask for confirmation if not in quick mode
    if not args.quick and len(args.sizes) * args.seeds * 4 > 100:
        print(f"This will run {len(args.sizes) * args.seeds * 4} algorithm executions.")
        print("It may take several minutes to complete.")
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            print("Benchmark cancelled.")
            return 0
    
    print("Starting benchmark experiment...")
    print("(Press Ctrl+C to interrupt)")
    print()
    
    start_time = time.time()
    
    try:
        # Run the experiment
        results = run_multi_seed_experiment(args.sizes, args.seeds)
        experiment_time = time.time() - start_time
        
        # Generate report
        report = generate_report(results)
        
        # Save results
        if args.output:
            results_file = args.output
        else:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            results_file = f"multi_seed_results_{timestamp}.json"
        
        save_results(results, results_file)
        
        # Save report
        if args.report:
            report_file = args.report
        else:
            report_file = results_file.replace('.json', '_report.txt')
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        # Print summary
        print("\n" + "=" * 70)
        print("BENCHMARK COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"Total time: {experiment_time:.1f} seconds")
        print(f"Results saved: {results_file}")
        print(f"Report saved: {report_file}")
        print()
        
        # Print key statistical findings
        print("KEY STATISTICAL FINDINGS (vs NN+2opt baseline):")
        print("-" * 50)
        
        any_significant = False
        for n in args.sizes:
            if n in results['by_problem_size']:
                print(f"\nn = {n}:")
                size_data = results['by_problem_size'][n]
                
                for alg_name, test_data in size_data.items():
                    if 'improvement_pct' in test_data:
                        improvement = test_data['improvement_pct']
                        p_value = test_data['p_value']
                        significant = test_data['statistically_significant']
                        
                        if significant:
                            any_significant = True
                            symbol = "✅" if improvement > 0.1 else "⚠️"
                            significance_note = "SIGNIFICANT"
                        else:
                            symbol = "❌"
                            significance_note = "NOT SIGNIFICANT"
                        
                        print(f"  {symbol} {alg_name}: {improvement:+.2f}% improvement")
                        print(f"     p = {p_value:.4f} ({significance_note})")
        
        print("\n" + "=" * 70)
        if any_significant:
            print("✅ Some algorithms show statistically significant improvement!")
            print("   Further validation needed with TSPLIB instances and strong solvers.")
        else:
            print("❌ No statistically significant improvements found.")
            print("   This suggests the algorithms may not outperform the NN+2opt baseline.")
        
        print("\nNEXT STEPS FOR METHODOLOGICAL CORRECTIONS:")
        print("1. Run on real TSPLIB instances (eil51, kroA100, a280, att532)")
        print("2. Install LKH/OR-Tools for strong solver comparison")
        print("3. Perform ablation studies for v16/v18/v19")
        print("4. Ensure all comparisons use NN+2opt baseline (not plain NN)")
        print("=" * 70)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user.")
        return 1
    except Exception as e:
        print(f"\nError running benchmark: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())