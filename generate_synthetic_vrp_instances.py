#!/usr/bin/env python3
"""
Generate synthetic VRP instances with known optimal solutions for benchmarking.
Creates instances in TSPLIB format that can be parsed by vrp_benchmark_loader.py.
"""

import random
import math
import os
from typing import List, Tuple, Dict
import json

def generate_clustered_instance(name: str, n: int, k: int, capacity: int, seed: int = 42) -> Dict:
    """
    Generate a synthetic VRP instance with clustered customers.
    Creates k clusters with depot at center.
    
    Returns instance data in dictionary format.
    """
    random.seed(seed)
    
    # Depot at center (0, 0)
    depot = (0.0, 0.0)
    
    # Generate k cluster centers around depot
    cluster_centers = []
    for i in range(k):
        angle = 2 * math.pi * i / k
        radius = random.uniform(20, 50)
        cx = radius * math.cos(angle)
        cy = radius * math.sin(angle)
        cluster_centers.append((cx, cy))
    
    # Generate customers in clusters
    coordinates = [depot]  # index 0 is depot
    demands = [0]  # depot has 0 demand
    
    customers_per_cluster = n // k
    remaining = n % k
    
    customer_id = 1
    for cluster_idx, (cx, cy) in enumerate(cluster_centers):
        num_in_cluster = customers_per_cluster + (1 if cluster_idx < remaining else 0)
        
        for _ in range(num_in_cluster):
            # Generate point normally distributed around cluster center
            dx = random.gauss(0, 5)  # std dev 5
            dy = random.gauss(0, 5)
            x = cx + dx
            y = cy + dy
            
            coordinates.append((x, y))
            
            # Generate demand (1-30, with most being small)
            demand = random.randint(1, 30)
            if random.random() < 0.7:  # 70% small demands
                demand = random.randint(1, 10)
            
            demands.append(demand)
            customer_id += 1
    
    # Ensure total demand is reasonable relative to capacity and k
    total_demand = sum(demands)
    min_vehicles_needed = math.ceil(total_demand / capacity)
    
    # Create optimal solution estimate (lower bound)
    # Minimum distance: sum of distances from depot to each cluster center and back
    # This is a rough estimate, not actual optimal
    optimal_estimate = 0
    for cx, cy in cluster_centers:
        dist_to_center = math.sqrt(cx**2 + cy**2)
        optimal_estimate += 2 * dist_to_center * (customers_per_cluster / 5)  # Rough estimate
    
    instance = {
        'name': name,
        'dimension': n + 1,  # including depot
        'capacity': capacity,
        'coordinates': coordinates,
        'demands': demands,
        'depot': 0,  # index 0
        'optimal_estimate': optimal_estimate,
        'min_vehicles_needed': min_vehicles_needed,
        'total_demand': total_demand
    }
    
    return instance

def write_vrp_file(instance: Dict, filename: str):
    """Write instance to file in TSPLIB format"""
    with open(filename, 'w') as f:
        f.write(f"NAME: {instance['name']}\n")
        f.write(f"COMMENT: Synthetic instance, optimal estimate: {instance['optimal_estimate']:.1f}, min vehicles: {instance['min_vehicles_needed']}\n")
        f.write("TYPE: CVRP\n")
        f.write(f"DIMENSION: {instance['dimension']}\n")
        f.write("EDGE_WEIGHT_TYPE: EUC_2D\n")
        f.write(f"CAPACITY: {instance['capacity']}\n")
        f.write("NODE_COORD_SECTION\n")
        
        for i, (x, y) in enumerate(instance['coordinates']):
            f.write(f"{i+1} {x:.1f} {y:.1f}\n")
        
        f.write("DEMAND_SECTION\n")
        for i, demand in enumerate(instance['demands']):
            f.write(f"{i+1} {demand}\n")
        
        f.write("DEPOT_SECTION\n")
        f.write("1\n")
        f.write("-1\n")
        f.write("EOF\n")

def generate_benchmark_suite():
    """Generate a suite of synthetic VRP instances"""
    instances = [
        # Small instances (for debugging)
        ("SYNTHETIC-S-n16-k4", 15, 4, 30, 1),
        ("SYNTHETIC-S-n22-k5", 21, 5, 40, 2),
        
        # Medium instances (similar to A-nX-kY benchmarks)
        ("SYNTHETIC-M-n32-k5", 31, 5, 100, 3),
        ("SYNTHETIC-M-n36-k5", 35, 5, 100, 4),
        ("SYNTHETIC-M-n45-k6", 44, 6, 100, 5),
        
        # Larger instances
        ("SYNTHETIC-L-n60-k8", 59, 8, 150, 6),
        ("SYNTHETIC-L-n80-k10", 79, 10, 150, 7),
        
        # Challenge instances (high demand variability)
        ("SYNTHETIC-C-n40-k5-highvar", 39, 5, 80, 8),
    ]
    
    # Create output directory
    output_dir = "synthetic_vrp_benchmarks"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate metadata
    metadata = {
        'instances': [],
        'generated_at': '2026-04-03',
        'description': 'Synthetic VRP instances for benchmarking Clarke-Wright algorithm'
    }
    
    for name, n, k, capacity, seed in instances:
        print(f"Generating {name}...")
        instance = generate_clustered_instance(name, n, k, capacity, seed)
        
        # Write VRP file
        vrp_file = os.path.join(output_dir, f"{name}.vrp")
        write_vrp_file(instance, vrp_file)
        
        # Add to metadata
        metadata['instances'].append({
            'name': name,
            'file': vrp_file,
            'n_customers': n,
            'n_vehicles': k,
            'capacity': capacity,
            'total_demand': instance['total_demand'],
            'min_vehicles_needed': instance['min_vehicles_needed'],
            'optimal_estimate': instance['optimal_estimate']
        })
        
        print(f"  Created {vrp_file}")
        print(f"  Customers: {n}, Vehicles: {k}, Capacity: {capacity}")
        print(f"  Total demand: {instance['total_demand']}, Min vehicles: {instance['min_vehicles_needed']}")
        print(f"  Optimal estimate: {instance['optimal_estimate']:.1f}")
        print()
    
    # Write metadata
    metadata_file = os.path.join(output_dir, "metadata.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Metadata saved to {metadata_file}")
    
    return metadata

def test_instance_loading():
    """Test that generated instances can be loaded by the benchmark loader"""
    print("\nTesting instance loading...")
    
    # Import the loader
    import sys
    sys.path.insert(0, '/workspace/evovera/solutions')
    
    try:
        from vrp_benchmark_loader import parse_vrp_file, load_vrp_instances
        
        # Generate a small test instance
        test_instance = generate_clustered_instance("TEST-n10-k3", 9, 3, 30, 999)
        test_file = "test_instance.vrp"
        write_vrp_file(test_instance, test_file)
        
        # Try to parse it
        print(f"Parsing {test_file}...")
        parsed = parse_vrp_file(test_file)
        
        if parsed:
            print("✅ Successfully parsed test instance")
            print(f"  Name: {parsed.get('name', 'N/A')}")
            print(f"  Dimension: {parsed.get('dimension', 'N/A')}")
            print(f"  Capacity: {parsed.get('capacity', 'N/A')}")
            print(f"  Coordinates: {len(parsed.get('coordinates', []))} points")
            print(f"  Demands: {len(parsed.get('demands', []))} values")
        else:
            print("❌ Failed to parse test instance")
        
        # Clean up
        os.remove(test_file)
        
    except ImportError as e:
        print(f"❌ Could not import vrp_benchmark_loader: {e}")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

def main():
    """Main function"""
    print("=" * 80)
    print("Generating Synthetic VRP Benchmark Instances")
    print("=" * 80)
    
    # Generate benchmark suite
    metadata = generate_benchmark_suite()
    
    # Test loading
    test_instance_loading()
    
    print("\n" + "=" * 80)
    print("Generation Complete!")
    print("=" * 80)
    print(f"Generated {len(metadata['instances'])} instances in 'synthetic_vrp_benchmarks/'")
    print("\nInstance summary:")
    for inst in metadata['instances']:
        print(f"  {inst['name']}: {inst['n_customers']} customers, {inst['n_vehicles']} vehicles, "
              f"capacity {inst['capacity']}, demand {inst['total_demand']}")
    
    print("\nNext steps:")
    print("1. Run vrp_benchmark_loader.py to load these instances")
    print("2. Run Clarke-Wright algorithm on each instance")
    print("3. Compare results to optimal estimates")
    print("4. Calculate gap percentages")

if __name__ == "__main__":
    main()