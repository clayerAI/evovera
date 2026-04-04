#!/usr/bin/env python3
"""
TSPLIB Parser Template for Phase 2 evaluation.
This template will be completed once TSPLIB instances are acquired.
"""

import re
import os
from typing import Dict, List, Tuple, Optional

class TSPLIBParser:
    """Parser for TSPLIB format instances."""
    
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
            
            print(f"✓ Parsed {self.name}: {self.dimension} nodes")
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
        
        # Optimal value (if present in comment)
        opt_match = re.search(r'OPTIMAL\s*:\s*(\d+)', content, re.IGNORECASE)
        if opt_match:
            self.optimal_value = int(opt_match.group(1))
    
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
    
    def get_distance_matrix(self) -> List[List[float]]:
        """Calculate Euclidean distance matrix."""
        if not self.node_coords:
            return []
        
        n = len(self.node_coords)
        dist_matrix = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(i + 1, n):
                x1, y1 = self.node_coords[i]
                x2, y2 = self.node_coords[j]
                dist = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
                dist_matrix[i][j] = dist
                dist_matrix[j][i] = dist
        
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

def test_parser():
    """Test function to demonstrate parser usage."""
    print("=" * 80)
    print("TSPLIB Parser Template - Test Demonstration")
    print("=" * 80)
    
    # Example of what the parser will do once instances are available
    print("\n📋 Parser capabilities:")
    print("  1. Parse TSPLIB format files (.tsp, .txt)")
    print("  2. Extract metadata (name, dimension, edge weight type)")
    print("  3. Read node coordinates")
    print("  4. Calculate distance matrix")
    print("  5. Compute gap to optimal solution")
    
    print("\n🔧 Integration with existing framework:")
    print("  • Will work with current TSP solver implementations")
    print("  • Can replace random instance generation with real instances")
    print("  • Gap-to-optimal will be new primary metric")
    
    print("\n📊 Expected output format:")
    print("  Instance: eil51 (51 nodes)")
    print("  Optimal: 426")
    print("  Our solution: 440 (3.29% gap)")
    print("  Runtime: 0.5s")
    
    print("\n⚠️ Current status:")
    print("  • Parser template created")
    print("  • Waiting for TSPLIB instance files")
    print("  • Ready for integration once instances are available")
    
    print("\n" + "=" * 80)
    print("✅ Parser template ready. Requires TSPLIB instance files.")
    print("=" * 80)

if __name__ == "__main__":
    test_parser()