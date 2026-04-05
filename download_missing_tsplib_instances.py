#!/usr/bin/env python3
"""
Download missing TSPLIB instances for Phase 2 evaluation.
"""

import os
import sys
import requests
import time

# Missing instances with their known optimal solutions
MISSING_INSTANCES = {
    "d198": {
        "optimal": 15780,
        "urls": [
            "https://raw.githubusercontent.com/pongells/ACO-TSP/master/src/problems/d198.tsp",
            "https://people.sc.fsu.edu/~jburkardt/datasets/tsp/d198.tsp"
        ]
    },
    "lin318": {
        "optimal": 42029,
        "urls": [
            "https://raw.githubusercontent.com/pongells/ACO-TSP/master/src/problems/lin318.tsp",
            "https://people.sc.fsu.edu/~jburkardt/datasets/tsp/lin318.tsp"
        ]
    },
    "pr439": {
        "optimal": 107217,
        "urls": [
            "https://raw.githubusercontent.com/pongells/ACO-TSP/master/src/problems/pr439.tsp",
            "https://people.sc.fsu.edu/~jburkardt/datasets/tsp/pr439.tsp"
        ]
    }
}

def download_file(url, destination):
    """Download a file from URL to destination."""
    try:
        print(f"  Downloading from: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(destination, 'wb') as f:
            f.write(response.content)
        
        print(f"  ✓ Downloaded: {destination} ({len(response.content)} bytes)")
        return True
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False

def main():
    print("=" * 80)
    print("MISSING TSPLIB INSTANCE ACQUISITION - Phase 2 Evaluation")
    print("=" * 80)
    
    # Create TSPLIB directory if it doesn't exist
    tsplib_dir = "/workspace/evovera/data/tsplib"
    os.makedirs(tsplib_dir, exist_ok=True)
    
    print(f"\n📁 Target directory: {tsplib_dir}")
    
    success_count = 0
    failed_count = 0
    
    for instance_name, instance_info in MISSING_INSTANCES.items():
        print(f"\n📥 Downloading {instance_name} (optimal: {instance_info['optimal']})...")
        
        filename = f"{instance_name}.tsp"
        destination = os.path.join(tsplib_dir, filename)
        
        # Check if file already exists
        if os.path.exists(destination):
            print(f"  ⚠️  File already exists: {filename}")
            print(f"  Skipping download...")
            success_count += 1
            continue
        
        # Try each URL until one succeeds
        downloaded = False
        for url in instance_info['urls']:
            if download_file(url, destination):
                downloaded = True
                success_count += 1
                break
            time.sleep(1)  # Brief pause between attempts
        
        if not downloaded:
            print(f"  ❌ All download attempts failed for {instance_name}")
            failed_count += 1
    
    print("\n" + "=" * 80)
    print("DOWNLOAD SUMMARY:")
    print(f"  ✅ Successfully downloaded: {success_count} instances")
    print(f"  ❌ Failed to download: {failed_count} instances")
    
    # List all files in directory
    print(f"\n📂 Files in {tsplib_dir}:")
    if os.path.exists(tsplib_dir):
        files = os.listdir(tsplib_dir)
        for f in sorted(files):
            filepath = os.path.join(tsplib_dir, f)
            size = os.path.getsize(filepath) if os.path.isfile(filepath) else 0
            print(f"  • {f} ({size} bytes)")
    
    print("\n" + "=" * 80)
    
    if success_count == len(MISSING_INSTANCES):
        print("✅ ALL MISSING INSTANCES ACQUIRED - Ready for complete TSPLIB evaluation!")
        return 0
    elif success_count > 0:
        print(f"⚠️  PARTIAL SUCCESS - {success_count}/{len(MISSING_INSTANCES)} missing instances acquired")
        return 1
    else:
        print("❌ ALL DOWNLOADS FAILED")
        return 2

if __name__ == "__main__":
    sys.exit(main())
