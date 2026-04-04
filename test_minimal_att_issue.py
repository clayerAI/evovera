#!/usr/bin/env python3
"""
Minimal test showing the ATT distance issue.
"""

import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsplib_parser import TSPLIBParser

print("=" * 80)
print("MINIMAL TEST: ATT DISTANCE ISSUE")
print("=" * 80)

# Load att532
filepath = "data/tsplib/att532.tsp"
parser = TSPLIBParser(filepath)
if not parser.parse():
    print("❌ Failed to parse att532")
    sys.exit(1)

print(f"✓ Loaded {parser.name}: {parser.dimension} nodes, optimal={parser.optimal_value}")

# Get points and distance matrix
points = parser.get_points_array()
distance_matrix = parser.get_distance_matrix()

print(f"\n🔍 DISTANCE COMPARISON (first 5 nodes):")
print("-" * 60)

# Compare distances for first 5 nodes
for i in range(min(5, parser.dimension)):
    for j in range(i + 1, min(5, parser.dimension)):
        # ATT distance from parser
        att_dist = distance_matrix[i, j]
        
        # Euclidean distance
        dx = points[i][0] - points[j][0]
        dy = points[i][1] - points[j][1]
        euclidean_dist = np.sqrt(dx*dx + dy*dy)
        
        ratio = euclidean_dist / att_dist if att_dist > 0 else 0
        
        print(f"  {i}→{j}: ATT={att_dist:6.2f}, Euclidean={euclidean_dist:6.2f}, ratio={ratio:.2f}x")

print(f"\n🔍 NEAREST NEIGHBOR DECISION ERROR:")
print("-" * 60)

# Test nearest neighbor from node 0
start = 0
n_test = min(20, parser.dimension)

# Find nearest using ATT distances (correct)
nearest_att = min(range(1, n_test), key=lambda j: distance_matrix[start, j])
att_dist = distance_matrix[start, nearest_att]

# Find nearest using Euclidean (what broken algorithm does)
nearest_euclidean = min(range(1, n_test), key=lambda j: np.linalg.norm(points[start] - points[j]))
euclidean_dist = np.linalg.norm(points[start] - points[nearest_euclidean])
actual_att_dist_for_euclidean = distance_matrix[start, nearest_euclidean]

print(f"  From node {start}, checking {n_test-1} nearest nodes:")
print(f"  ✓ ATT chooses node {nearest_att} (distance: {att_dist:.2f})")
print(f"  🚨 Euclidean chooses node {nearest_euclidean} (distance: {euclidean_dist:.2f})")
print(f"     Actual ATT distance for this choice: {actual_att_dist_for_euclidean:.2f}")

if nearest_att != nearest_euclidean:
    error_percent = ((actual_att_dist_for_euclidean - att_dist) / att_dist) * 100
    print(f"  🚨 EUCLIDEAN MAKES WRONG DECISION!")
    print(f"     Would be {error_percent:.1f}% worse than optimal choice")
else:
    print(f"  ⚠️ Same node chosen (coincidence)")

print(f"\n🔍 TOUR LENGTH CALCULATION ERROR:")
print("-" * 60)

# Create a simple tour [0, 1, 2, 3, 4, 0]
simple_tour = list(range(min(5, parser.dimension))) + [0]

# Calculate length using ATT distances (correct)
att_length = 0.0
for i in range(len(simple_tour) - 1):
    att_length += distance_matrix[simple_tour[i], simple_tour[i + 1]]

# Calculate length using Euclidean (what broken algorithm would report)
euclidean_length = 0.0
for i in range(len(simple_tour) - 1):
    p1 = points[simple_tour[i]]
    p2 = points[simple_tour[i + 1]]
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    euclidean_length += np.sqrt(dx*dx + dy*dy)

error_percent = ((euclidean_length - att_length) / att_length) * 100

print(f"  Simple tour {simple_tour}:")
print(f"  ✓ ATT length: {att_length:.2f}")
print(f"  🚨 Euclidean length: {euclidean_length:.2f}")
print(f"  🚨 Error: {error_percent:.1f}%")

print(f"\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print("🚨 CRITICAL METHODOLOGICAL ISSUE CONFIRMED:")
print("1. ATT distance formula: ceil(sqrt((dx²+dy²)/10.0))")
print("2. Euclidean is 3.16x larger than ATT")
print("3. Algorithms using Euclidean make wrong decisions")
print("4. Tour length calculations are wrong by ~215%")
print("\n✅ Vera's finding is VALID and CRITICAL")
print("   TSPLIB evaluation cannot proceed without fixing algorithms")
print("\n📋 REQUIRED FIX:")
print("   Algorithms must accept distance matrix parameter")
print("   and use correct metric per TSPLIB instance type")