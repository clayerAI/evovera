#!/usr/bin/env python3
"""
Test TSPLIB parser with sample data.
"""

import sys
import os

# Import the parser template
from tsplib_parser_template import TSPLIBParser

def test_parser():
    """Test the TSPLIB parser with sample data."""
    print("Testing TSPLIB parser with sample data...")
    
    # Create test file path
    test_file = "test_sample.tsp"
    
    if not os.path.exists(test_file):
        print(f"✗ Test file not found: {test_file}")
        print("Creating sample test file...")
        create_sample_file(test_file)
    
    # Test parser
    parser = TSPLIBParser(test_file)
    success = parser.parse()
    
    if success:
        print(f"✓ Parser test successful!")
        print(f"  Name: {parser.name}")
        print(f"  Dimension: {parser.dimension}")
        print(f"  Edge weight type: {parser.edge_weight_type}")
        print(f"  Node coordinates: {len(parser.node_coords)} points")
        
        # Verify coordinates
        if parser.node_coords:
            print(f"  First coordinate: {parser.node_coords[0]}")
            print(f"  Last coordinate: {parser.node_coords[-1]}")
        
        return True
    else:
        print("✗ Parser test failed")
        return False

def create_sample_file(filename):
    """Create a sample TSPLIB file for testing."""
    sample_content = """NAME: test_sample
TYPE: TSP
COMMENT: Test instance for parser validation
DIMENSION: 5
EDGE_WEIGHT_TYPE: EUC_2D
NODE_COORD_SECTION
1 0.1 0.1
2 0.2 0.2
3 0.3 0.3
4 0.4 0.4
5 0.5 0.5
EOF"""
    
    with open(filename, 'w') as f:
        f.write(sample_content)
    
    print(f"✓ Created sample file: {filename}")
    return True

def test_gap_calculation():
    """Test gap-to-optimal calculation."""
    print("\nTesting gap-to-optimal calculation...")
    
    # Test cases
    test_cases = [
        {"optimal": 100, "our_solution": 105, "expected_gap": 5.0},
        {"optimal": 426, "our_solution": 450, "expected_gap": 5.63},
        {"optimal": 21282, "our_solution": 22000, "expected_gap": 3.37},
    ]
    
    for i, test in enumerate(test_cases):
        optimal = test["optimal"]
        our_solution = test["our_solution"]
        expected_gap = test["expected_gap"]
        
        gap = ((our_solution - optimal) / optimal) * 100.0
        gap_rounded = round(gap, 2)
        
        print(f"  Test {i+1}: Optimal={optimal}, Our={our_solution}, "
              f"Gap={gap_rounded}% (expected: {expected_gap}%)")
        
        if abs(gap_rounded - expected_gap) < 0.1:
            print(f"    ✓ Gap calculation correct")
        else:
            print(f"    ✗ Gap calculation incorrect")
    
    return True

def main():
    """Main test function."""
    print("=" * 80)
    print("TSPLIB Parser Test Suite")
    print("=" * 80)
    
    # Test 1: Parser functionality
    parser_ok = test_parser()
    
    # Test 2: Gap calculation
    gap_ok = test_gap_calculation()
    
    # Test 3: Directory structure
    print("\nTesting directory structure...")
    data_dir = "/workspace/evovera/data"
    tsplib_dir = os.path.join(data_dir, "tsplib")
    
    if not os.path.exists(tsplib_dir):
        print(f"  Creating TSPLIB directory: {tsplib_dir}")
        os.makedirs(tsplib_dir, exist_ok=True)
    
    if os.path.exists(tsplib_dir):
        print(f"  ✓ TSPLIB directory exists: {tsplib_dir}")
    else:
        print(f"  ✗ Failed to create TSPLIB directory")
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY:")
    print(f"  Parser test: {'✓ PASS' if parser_ok else '✗ FAIL'}")
    print(f"  Gap calculation: {'✓ PASS' if gap_ok else '✗ FAIL'}")
    print(f"  Directory structure: {'✓ READY' if os.path.exists(tsplib_dir) else '✗ NOT READY'}")
    
    if parser_ok and gap_ok and os.path.exists(tsplib_dir):
        print("\n✅ TSPLIB evaluation framework is READY for instance acquisition.")
        print("   Next step: Coordinate with Vera for TSPLIB instance download.")
    else:
        print("\n⚠️  TSPLIB evaluation framework needs attention.")
    
    print("=" * 80)

if __name__ == "__main__":
    main()