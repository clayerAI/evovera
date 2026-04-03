"""
Adversarial test cases for maximum subarray sum solution.
These test cases expose weaknesses in the current implementation.
"""

import sys
import os

# Add parent directory to path to import solution
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../solutions/sample-problem-001'))
from solution import max_subarray_sum

def run_adversarial_tests():
    """Run adversarial test cases against the solution."""
    print("Running adversarial tests for max_subarray_sum...")
    print("=" * 60)
    
    test_cases = [
        # Standard cases (should pass)
        {
            "name": "Standard case",
            "input": [-2, 1, -3, 4, -1, 2, 1, -5, 4],
            "expected": 6,
            "should_pass": True
        },
        {
            "name": "All positive",
            "input": [1, 2, 3, 4, 5],
            "expected": 15,
            "should_pass": True
        },
        {
            "name": "All negative",
            "input": [-1, -2, -3, -4],
            "expected": -1,
            "should_pass": True
        },
        {
            "name": "Empty array",
            "input": [],
            "expected": 0,
            "should_pass": True
        },
        
        # Adversarial cases (may fail or crash)
        {
            "name": "Floating point numbers",
            "input": [1.5, 2.5, 3.5],
            "expected": 7.5,
            "should_pass": False,  # Works but not documented
            "issue": "Type documentation says 'integers' but accepts floats"
        },
        {
            "name": "Mixed types (string)",
            "input": ["1", "2", "3"],
            "expected": None,
            "should_pass": False,  # Will crash
            "issue": "TypeError: '>' not supported between instances of 'str' and 'int'"
        },
        {
            "name": "None values",
            "input": [None, 1, 2],
            "expected": None,
            "should_pass": False,  # Will crash
            "issue": "TypeError: '>' not supported between instances of 'NoneType' and 'int'"
        },
        {
            "name": "Single zero",
            "input": [0],
            "expected": 0,
            "should_pass": True,
            "issue": "Edge case worth testing explicitly"
        },
        {
            "name": "Large negative numbers",
            "input": [-10**100, -10**100, -10**100],
            "expected": -10**100,
            "should_pass": True,
            "issue": "Tests handling of very large integers"
        },
        {
            "name": "Infinity values",
            "input": [float('inf'), 1, 2],
            "expected": float('inf'),
            "should_pass": False,  # May have unexpected behavior
            "issue": "Infinity handling not considered"
        },
        {
            "name": "Negative infinity",
            "input": [float('-inf'), -1, -2],
            "expected": float('-inf'),
            "should_pass": False,  # May have unexpected behavior
            "issue": "Negative infinity handling not considered"
        },
    ]
    
    passed = 0
    failed = 0
    crashed = 0
    
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        print(f"  Input: {test['input']}")
        print(f"  Expected: {test['expected']}")
        
        try:
            result = max_subarray_sum(test['input'])
            
            # Check if result matches expected (with tolerance for floats)
            if isinstance(result, float) and isinstance(test['expected'], float):
                match = abs(result - test['expected']) < 1e-10
            else:
                match = result == test['expected']
            
            if match:
                print(f"  Result: {result} ✓")
                if test.get('should_pass', True):
                    passed += 1
                    print(f"  Status: PASS (as expected)")
                else:
                    failed += 1
                    print(f"  Status: PASS (but shouldn't according to spec)")
                    if 'issue' in test:
                        print(f"  Issue: {test['issue']}")
            else:
                failed += 1
                print(f"  Result: {result} ✗")
                print(f"  Status: FAIL")
                if 'issue' in test:
                    print(f"  Issue: {test['issue']}")
                    
        except Exception as e:
            crashed += 1
            print(f"  Result: CRASHED with {type(e).__name__}: {e}")
            print(f"  Status: CRASH")
            if 'issue' in test:
                print(f"  Issue: {test['issue']}")
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"  Total tests: {len(test_cases)}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Crashed: {crashed}")
    
    # Calculate adversarial score (lower is more vulnerable)
    adversarial_score = (crashed * 3 + failed * 1) / len(test_cases)
    print(f"  Adversarial Vulnerability Score: {adversarial_score:.2f}/3.0")
    
    if adversarial_score > 1.0:
        print("  ⚠️  Solution is vulnerable to adversarial inputs")
    elif adversarial_score > 0.5:
        print("  ⚠️  Solution has some adversarial weaknesses")
    else:
        print("  ✓ Solution is relatively robust to adversarial inputs")
    
    return adversarial_score

def generate_edge_cases():
    """Generate additional edge cases for fuzz testing."""
    print("\n" + "=" * 60)
    print("Suggested edge cases for further testing:")
    
    edge_cases = [
        "Arrays with alternating very large positive and negative numbers",
        "Arrays where all elements are zero",
        "Arrays with duplicate maximum subarrays",
        "Arrays where maximum subarray is the entire array",
        "Arrays where maximum subarray is a single element",
        "Arrays with arithmetic progressions",
        "Arrays with geometric progressions",
        "Random arrays with known optimal solutions (for property testing)",
        "Arrays with overflow potential in other languages (test with sys.maxsize)",
        "Arrays with numpy arrays or other sequence types",
    ]
    
    for i, case in enumerate(edge_cases, 1):
        print(f"  {i}. {case}")
    
    return edge_cases

if __name__ == "__main__":
    score = run_adversarial_tests()
    edge_cases = generate_edge_cases()
    
    # Save results
    with open("adversarial_test_results.txt", "w") as f:
        f.write(f"Adversarial Vulnerability Score: {score:.2f}/3.0\n")
        f.write(f"Edge cases to test: {len(edge_cases)}\n")
        f.write("\n".join(edge_cases))