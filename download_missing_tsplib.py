#!/usr/bin/env python3
"""
Download missing TSPLIB instances for Phase 2 evaluation.
Missing: d198, lin318, pr439
"""
import os
import requests
import gzip
import shutil

# TSPLIB instance URLs (from official repository)
TSPLIB_URLS = {
    "d198": "http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/d198.tsp.gz",
    "lin318": "http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/lin318.tsp.gz",
    "pr439": "http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/pr439.tsp.gz",
}

def download_and_extract(instance_name, url, output_dir):
    """Download and extract a TSPLIB instance."""
    output_path = os.path.join(output_dir, f"{instance_name}.tsp")
    gz_path = os.path.join(output_dir, f"{instance_name}.tsp.gz")
    
    print(f"Downloading {instance_name}...")
    
    try:
        # Download
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(gz_path, 'wb') as f:
            f.write(response.content)
        
        # Extract
        with gzip.open(gz_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Clean up
        os.remove(gz_path)
        
        print(f"  ✅ Downloaded and extracted to {output_path}")
        return True
        
    except Exception as e:
        print(f"  ❌ Failed to download {instance_name}: {e}")
        return False

def main():
    output_dir = "data/tsplib"
    os.makedirs(output_dir, exist_ok=True)
    
    print("Downloading missing TSPLIB instances for Phase 2 evaluation...")
    print("=" * 60)
    
    success_count = 0
    for instance_name, url in TSPLIB_URLS.items():
        if download_and_extract(instance_name, url, output_dir):
            success_count += 1
    
    print("=" * 60)
    print(f"Download complete: {success_count}/{len(TSPLIB_URLS)} instances")
    
    if success_count == len(TSPLIB_URLS):
        print("✅ All missing instances downloaded successfully!")
        print("TSPLIB Phase 2 evaluation can now proceed.")
    else:
        print("⚠️  Some instances failed to download.")
        print("Manual download may be required.")

if __name__ == "__main__":
    main()
