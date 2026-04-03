#!/usr/bin/env python3
"""Download VRP benchmark instances from standard repositories."""

import os
import urllib.request
import zipfile
import io
import ssl
import time

def download_cvrplib_instances():
    """Download instances from CVRPLIB (Capacitated VRP Library)."""
    print("Downloading CVRPLIB instances...")
    
    # CVRPLIB instances (Christofides & Eilon, Golden et al.)
    # Let's start with a smaller subset for testing
    instances = [
        "A-n32-k5.vrp",
        "A-n33-k5.vrp", 
        "A-n33-k6.vrp",
        "A-n34-k5.vrp",
        "A-n36-k5.vrp",
        "A-n37-k5.vrp",
        "A-n37-k6.vrp",
        "A-n38-k5.vrp",
        "A-n39-k5.vrp",
        "A-n39-k6.vrp",
    ]
    
    base_url = "http://vrp.atd-lab.inf.puc-rio.br/media/com_vrp/instances/"
    
    # Create SSL context that doesn't verify certificates (for testing)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    successful = 0
    for instance in instances:
        url = base_url + instance
        local_path = os.path.join("vrp_benchmarks", instance)
        
        try:
            print(f"  Downloading {instance}...", end="")
            # Use custom opener with SSL context
            opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
            urllib.request.install_opener(opener)
            
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as response:
                with open(local_path, 'wb') as f:
                    f.write(response.read())
            print(f" OK")
            successful += 1
            time.sleep(0.5)  # Be polite to server
        except Exception as e:
            print(f" FAILED: {e}")
    
    print(f"CVRPLIB download complete: {successful}/{len(instances)} instances downloaded.")

def download_from_github():
    """Download VRP instances from GitHub repositories as fallback."""
    print("\nTrying GitHub repositories as fallback...")
    
    # Known GitHub repositories with VRP instances
    github_urls = [
        "https://raw.githubusercontent.com/coin-or/jorlib/master/jorlib-core/src/test/resources/vrp/A-n32-k5.vrp",
        "https://raw.githubusercontent.com/coin-or/jorlib/master/jorlib-core/src/test/resources/vrp/A-n33-k5.vrp",
        "https://raw.githubusercontent.com/coin-or/jorlib/master/jorlib-core/src/test/resources/vrp/A-n33-k6.vrp",
    ]
    
    successful = 0
    for url in github_urls:
        try:
            filename = os.path.basename(url)
            local_path = os.path.join("vrp_benchmarks", filename)
            
            if os.path.exists(local_path):
                print(f"  {filename} already exists, skipping")
                successful += 1
                continue
                
            print(f"  Downloading {filename}...", end="")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as response:
                with open(local_path, 'wb') as f:
                    f.write(response.read())
            print(f" OK")
            successful += 1
            time.sleep(0.5)
        except Exception as e:
            print(f" FAILED: {e}")
    
    return successful

def create_synthetic_instances():
    """Create synthetic VRP instances for testing."""
    print("\nCreating synthetic VRP instances...")
    
    # Create some simple synthetic instances
    synthetic_instances = [
        ("synthetic_10_2.vrp", 10, 2, 50),
        ("synthetic_20_3.vrp", 20, 3, 100),
        ("synthetic_30_4.vrp", 30, 4, 150),
        ("synthetic_40_5.vrp", 40, 5, 200),
        ("synthetic_50_6.vrp", 50, 6, 250),
    ]
    
    for filename, n_customers, n_vehicles, capacity in synthetic_instances:
        path = os.path.join("vrp_benchmarks", filename)
        if os.path.exists(path):
            print(f"  {filename} already exists, skipping")
            continue
            
        with open(path, 'w') as f:
            f.write(f"NAME: {filename}\n")
            f.write(f"COMMENT: Synthetic VRP instance with {n_customers} customers, {n_vehicles} vehicles\n")
            f.write(f"TYPE: CVRP\n")
            f.write(f"DIMENSION: {n_customers + 1}\n")  # +1 for depot
            f.write(f"EDGE_WEIGHT_TYPE: EUC_2D\n")
            f.write(f"CAPACITY: {capacity}\n")
            f.write(f"NODE_COORD_SECTION\n")
            
            # Depot at (0, 0)
            f.write(f"1 0 0\n")
            
            # Customers at random locations
            import random
            random.seed(42)
            for i in range(2, n_customers + 2):
                x = random.randint(0, 100)
                y = random.randint(0, 100)
                f.write(f"{i} {x} {y}\n")
            
            f.write(f"DEMAND_SECTION\n")
            f.write(f"1 0\n")  # Depot has 0 demand
            for i in range(2, n_customers + 2):
                demand = random.randint(1, 30)
                f.write(f"{i} {demand}\n")
            
            f.write(f"DEPOT_SECTION\n")
            f.write(f"1\n")
            f.write(f"-1\n")
            f.write(f"EOF\n")
        
        print(f"  Created {filename}")

def main():
    """Main download function."""
    # Create directory if it doesn't exist
    os.makedirs("vrp_benchmarks", exist_ok=True)
    
    print("VRP Benchmark Downloader")
    print("=" * 60)
    
    # Try to download real instances
    real_downloaded = 0
    try:
        download_cvrplib_instances()
        real_downloaded += 10  # We tried 10 instances
    except Exception as e:
        print(f"Failed to download CVRPLIB instances: {e}")
        print("Trying GitHub fallback...")
        try:
            real_downloaded = download_from_github()
        except Exception as e2:
            print(f"GitHub fallback also failed: {e2}")
            real_downloaded = 0
    
    # Always create synthetic instances
    create_synthetic_instances()
    
    print("\n" + "=" * 60)
    files = os.listdir("vrp_benchmarks")
    print(f"VRP benchmark instances ready in: vrp_benchmarks/")
    print(f"Total files: {len(files)}")
    print(f"Real instances: {sum(1 for f in files if f.startswith('A-'))}")
    print(f"Synthetic instances: {sum(1 for f in files if f.startswith('synthetic_'))}")
    
    if real_downloaded == 0:
        print("\nWARNING: Could not download real benchmark instances.")
        print("Using synthetic instances only. Real benchmarks needed for proper comparison.")

if __name__ == "__main__":
    main()