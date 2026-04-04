"""
Adversarial Test Runner for TSP Solutions
Automatically tests Evo's TSP implementations against adversarial test cases.
"""

import importlib.util
import sys
import os
import json
import time
from typing import Dict, List, Tuple, Any, Optional
import math

class TSPAdversarialRunner:
    """Run adversarial tests on TSP solutions."""
    
    def __init__(self, solutions_dir: str = "/workspace/evovera/solutions"):
        self.solutions_dir = solutions_dir
        self.test_suite = None
        self.results = {}
    
    def load_solution(self, solution_path: str) -> Any:
        """Dynamically load a TSP solution module."""
        try:
            spec = importlib.util.spec_from_file_location("tsp_solution", solution_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules["tsp_solution"] = module
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            print(f"Error loading solution {solution_path}: {e}")
            return None
    
    def load_test_suite(self, suite_path: str = "/workspace/evovera/tests/adversarial_suite.json"):
        """Load adversarial test suite."""
        try:
            with open(suite_path, 'r') as f:
                self.test_suite = json.load(f)
            print(f"Loaded test suite from {suite_path}")
            return True
        except Exception as e:
            print(f"Error loading test suite: {e}")
            return False
    
    def run_solution_on_test(self, solution_module, test_case: Dict[str, Any], 
                            test_name: str) -> Dict[str, Any]:
        """Run a solution on a specific test case."""
        result = {
            "test_name": test_name,
            "passed": False,
            "error": None,
            "execution_time": None,
            "tour_length": None,
            "tour_valid": False
        }
        
        try:
            # Extract cities from test case
            if "cities_list" in test_case:
                # Edge cases - run on each subcase
                return self.run_solution_on_edge_cases(solution_module, test_case, test_name)
            
            cities = test_case["cities"]
            
            # Convert to format expected by TSP solutions
            # Typically: list of (x, y) tuples or list of city objects
            coordinates = [(x, y) for x, y, _ in cities]
            
            # Find the solve function in the module
            solve_func = None
            for attr_name in dir(solution_module):
                attr = getattr(solution_module, attr_name)
                if callable(attr) and "solve" in attr_name.lower():
                    solve_func = attr
                    break
            
            if not solve_func:
                # Try default name
                if hasattr(solution_module, "solve_tsp"):
                    solve_func = solution_module.solve_tsp
                else:
                    result["error"] = "No solve function found in module"
                    return result
            
            # Run the solution
            start_time = time.time()
            tour = solve_func(coordinates)
            end_time = time.time()
            
            result["execution_time"] = end_time - start_time
            
            # Validate tour
            if self.validate_tour(tour, len(coordinates)):
                result["tour_valid"] = True
                result["tour_length"] = self.calculate_tour_length(tour, coordinates)
                result["passed"] = True
            else:
                result["error"] = "Invalid tour produced"
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def run_solution_on_edge_cases(self, solution_module, test_case: Dict[str, Any], 
                                  test_name: str) -> Dict[str, Any]:
        """Run solution on edge cases (collection of small tests)."""
        results = []
        all_passed = True
        
        for i, cities in enumerate(test_case["cities_list"]):
            sub_result = {
                "subcase": i,
                "passed": False,
                "error": None,
                "tour_valid": False
            }
            
            try:
                coordinates = [(x, y) for x, y, _ in cities]
                
                # Find solve function
                solve_func = None
                for attr_name in dir(solution_module):
                    attr = getattr(solution_module, attr_name)
                    if callable(attr) and "solve" in attr_name.lower():
                        solve_func = attr
                        break
                
                if not solve_func and hasattr(solution_module, "solve_tsp"):
                    solve_func = solution_module.solve_tsp
                
                if not solve_func:
                    sub_result["error"] = "No solve function found"
                    results.append(sub_result)
                    all_passed = False
                    continue
                
                tour = solve_func(coordinates)
                
                if self.validate_tour(tour, len(coordinates)):
                    sub_result["tour_valid"] = True
                    sub_result["passed"] = True
                else:
                    sub_result["error"] = "Invalid tour"
                    all_passed = False
                    
            except Exception as e:
                sub_result["error"] = str(e)
                all_passed = False
            
            results.append(sub_result)
        
        return {
            "test_name": test_name,
            "passed": all_passed,
            "subresults": results,
            "all_passed": all_passed
        }
    
    def validate_tour(self, tour: List[int], n_cities: int) -> bool:
        """Validate that a tour is a valid permutation of cities."""
        if not tour:
            return False
        
        if len(tour) != n_cities:
            return False
        
        # Check that all cities appear exactly once
        seen = set()
        for city in tour:
            if not isinstance(city, int):
                return False
            if city < 0 or city >= n_cities:
                return False
            if city in seen:
                return False
            seen.add(city)
        
        return len(seen) == n_cities
    
    def calculate_tour_length(self, tour: List[int], coordinates: List[Tuple[float, float]]) -> float:
        """Calculate total length of a tour."""
        total = 0.0
        n = len(tour)
        
        for i in range(n):
            city1 = tour[i]
            city2 = tour[(i + 1) % n]
            x1, y1 = coordinates[city1]
            x2, y2 = coordinates[city2]
            total += math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
        
        return total
    
    def run_all_tests(self, solution_path: str) -> Dict[str, Any]:
        """Run all adversarial tests on a solution."""
        print(f"\n{'='*60}")
        print(f"Running adversarial tests on: {solution_path}")
        print(f"{'='*60}")
        
        solution_module = self.load_solution(solution_path)
        if not solution_module:
            return {"error": "Failed to load solution"}
        
        if not self.test_suite:
            if not self.load_test_suite():
                return {"error": "Failed to load test suite"}
        
        results = {
            "solution": os.path.basename(solution_path),
            "timestamp": time.time(),
            "tests": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0
            }
        }
        
        for test_name, test_case in self.test_suite.items():
            print(f"\nRunning test: {test_name}")
            print(f"  Description: {test_case.get('description', 'No description')}")
            
            test_result = self.run_solution_on_test(solution_module, test_case, test_name)
            results["tests"][test_name] = test_result
            
            results["summary"]["total_tests"] += 1
            
            if test_result.get("passed", False):
                results["summary"]["passed"] += 1
                print(f"  Result: PASSED")
                if "tour_length" in test_result:
                    print(f"  Tour length: {test_result['tour_length']:.2f}")
                if "execution_time" in test_result:
                    print(f"  Execution time: {test_result['execution_time']:.4f}s")
            else:
                results["summary"]["failed"] += 1
                if test_result.get("error"):
                    results["summary"]["errors"] += 1
                    print(f"  Result: ERROR - {test_result['error']}")
                else:
                    print(f"  Result: FAILED")
        
        # Print summary
        print(f"\n{'='*60}")
        print("TEST SUMMARY:")
        print(f"  Total tests: {results['summary']['total_tests']}")
        print(f"  Passed: {results['summary']['passed']}")
        print(f"  Failed: {results['summary']['failed']}")
        print(f"  Errors: {results['summary']['errors']}")
        print(f"{'='*60}")
        
        return results
    
    def generate_report(self, results: Dict[str, Any], 
                       output_path: str = "/workspace/evovera/reviews/adversarial_report.md") -> str:
        """Generate a markdown report from test results."""
        report = f"""# Adversarial Test Report

## Solution: {results.get('solution', 'Unknown')}
**Test Date:** {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(results.get('timestamp', time.time())))}

## Summary
- **Total Tests:** {results['summary']['total_tests']}
- **Passed:** {results['summary']['passed']}
- **Failed:** {results['summary']['failed']}
- **Errors:** {results['summary']['errors']}
- **Success Rate:** {results['summary']['passed'] / max(1, results['summary']['total_tests']) * 100:.1f}%

## Detailed Results

"""
        
        for test_name, test_result in results.get("tests", {}).items():
            report += f"### {test_name}\n"
            
            if test_result.get("passed", False):
                report += f"**Status:** ✅ PASSED\n"
                if "tour_length" in test_result:
                    report += f"- Tour length: {test_result['tour_length']:.2f}\n"
                if "execution_time" in test_result:
                    report += f"- Execution time: {test_result['execution_time']:.4f}s\n"
            else:
                report += f"**Status:** ❌ FAILED\n"
                if test_result.get("error"):
                    report += f"- Error: {test_result['error']}\n"
                else:
                    report += f"- Reason: Tour validation failed\n"
            
            # Add subresults for edge cases
            if "subresults" in test_result:
                report += "\n**Edge Case Subresults:**\n"
                for i, sub in enumerate(test_result["subresults"]):
                    status = "✅" if sub.get("passed", False) else "❌"
                    error = f" - {sub['error']}" if sub.get("error") else ""
                    report += f"  {i}. {status}{error}\n"
            
            report += "\n"
        
        # Add recommendations based on failures
        report += "## Recommendations\n\n"
        
        failures = []
        for test_name, test_result in results.get("tests", {}).items():
            if not test_result.get("passed", False):
                failures.append((test_name, test_result))
        
        if not failures:
            report += "All tests passed! The solution appears robust against standard adversarial cases.\n"
        else:
            report += "### Issues Found:\n"
            for test_name, test_result in failures:
                weakness = self.test_suite.get(test_name, {}).get("expected_weakness", "Unknown weakness")
                report += f"1. **{test_name}**: {weakness}\n"
                if test_result.get("error"):
                    report += f"   - Error: {test_result['error']}\n"
            
            report += "\n### Suggested Improvements:\n"
            if any("nearest_neighbor" in name for name, _ in failures):
                report += "- Consider adding 2-opt or 3-opt local search to escape local optima\n"
                report += "- Implement multiple random restarts with different starting cities\n"
                report += "- Add lookahead or beam search for better global optimization\n"
            
            if any("triangle" in name for name, _ in failures):
                report += "- Ensure algorithm doesn't assume triangle inequality holds\n"
                report += "- Consider supporting non-metric TSP instances\n"
            
            if any("large_scale" in name for name, _ in failures):
                report += "- Optimize for scalability with large instance sizes\n"
                report += "- Consider space-time tradeoffs for memory efficiency\n"
                report += "- Implement pruning techniques for faster execution\n"
        
        # Save report
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(report)
        
        print(f"Report saved to: {output_path}")
        return report


def main():
    """Main function to run adversarial tests."""
    runner = TSPAdversarialRunner()
    
    # First, generate the test suite if it doesn't exist
    from adversarial_tsp_tests import TSPAdversarialGenerator
    generator = TSPAdversarialGenerator()
    
    test_dir = "/workspace/evovera/tests"
    os.makedirs(test_dir, exist_ok=True)
    
    suite_path = os.path.join(test_dir, "adversarial_suite.json")
    if not os.path.exists(suite_path):
        print("Generating adversarial test suite...")
        generator.save_test_suite(suite_path)
    
    # Load test suite
    runner.load_test_suite(suite_path)
    
    # Find TSP solutions to test
    solutions_dir = "/workspace/evovera/solutions"
    tsp_solutions = []
    
    for root, dirs, files in os.walk(solutions_dir):
        for file in files:
            if file.startswith("tsp_") and file.endswith(".py"):
                tsp_solutions.append(os.path.join(root, file))
    
    if not tsp_solutions:
        print("No TSP solutions found. Waiting for Evo's implementation...")
        print("Expected: solutions/tsp_v1_nearest_neighbor.py")
        return
    
    # Run tests on each solution
    all_results = []
    for solution_path in tsp_solutions:
        results = runner.run_all_tests(solution_path)
        all_results.append(results)
        
        # Generate report
        solution_name = os.path.basename(solution_path).replace('.py', '')
        report_path = f"/workspace/evovera/reviews/adversarial_{solution_name}.md"
        runner.generate_report(results, report_path)
    
    return all_results


if __name__ == "__main__":
    main()