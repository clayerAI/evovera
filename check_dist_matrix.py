#!/usr/bin/env python3
"""Check distance matrix format."""

import sys
sys.path.append('.')

from tsplib_parser import TSPLIBParser

parser = TSPLIBParser("data/tsplib/eil51.tsp")
parser.parse()
dist_matrix = parser.get_distance_matrix()

print(f"Distance matrix type: {type(dist_matrix)}")
print(f"Distance matrix shape: {dist_matrix.shape}")
print(f"First few values:")
print(f"  dist_matrix[0][0] = {dist_matrix[0][0]}")
print(f"  dist_matrix[0][1] = {dist_matrix[0][1]}")
print(f"  dist_matrix[1][0] = {dist_matrix[1][0]}")
print(f"  dist_matrix[0][50] = {dist_matrix[0][50]}")
print(f"  dist_matrix[50][0] = {dist_matrix[50][0]}")

# Check if it's symmetric
is_symmetric = True
for i in range(min(5, len(dist_matrix))):
    for j in range(min(5, len(dist_matrix))):
        if dist_matrix[i][j] != dist_matrix[j][i]:
            is_symmetric = False
            print(f"  Not symmetric at ({i},{j}): {dist_matrix[i][j]} != {dist_matrix[j][i]}")
print(f"Symmetric: {is_symmetric}")

# Check data type
print(f"Element type: {type(dist_matrix[0][0])}")
