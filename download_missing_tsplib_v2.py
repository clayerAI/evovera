#!/usr/bin/env python3
"""
Download missing TSPLIB instances for Phase 2 evaluation.
Updated with working sources.
"""
import os
import requests
import time

# Working TSPLIB sources (tested)
SOURCES = {
    "github": "https://raw.githubusercontent.com/rhgrant10/tsplib95/master/data/{}.tsp",
    "burkardt": "https://people.sc.fsu.edu/~jburkardt/datasets/tsp/{}.tsp",
    "waterloo": "https://www.math.uwaterloo.ca/tsp/vlsi/{}.tsp",
}

# All instances needed for Phase 2 evaluation
INSTANCES = [
    # Already have these 4
    {"name": "eil51", "optimal": 426},
    {"name": "kroA100", "optimal": 21282},
    {"name": "a280", "optimal": 2579},
    {"name": "att532", "optimal": 27686},
    # MISSING - need to download
    {"name": "d198", "optimal": 15780},
    {"name": "lin318", "optimal": 42029},
    {"name": "pr439", "optimal": 107217},
]

def download_instance(instance_name, output_dir):
    """Try to download an instance from multiple sources."""
    for source_name, url_template in SOURCES.items():
        url = url_template.format(instance_name)
        output_path = os.path.join(output_dir, f"{instance_name}.tsp")
        
        try:
            print(f"  Trying {source_name}: {url}")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                # Verify it's a valid TSP file
                with open(output_path, 'r') as f:
                    content = f.read(100)
                    if "NAME" in content and "DIMENSION" in content:
                        print(f"    ✅ Downloaded successfully")
                        return True
                    else:
                        print(f"    ⚠️  Downloaded but content doesn't look like TSP")
                        os.remove(output_path)
                        continue
            else:
                print(f"    ✗ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    return False

def main():
    output_dir = "data/tsplib"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 70)
    print("TSPLIB INSTANCE ACQUISITION - Phase 2 Evaluation")
    print("=" * 70)
    print(f"📁 Target directory: {output_dir}")
    print()
    
    # Check what we already have
    existing = []
    missing = []
    
    for instance in INSTANCES:
        name = instance["name"]
        path = os.path.join(output_dir, f"{name}.tsp")
        
        if os.path.exists(path):
            existing.append(name)
        else:
            missing.append(name)
    
    print(f"📊 Status: {len(existing)}/{len(INSTANCES)} instances already present")
    print(f"   ✅ Have: {', '.join(existing)}")
    print(f"   ❌ Missing: {', '.join(missing)}")
    print()
    
    if not missing:
        print("✅ All required instances are already present!")
        print("TSPLIB Phase 2 evaluation can proceed.")
        return
    
    print("📥 Attempting to download missing instances...")
    print()
    
    success_count = 0
    for instance in INSTANCES:
        name = instance["name"]
        
        if name in existing:
            continue
        
        print(f"📥 Downloading {name} (optimal: {instance['optimal']})...")
        
        if download_instance(name, output_dir):
            success_count += 1
        else:
            print(f"  ❌ All download attempts failed for {name}")
        
        print()
        time.sleep(1)  # Be nice to servers
    
    print("=" * 70)
    print("DOWNLOAD SUMMARY:")
    print(f"  ✅ Successfully downloaded: {success_count} instances")
    print(f"  ❌ Still missing: {len(missing) - success_count} instances")
    print()
    
    # Final status check
    final_missing = []
    for instance in INSTANCES:
        name = instance["name"]
        path = os.path.join(output_dir, f"{name}.tsp")
        
        if not os.path.exists(path):
            final_missing.append(name)
    
    if final_missing:
        print("❌ CRITICAL BLOCKER: Missing instances prevent evaluation:")
        for name in final_missing:
            print(f"   • {name}.tsp")
        print()
        print("NEXT STEPS:")
        print("1. Manual download required from TSPLIB website")
        print("2. Or use tsplib95 Python package: pip install tsplib95")
        print("3. Contact Evo for coordination")
    else:
        print("✅ ALL INSTANCES ACQUIRED!")
        print("TSPLIB Phase 2 evaluation can now proceed.")

if __name__ == "__main__":
    main()
