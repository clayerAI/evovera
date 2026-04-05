#!/usr/bin/env python3
"""
TSPLIB Parser for Phase 2 evaluation.
Updated with all required instances including d198, lin318, pr439.
"""

import re
import os
import numpy as np
from typing import Dict, List, Tuple, Optional

class TSPLIBParser:
    """Parser for TSPLIB format instances."""
    
    # Known optimal solutions for all required instances
    OPTIMAL_VALUES = {
        "eil51": 426,
        "kroA100": 21282,
        "a280": 2579,
        "att532": 27686,
        "d198": 15780,
        "lin318": 42029,
        "pr439": 107217,
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
            print(f"✗ Failed to parse {self.filepath}: {e}")
            return False
    
    def _extract_metadata(self, content: str):
        """Extract metadata from TSPLIB file."""
        # Extract NAME
        name_match = re.search(r'NAME\s*:\s*(\S+)', content, re.IGNORECASE)
        if name_match:
            self.name = name_match.group(1).strip()
        
        # Extract DIMENSION
        dim_match = re.search(r'DIMENSION\s*:\s*(\d+)', content, re.IGNORECASE)
        if dim_match:
            self.dimension = int(dim_match.group(1))
        
        # Extract EDGE_WEIGHT_TYPE
        ewt_match = re.search(r'EDGE_WEIGHT_TYPE\s*:\s*(\S+)', content, re.IGNORECASE)
        if ewt_match:
            self.edge_weight_type = ewt_match.group(1).strip()
        
        # Extract BEST_KNOWN (if present)
        best_match = re.search(r'BEST_KNOWN\s*:\s*(\d+)', content, re.IGNORECASE)
        if best_match and not self.optimal_value:
            self.optimal_value = int(best_match.group(1))
    
    def _extract_node_coords(self, content: str):
        """Extract node coordinates from NODE_COORD_SECTION."""
        # Find NODE_COORD_SECTION
        coord_section_match = re.search(r'NODE_COORD_SECTION\s*(.*?)\s*EOF', content, re.DOTALL | re.IGNORECASE)
        if not coord_section_match:
            coord_section_match = re.search(r'NODE_COORD_SECTION\s*(.*)', content, re.DOTALL | re.IGNORECASE)
        
        if coord_section_match:
            coord_text = coord_section_match.group(1).strip()
            lines = coord_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Parse node coordinates (format: index x y)
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        # Some files use scientific notation
                        x = float(parts[1])
                        y = float(parts[2])
                        self.node_coords.append((x, y))
                    except ValueError:
                        continue
    
    def get_distance_matrix(self) -> np.ndarray:
        """Compute Euclidean distance matrix."""
        if not self.node_coords:
            raise ValueError("No coordinates parsed")
        
        n = len(self.node_coords)
        dist_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    dx = self.node_coords[i][0] - self.node_coords[j][0]
                    dy = self.node_coords[i][1] - self.node_coords[j][1]
                    
                    # Handle ATT special metric
                    if self.edge_weight_type == "ATT":
                        # ATT distance: ceil(sqrt((dx²+dy²)/10.0))
                        dist = np.ceil(np.sqrt((dx*dx + dy*dy) / 10.0))
                    else:
                        # EUC_2D: rounded Euclidean
                        dist = np.sqrt(dx*dx + dy*dy)
                        dist = int(dist + 0.5)  # Round to nearest integer
                    
                    dist_matrix[i][j] = dist
        
        return dist_matrix
    
    def get_coordinates(self) -> List[Tuple[float, float]]:
        """Return list of coordinates."""
        return self.node_coords

def parse_tsplib_file(filepath: str) -> Tuple[List[Tuple[float, float]], Optional[int]]:
    """Convenience function to parse TSPLIB file and return coordinates and optimal value."""
    parser = TSPLIBParser(filepath)
    if parser.parse():
        return parser.get_coordinates(), parser.optimal_value
    else:
        raise ValueError(f"Failed to parse {filepath}")

if __name__ == "__main__":
    # Test with all instances
    tsplib_dir = "data/tsplib"
    instances = ["eil51.tsp", "kroA100.tsp", "a280.tsp", "att532.tsp", 
                 "d198.tsp", "lin318.tsp", "pr439.tsp"]
    
    print("Testing TSPLIB parser with all instances:")
    print("=" * 60)
    
    for instance in instances:
        filepath = os.path.join(tsplib_dir, instance)
        if os.path.exists(filepath):
            parser = TSPLIBParser(filepath)
            if parser.parse():
                print(f"  {instance}: {parser.dimension} nodes, {parser.edge_weight_type}, optimal={parser.optimal_value}")
            else:
                print(f"  {instance}: FAILED")
        else:
            print(f"  {instance}: File not found")
