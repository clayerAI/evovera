#!/usr/bin/env python3
"""
Download TSPLIB instances for Phase 2 evaluation.
Uses alternative sources since the official TSPLIB website may be blocked.
"""

import os
import sys
import requests
import time

# Required instances with their known optimal solutions
REQUIRED_INSTANCES = {
    "eil51": {
        "optimal": 426,
        "urls": [
            "https://raw.githubusercontent.com/rhgrant10/tsplib95/master/tsplib95/problems/eil51.tsp",
            "https://people.sc.fsu.edu/~jburkardt/datasets/tsp/eil51.tsp",
            "https://www.math.uwaterloo.ca/tsp/vlsi/eil51.tsp"
        ]
    },
    "kroA100": {
        "optimal": 21282,
        "urls": [
            "https://raw.githubusercontent.com/rhgrant10/tsplib95/master/tsplib95/problems/kroA100.tsp",
            "https://people.sc.fsu.edu/~jburkardt/datasets/tsp/kroA100.tsp"
        ]
    },
    "a280": {
        "optimal": 2579,
        "urls": [
            "https://raw.githubusercontent.com/rhgrant10/tsplib95/master/tsplib95/problems/a280.tsp",
            "https://people.sc.fsu.edu/~jburkardt/datasets/tsp/a280.tsp"
        ]
    },
    "att532": {
        "optimal": 27686,
        "urls": [
            "https://raw.githubusercontent.com/rhgrant10/tsplib95/master/tsplib95/problems/att532.tsp",
            "https://people.sc.fsu.edu/~jburkardt/datasets/tsp/att532.tsp"
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
    print("TSPLIB INSTANCE ACQUISITION - Phase 2 Evaluation")
    print("=" * 80)
    
    # Create TSPLIB directory if it doesn't exist
    tsplib_dir = "/workspace/evovera/data/tsplib"
    os.makedirs(tsplib_dir, exist_ok=True)
    
    print(f"\n📁 Target directory: {tsplib_dir}")
    
    success_count = 0
    failed_count = 0
    
    for instance_name, instance_info in REQUIRED_INSTANCES.items():
        print(f"\n📥 Downloading {instance_name} (optimal: {instance_info['optimal']})...")
        
        filename = f"{instance_name}.tsp"
        destination = os.path.join(tsplib_dir, filename)
        
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
    
    # List downloaded files
    print(f"\n📂 Files in {tsplib_dir}:")
    if os.path.exists(tsplib_dir):
        files = os.listdir(tsplib_dir)
        for f in sorted(files):
            filepath = os.path.join(tsplib_dir, f)
            size = os.path.getsize(filepath) if os.path.isfile(filepath) else 0
            print(f"  • {f} ({size} bytes)")
    
    print("\n" + "=" * 80)
    
    if success_count == len(REQUIRED_INSTANCES):
        print("✅ ALL INSTANCES ACQUIRED - Ready for TSPLIB evaluation!")
        return 0
    elif success_count > 0:
        print(f"⚠️  PARTIAL SUCCESS - {success_count}/{len(REQUIRED_INSTANCES)} instances acquired")
        print("   Consider manual download for missing instances")
        return 1
    else:
        print("❌ ALL DOWNLOADS FAILED - Need alternative acquisition method")
        print("   Options: 1) Manual download from TSPLIB website")
        print("            2) Use tsplib95 Python package (if installable)")
        print("            3) Request Vera's coordination for instance acquisition")
        return 2

if __name__ == "__main__":
    sys.exit(main())