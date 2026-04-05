#!/usr/bin/env python3
"""Test evaluation on one instance."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from evaluate_v11_tsplib_complete_fixed_optimized import evaluate_instance

# Test on d198 (medium instance)
print("Testing evaluation on d198...")
results = evaluate_instance("d198", "data/tsplib/d198.tsp", 15780, seeds=2)
print(f"Results: {results}")
