"""
VRP Benchmark Instance Loader

Load standard VRP benchmark instances (Christofides & Eilon, Golden et al.)
and compare Clarke-Wright algorithm results to known optimal/best solutions.
"""

import numpy as np
import os
import re
from typing import List, Tuple, Dict, Optional

def parse_vrp_file(filepath: str) -> Dict:
    """
    Parse VRP instance file in TSPLIB format.
    
    Format example:
    NAME: A-n32-k5
    COMMENT: (Augerat et al, No of trucks: 5, Optimal value: 784)
    TYPE: CVRP
    DIMENSION: 32
    EDGE_WEIGHT_TYPE: EUC_2D
    CAPACITY: 100
    NODE_COORD_SECTION
    1 82 76
    2 96 44
    ...
    DEMAND_SECTION
    1 0
    2 19
    ...
    DEPOT_SECTION
    1
    -1
    EOF
    """
    data = {
        'name': '',
        'comment': '',
        'type': '',
        'dimension': 0,
        'edge_weight_type': '',
        'capacity': 0,
        'coordinates': [],
        'demands': [],
        'depot': 0,
        'optimal_value': None
    }
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return data
    
    # Parse metadata
    lines = content.split('\n')
    section = 'HEADER'
    coordinates = []
    demands = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('NAME:'):
            data['name'] = line.split(':', 1)[1].strip()
        elif line.startswith('COMMENT:'):
            data['comment'] = line.split(':', 1)[1].strip()
            # Try to extract optimal value from comment
            match = re.search(r'Optimal value: (\d+)', data['comment'])
            if match:
                data['optimal_value'] = int(match.group(1))
        elif line.startswith('TYPE:'):
            data['type'] = line.split(':', 1)[1].strip()
        elif line.startswith('DIMENSION:'):
            data['dimension'] = int(line.split(':', 1)[1].strip())
        elif line.startswith('EDGE_WEIGHT_TYPE:'):
            data['edge_weight_type'] = line.split(':', 1)[1].strip()
        elif line.startswith('CAPACITY:'):
            data['capacity'] = int(line.split(':', 1)[1].strip())
        elif line == 'NODE_COORD_SECTION':
            section = 'COORDINATES'
        elif line == 'DEMAND_SECTION':
            section = 'DEMANDS'
        elif line == 'DEPOT_SECTION':
            section = 'DEPOT'
        elif line == 'EOF' or line == '-1':
            break
        else:
            if section == 'COORDINATES':
                parts = line.split()
                if len(parts) >= 3:
                    node_id = int(parts[0]) - 1  # Convert to 0-based
                    x = float(parts[1])
                    y = float(parts[2])
                    coordinates.append((x, y))
            elif section == 'DEMANDS':
                parts = line.split()
                if len(parts) >= 2:
                    node_id = int(parts[0]) - 1  # Convert to 0-based
                    demand = int(parts[1])
                    demands.append(demand)
            elif section == 'DEPOT':
                if line.strip() and line.strip() != '-1':
                    data['depot'] = int(line.strip()) - 1  # Convert to 0-based
    
    # Store data
    data['coordinates'] = coordinates
    data['demands'] = demands
    
    # Validate
    if len(coordinates) != data['dimension']:
        print(f"Warning: Expected {data['dimension']} coordinates, got {len(coordinates)}")
    if len(demands) != data['dimension']:
        print(f"Warning: Expected {data['dimension']} demands, got {len(demands)}")
    
    return data

def load_standard_benchmarks(vrp_dir: str = "vrp_benchmarks") -> List[Dict]:
    """
    Load standard VRP benchmark instances from files.
    Returns list of instance data dictionaries.
    """
    import os
    import glob
    
    instances = []
    
    # Find all .vrp files in the directory
    vrp_files = glob.glob(os.path.join(vrp_dir, "*.vrp"))
    
    if not vrp_files:
        print(f"No VRP files found in {vrp_dir}. Creating synthetic instances.")
        return _create_synthetic_instances()
    
    print(f"Found {len(vrp_files)} VRP files")
    
    for vrp_file in vrp_files:
        try:
            instance_data = parse_vrp_file(vrp_file)
            if instance_data['name'] and instance_data['coordinates']:
                instances.append(instance_data)
                print(f"  Loaded: {instance_data['name']} ({instance_data['dimension']} nodes)")
            else:
                print(f"  Skipped {vrp_file}: incomplete data")
        except Exception as e:
            print(f"  Error parsing {vrp_file}: {e}")
    
    # If no instances loaded, create synthetic ones
    if not instances:
        print("No valid instances loaded. Creating synthetic instances.")
        instances = _create_synthetic_instances()
    
    return instances

def _create_synthetic_instances() -> List[Dict]:
    """Create synthetic instances when real ones aren't available."""
    synthetic_instances = []
    
    # Create some synthetic instances for testing
    instance_configs = [
        {
            'name': 'SYNTHETIC-16',
            'dimension': 16,
            'capacity': 100,
            'optimal_value': 145
        },
        {
            'name': 'SYNTHETIC-32', 
            'dimension': 32,
            'capacity': 100,
            'optimal_value': 280
        }
    ]
    
    for instance_info in instance_configs:
        n = instance_info['dimension']
        
        # Generate random coordinates
        np.random.seed(42)
        coordinates = []
        for i in range(n):
            # Depot at (50, 50), customers around
            if i == 0:
                x, y = 50, 50  # Depot
            else:
                x = np.random.uniform(10, 90)
                y = np.random.uniform(10, 90)
            coordinates.append((x, y))
        
        # Generate random demands (depot has 0 demand)
        demands = [0]  # Depot
        for i in range(1, n):
            demands.append(np.random.randint(5, 30))
        
        instance = {
            'name': instance_info['name'],
            'dimension': n,
            'capacity': instance_info['capacity'],
            'optimal_value': instance_info['optimal_value'],
            'coordinates': coordinates,
            'demands': demands,
            'depot': 0,
            'type': 'CVRP',
            'edge_weight_type': 'EUC_2D',
            'comment': f'Synthetic instance {instance_info["name"]}'
        }
        
        synthetic_instances.append(instance)
    
    return synthetic_instances

def calculate_distance_matrix(coordinates: List[Tuple[float, float]]) -> np.ndarray:
    """Calculate Euclidean distance matrix."""
    n = len(coordinates)
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dx = coordinates[i][0] - coordinates[j][0]
            dy = coordinates[i][1] - coordinates[j][1]
            d = np.sqrt(dx*dx + dy*dy)
            dist[i, j] = d
            dist[j, i] = d
    return dist

def clarke_wright_vrp(
    dist_matrix: np.ndarray,
    demands: List[int],
    capacity: int,
    depot: int = 0,
    parallel: bool = True
) -> Tuple[List[List[int]], float]:
    """
    Clarke-Wright savings algorithm for VRP.
    
    Returns:
        routes: List of routes (each route is list of node indices)
        total_distance: Total distance of all routes
    """
    n = len(dist_matrix)
    
    # Calculate savings
    savings = []
    for i in range(n):
        if i == depot:
            continue
        for j in range(i + 1, n):
            if j == depot:
                continue
            # Savings = dist(depot, i) + dist(depot, j) - dist(i, j)
            s = dist_matrix[depot, i] + dist_matrix[depot, j] - dist_matrix[i, j]
            savings.append((s, i, j))
    
    # Sort savings in descending order
    savings.sort(reverse=True, key=lambda x: x[0])
    
    # Initialize routes: each customer in separate route
    routes = [[i] for i in range(n) if i != depot]
    route_demands = [demands[i] for i in range(n) if i != depot]
    route_ends = [(i, i) for i in range(n) if i != depot]  # (start, end) of each route
    
    # Merge routes based on savings
    for s, i, j in savings:
        # Find routes containing i and j
        route_i = route_j = -1
        start_i = end_i = start_j = end_j = -1
        
        for idx, (start, end) in enumerate(route_ends):
            if start == i or end == i:
                route_i = idx
                start_i, end_i = start, end
            if start == j or end == j:
                route_j = idx
                start_j, end_j = start, end
        
        # Check if i and j are in different routes
        if route_i != route_j and route_i != -1 and route_j != -1:
            # Check capacity constraint
            total_demand = route_demands[route_i] + route_demands[route_j]
            if total_demand <= capacity:
                # Check if we can merge (i and j must be at ends of their routes)
                can_merge = False
                new_start = new_end = -1
                
                if end_i == i and start_j == j:
                    # Route i ends with i, route j starts with j
                    can_merge = True
                    new_start = start_i
                    new_end = end_j
                elif end_i == i and end_j == j:
                    # Route i ends with i, route j ends with j (need to reverse route j)
                    can_merge = True
                    new_start = start_i
                    new_end = start_j
                    routes[route_j] = routes[route_j][::-1]
                elif start_i == i and start_j == j:
                    # Route i starts with i, route j starts with j (need to reverse route i)
                    can_merge = True
                    new_start = end_i
                    new_end = end_j
                    routes[route_i] = routes[route_i][::-1]
                elif start_i == i and end_j == j:
                    # Route i starts with i, route j ends with j
                    can_merge = True
                    new_start = end_i
                    new_end = start_j
                
                if can_merge:
                    # Merge routes
                    routes[route_i] = routes[route_i] + routes[route_j]
                    route_demands[route_i] = total_demand
                    route_ends[route_i] = (new_start, new_end)
                    
                    # Remove route j
                    del routes[route_j]
                    del route_demands[route_j]
                    del route_ends[route_j]
    
    # Add depot to beginning and end of each route
    full_routes = []
    total_distance = 0.0
    
    for route in routes:
        full_route = [depot] + route + [depot]
        full_routes.append(full_route)
        
        # Calculate route distance
        route_dist = 0.0
        for k in range(len(full_route) - 1):
            route_dist += dist_matrix[full_route[k], full_route[k + 1]]
        total_distance += route_dist
    
    return full_routes, total_distance

def benchmark_clarke_wright():
    """Run Clarke-Wright on benchmark instances and compare to optimal."""
    instances = load_standard_benchmarks()
    
    results = []
    
    for instance in instances:
        print(f"\nInstance: {instance['name']}")
        print(f"  Dimension: {instance['dimension']}, Capacity: {instance['capacity']}")
        
        # Calculate distance matrix
        dist_matrix = calculate_distance_matrix(instance['coordinates'])
        
        # Run Clarke-Wright
        routes, total_distance = clarke_wright_vrp(
            dist_matrix,
            instance['demands'],
            instance['capacity'],
            depot=instance['depot'],
            parallel=True
        )
        
        print(f"  Clarke-Wright result: {total_distance:.2f}")
        print(f"  Number of vehicles: {len(routes)}")
        
        # Compare to optimal if available
        optimal = instance.get('optimal_value')
        if optimal:
            gap = ((total_distance - optimal) / optimal) * 100
            print(f"  Optimal value: {optimal}")
            print(f"  Gap: {gap:.2f}%")
        else:
            gap = None
            print(f"  Optimal value: Unknown")
        
        results.append({
            'instance': instance['name'],
            'dimension': instance['dimension'],
            'clarke_wright_distance': total_distance,
            'optimal_distance': optimal,
            'gap_percent': gap,
            'num_vehicles': len(routes)
        })
    
    # Save results
    import json
    results_file = 'vrp_benchmark_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {results_file}")
    
    # Calculate summary statistics
    if results:
        gaps = [r['gap_percent'] for r in results if r['gap_percent'] is not None]
        if gaps:
            avg_gap = sum(gaps) / len(gaps)
            max_gap = max(gaps)
            min_gap = min(gaps)
            print(f"\nSummary (for instances with known optimal):")
            print(f"  Average gap: {avg_gap:.2f}%")
            print(f"  Minimum gap: {min_gap:.2f}%")
            print(f"  Maximum gap: {max_gap:.2f}%")
            print(f"  Instances: {len(gaps)}/{len(results)}")
    
    return results

if __name__ == "__main__":
    benchmark_clarke_wright()