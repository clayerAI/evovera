#!/usr/bin/env python3
"""Run quick comprehensive benchmark with n=100, 2 trials."""
import sys
sys.path.append('.')

# Import the comprehensive benchmark module
import comprehensive_benchmark_all_algorithms as benchmark

def main():
    print("Running quick comprehensive benchmark (n=100, trials=2)")
    print("This will test all 15 standardized TSP algorithms")
    print("=" * 70)
    
    # Run benchmark with smaller parameters for speed
    results = benchmark.run_comprehensive_benchmark(n=100, trials=2)
    
    print("\n" + "=" * 70)
    print("QUICK BENCHMARK COMPLETE")
    print("=" * 70)
    
    # Save results to file
    import json
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/workspace/evovera/quick_benchmark_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {filename}")
    
    # Print summary
    if 'baseline_avg' in results:
        baseline = results['baseline_avg']
        print(f"\nBaseline (NN+2opt) average: {baseline:.4f}")
        print("\nAlgorithm Performance (sorted by tour length):")
        print("-" * 80)
        
        # Get algorithm results
        algo_results = []
        for key, value in results.items():
            if key.startswith('algo_'):
                algo_name = key[5:]  # Remove 'algo_' prefix
                if 'avg_length' in value:
                    avg_length = value['avg_length']
                    avg_runtime = value.get('avg_runtime', 0)
                    improvement = ((baseline - avg_length) / baseline * 100) if baseline > 0 else 0
                    algo_results.append((algo_name, avg_length, avg_runtime, improvement))
        
        # Sort by tour length (best first)
        algo_results.sort(key=lambda x: x[1])
        
        for algo_name, avg_length, avg_runtime, improvement in algo_results:
            status = "✅ BEATS 0.1%" if improvement > 0.1 else "❌ Below threshold"
            print(f"{algo_name:35} Length: {avg_length:8.4f}  Runtime: {avg_runtime:6.2f}s  Improvement: {improvement:6.2f}%  {status}")

if __name__ == "__main__":
    main()