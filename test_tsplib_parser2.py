import sys
sys.path.append('.')
from tsplib_parser import TSPLIBParser

# Test loading eil51
parser = TSPLIBParser("data/tsplib/eil51.tsp")
success = parser.parse()

if success:
    print(f"Successfully loaded eil51")
    print(f"Number of nodes: {parser.dimension}")
    print(f"Edge weight type: {parser.edge_weight_type}")
    print(f"Node coords shape: {len(parser.node_coords)}")
    print(f"First 5 nodes: {parser.node_coords[:5]}")
    
    # Calculate distance matrix
    import numpy as np
    n = parser.dimension
    points = np.array(parser.node_coords)
    
    # Use the same calculation as in the script
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            
            if parser.edge_weight_type == "EUC_2D":
                # Euclidean distance rounded to nearest integer
                dist = round(np.sqrt(dx*dx + dy*dy))
            else:
                dist = round(np.sqrt(dx*dx + dy*dy))
            
            dist_matrix[i][j] = dist
            dist_matrix[j][i] = dist
    
    print(f"\nDistance matrix shape: {dist_matrix.shape}")
    print(f"Sample distances from node 0: {dist_matrix[0][:5]}")
    print(f"Min distance (non-zero): {dist_matrix[dist_matrix > 0].min()}")
    print(f"Max distance: {dist_matrix.max()}")
    print(f"Diagonal (should be 0): {np.diag(dist_matrix)[:5]}")
    
    # Check for any zeros in non-diagonal positions
    zero_count = 0
    for i in range(n):
        for j in range(n):
            if i != j and dist_matrix[i][j] == 0:
                zero_count += 1
    if zero_count > 0:
        print(f"WARNING: Found {zero_count} zero distances in non-diagonal positions!")
    
else:
    print("Failed to load eil51")
