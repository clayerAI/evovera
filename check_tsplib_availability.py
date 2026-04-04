#!/usr/bin/env python3
"""
Check TSPLIB instance availability and document requirements for Phase 2.
This is preparatory work that doesn't conflict with Vera's coordination.
"""

import os
import sys

def check_tsplib_requirements():
    """Document TSPLIB instance requirements for methodological correction."""
    
    print("=" * 80)
    print("TSPLIB EVALUATION REQUIREMENTS - Phase 2 of Methodological Correction")
    print("=" * 80)
    
    # Required TSPLIB instances (from methodological_correction_plan.md)
    required_instances = [
        "eil51",      # 51 cities - small instance
        "kroA100",    # 100 cities - medium instance  
        "a280",       # 280 cities - larger instance
        "att532",     # 532 cities - challenging instance
    ]
    
    # Known optimal solutions (from TSPLIB documentation)
    optimal_solutions = {
        "eil51": 426,
        "kroA100": 21282,
        "a280": 2579,
        "att532": 27686,
    }
    
    print("\n📋 REQUIRED INSTANCES:")
    for instance in required_instances:
        opt = optimal_solutions.get(instance, "UNKNOWN")
        print(f"  • {instance}: Optimal solution = {opt}")
    
    print("\n📁 EXPECTED FILE FORMAT:")
    print("  • File extension: .tsp or .txt")
    print("  • Format: Standard TSPLIB format")
    print("  • Location: /workspace/evovera/data/tsplib/")
    
    print("\n🔧 TECHNICAL REQUIREMENTS:")
    print("  1. TSPLIB parser to read instance files")
    print("  2. Gap-to-optimal calculation: (our_solution - optimal) / optimal * 100%")
    print("  3. Integration with existing benchmark framework")
    
    print("\n📊 EVALUATION METRICS:")
    print("  • Gap to optimal (%) - primary metric")
    print("  • Runtime comparison")
    print("  • Consistency across instances")
    
    print("\n🎯 SUCCESS CRITERIA:")
    print("  • All 4 instances successfully parsed and benchmarked")
    print("  • Gap-to-optimal calculated for all algorithms")
    print("  • Results documented in comprehensive report")
    
    print("\n⚠️ COORDINATION NEEDED:")
    print("  • Need Vera's coordination for acquiring instances")
    print("  • Potential sources: TSPLIB website, academic repositories")
    print("  • May require owner approval for download/usage")
    
    print("\n" + "=" * 80)
    
    # Check current directory structure
    print("\n📂 CURRENT DIRECTORY CHECK:")
    data_dir = "/workspace/evovera/data"
    tsplib_dir = os.path.join(data_dir, "tsplib")
    
    if os.path.exists(data_dir):
        print(f"  ✓ Data directory exists: {data_dir}")
        
        # List current files in data directory
        try:
            current_files = os.listdir(data_dir)
            print(f"  • Current files in data/: {len(current_files)} files")
            for f in sorted(current_files)[:10]:  # Show first 10
                print(f"    - {f}")
            if len(current_files) > 10:
                print(f"    ... and {len(current_files) - 10} more")
        except Exception as e:
            print(f"  ✗ Error listing data directory: {e}")
    else:
        print(f"  ✗ Data directory missing: {data_dir}")
    
    if os.path.exists(tsplib_dir):
        print(f"  ✓ TSPLIB directory exists: {tsplib_dir}")
        try:
            tsplib_files = os.listdir(tsplib_dir)
            print(f"  • TSPLIB files found: {len(tsplib_files)}")
            for f in sorted(tsplib_files):
                if f.endswith(('.tsp', '.txt', '.TSP')):
                    print(f"    - {f}")
        except Exception as e:
            print(f"  ✗ Error listing TSPLIB directory: {e}")
    else:
        print(f"  ✗ TSPLIB directory missing: {tsplib_dir}")
        print(f"  • Will need to create: mkdir -p {tsplib_dir}")
    
    print("\n" + "=" * 80)
    print("✅ Preparatory analysis complete. Ready for coordination with Vera.")
    print("=" * 80)

if __name__ == "__main__":
    check_tsplib_requirements()