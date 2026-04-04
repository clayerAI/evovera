#!/usr/bin/env python3
"""
TSPLIB Parser for Phase 2 evaluation.
Updated with actual optimal values and tested with acquired instances.
"""

import re
import os
import numpy as np
from typing import Dict, List, Tuple, Optional

class TSPLIBParser:
    """Parser for TSPLIB format instances."""
    
    # Known optimal solutions for required instances
    OPTIMAL_VALUES = {
        "eil51": 426,
        "kroA100": 21282,
        "a280": 2579,
        "att532": 27686,
    }
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.name = None
        self.dimension = 0
        self.edge_weight_type = None
        self.node_coords = []
        self.optimal_value = None
        
    def parse(self) -> bool:
        """Parse TSPLIB file and extract instance data."""
        try:
            with open(self.filepath, 'r') as f:
                content = f.read()
            
            # Extract metadata
            self._extract_metadata(content)
            
            # Extract node coordinates
            self._extract_node_coords(content)
            
            # Set optimal value from known database
            if self.name in self.OPTIMAL_VALUES:
                self.optimal_value = self.OPTIMAL_VALUES[self.name]
            
            print(f"✓ Parsed {self.name}: {self.dimension} nodes, optimal={self.optimal_value}")
            return True
            
        except Exception as e:
            print(f"✗ Error parsing {self.filepath}: {e}")
            return False
    
    def _extract_metadata(self, content: str):
        """Extract metadata from TSPLIB file."""
        # Name
        name_match = re.search(r'NAME\s*:\s*(.+)', content)
        if name_match:
            self.name = name_match.group(1).strip()
        
        # Dimension
        dim_match = re.search(r'DIMENSION\s*:\s*(\d+)', content)
        if dim_match:
            self.dimension = int(dim_match.group(1))
        
        # Edge weight type
        weight_match = re.search(r'EDGE_WEIGHT_TYPE\s*:\s*(.+)', content)
        if weight_match:
            self.edge_weight_type = weight_match.group(1).strip()
    
    def _extract_node_coords(self, content: str):
        """Extract node coordinates from TSPLIB file."""
        # Find NODE_COORD_SECTION
        coord_section_match = re.search(r'NODE_COORD_SECTION\s*(.+?)(?:EOF|$)', content, re.DOTALL)
        if not coord_section_match:
            return
        
        coord_section = coord_section_match.group(1)
        
        # Parse coordinates: node_id x y
        coord_pattern = re.compile(r'^\s*(\d+)\s+([\d\.]+)\s+([\d\.]+)\s*$', re.MULTILINE)
        matches = coord_pattern.findall(coord_section)
        
        self.node_coords = []
        for match in matches:
            node_id = int(match[0])
            x = float(match[1])
            y = float(match[2])
            self.node_coords.append((x, y))
        
        # Verify dimension matches
        if len(self.node_coords) != self.dimension:
            print(f"⚠️ Warning: Parsed {len(self.node_coords)} nodes but dimension is {self.dimension}")
    
    def get_distance_matrix(self) -> np.ndarray:
        """Calculate distance matrix based on edge weight type."""
        if not self.node_coords:
            return np.array([])
        
        n = len(self.node_coords)
        dist_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i + 1, n):
                x1, y1 = self.node_coords[i]
                x2, y2 = self.node_coords[j]
                
                if self.edge_weight_type == "ATT":
                    # ATT distance: ceil(sqrt(((x1 - x2)^2 + (y1 - y2)^2) / 10.0))
                    dx = x1 - x2
                    dy = y1 - y2
                    dist = np.ceil(np.sqrt((dx * dx + dy * dy) / 10.0))
                elif self.edge_weight_type == "EUC_2D":
                    # Euclidean distance rounded to nearest integer
                    dist = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
                    dist = np.round(dist)
                else:
                    # Default: Euclidean distance
                    dist = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
                
                dist_matrix[i, j] = dist
                dist_matrix[j, i] = dist
        
        return dist_matrix
    
    def calculate_gap(self, our_solution_length: float) -> float:
        """Calculate gap to optimal solution in percentage."""
        if self.optimal_value is None:
            print(f"⚠️ No optimal value known for {self.name}")
            return None
        
        if our_solution_length <= 0:
            return float('inf')
        
        gap = ((our_solution_length - self.optimal_value) / self.optimal_value) * 100.0
        return gap
    
    def get_points_array(self) -> np.ndarray:
        """Get points as numpy array for algorithm compatibility."""
        return np.array(self.node_coords)

def test_all_instances():
    """Test parser with all acquired TSPLIB instances."""
    print("=" * 80)
    print("TSPLIB Parser Validation - Testing All Acquired Instances")
    print("=" * 80)
    
    tsplib_dir = "/workspace/evovera/data/tsplib"
    instances = ["eil51", "kroA100", "a280", "att532"]
    
    success_count = 0
    failed_count = 0
    
    for instance_name in instances:
        filepath = os.path.join(tsplib_dir, f"{instance_name}.tsp")
        
        if not os.path.exists(filepath):
            print(f"\n❌ Missing: {filepath}")
            failed_count += 1
            continue
        
        print(f"\n📋 Testing {instance_name}...")
        parser = TSPLIBParser(filepath)
        
        if parser.parse():
            print(f"  ✓ Name: {parser.name}")
            print(f"  ✓ Dimension: {parser.dimension}")
            print(f"  ✓ Edge weight type: {parser.edge_weight_type}")
            print(f"  ✓ Optimal value: {parser.optimal_value}")
            print(f"  ✓ Coordinates parsed: {len(parser.node_coords)} points")
            
            # Test distance matrix calculation
            if parser.node_coords:
                dist_matrix = parser.get_distance_matrix()
                print(f"  ✓ Distance matrix shape: {dist_matrix.shape}")
                
                # Test gap calculation with a dummy value
                dummy_solution = parser.optimal_value * 1.1  # 10% worse
                gap = parser.calculate_gap(dummy_solution)
                print(f"  ✓ Gap calculation test: {gap:.2f}% (dummy: {dummy_solution:.1f})")
            
            success_count += 1
        else:
            print(f"  ❌ Failed to parse {instance_name}")
            failed_count += 1
    
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY:")
    print(f"  ✅ Successfully parsed: {success_count} instances")
    print(f"  ❌ Failed to parse: {failed_count} instances")
    
    if success_count == len(instances):
        print("\n🎉 ALL INSTANCES VALIDATED - Ready for TSPLIB evaluation!")
    else:
        print(f"\n⚠️  PARTIAL SUCCESS - {success_count}/{len(instances)} instances validated")
    
    print("\n" + "=" * 80)
    
    return success_count == len(instances)

def create_benchmark_integration_example():
    """Create example of how to integrate with existing benchmark framework."""
    print("\n" + "=" * 80)
    print("BENCHMARK INTEGRATION EXAMPLE")
    print("=" * 80)
    
    print("\n📋 Integration with existing TSP solvers:")
    print("""
# Example integration code:
def run_tsplib_benchmark(algorithm_func, instance_names):
    results = {}
    
    for instance_name in instance_names:
        # Parse instance
        parser = TSPLIBParser(f"data/tsplib/{instance_name}.tsp")
        parser.parse()
        
        # Get points for algorithm
        points = parser.get_points_array()
        
        # Run algorithm (compatible with existing TSP solvers)
        tour, length = algorithm_func(points)
        
        # Calculate gap to optimal
        gap = parser.calculate_gap(length)
        
        results[instance_name] = {
            "optimal": parser.optimal_value,
            "our_length": length,
            "gap_percent": gap,
            "points": len(points)
        }
    
    return results
""")
    
    print("\n📊 Expected output format:")
    print("""
TSPLIB Evaluation Results:
- eil51: Optimal=426, Our=440.2, Gap=3.33%
- kroA100: Optimal=21282, Our=22500.5, Gap=5.73%
- a280: Optimal=2579, Our=2800.1, Gap=8.57%
- att532: Optimal=27686, Our=29500.3, Gap=6.54%
""")
    
    print("\n🔧 Next steps:")
    print("  1. Integrate parser with existing benchmark framework")
    print("  2. Run NN+2opt baseline on all TSPLIB instances")
    print("  3. Run v19 algorithm on all TSPLIB instances")
    print("  4. Generate comparative analysis report")
    print("  5. Document findings for publication")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    # Test all instances
    all_valid = test_all_instances()
    
    if all_valid:
        # Show integration example
        create_benchmark_integration_example()
        
        print("\n✅ TSPLIB Parser ready for Phase 2 evaluation!")
        print("   Next: Integrate with benchmark framework and run evaluations.")
    else:
        print("\n❌ Parser validation failed. Need to fix issues before proceeding.")