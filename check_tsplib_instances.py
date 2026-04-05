#!/usr/bin/env python3
"""
Check TSPLIB instance availability for Phase 2 evaluation.
Run this periodically to monitor for missing instances.
"""
import os
import sys
import json
from datetime import datetime

REQUIRED_INSTANCES = [
    "eil51.tsp",
    "kroA100.tsp", 
    "a280.tsp",
    "att532.tsp",
    "d198.tsp",
    "lin318.tsp",
    "pr439.tsp"
]

def check_instances():
    """Check which instances are present."""
    tsplib_dir = "data/tsplib"
    
    if not os.path.exists(tsplib_dir):
        return {"status": "error", "message": f"Directory {tsplib_dir} does not exist"}
    
    present = []
    missing = []
    
    for instance in REQUIRED_INSTANCES:
        path = os.path.join(tsplib_dir, instance)
        if os.path.exists(path):
            size = os.path.getsize(path)
            present.append({"name": instance, "size": size, "path": path})
        else:
            missing.append(instance)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "directory": os.path.abspath(tsplib_dir),
        "total_required": len(REQUIRED_INSTANCES),
        "present_count": len(present),
        "missing_count": len(missing),
        "present": present,
        "missing": missing,
        "complete": len(missing) == 0,
        "status": "complete" if len(missing) == 0 else "incomplete"
    }

def main():
    """Main function."""
    result = check_instances()
    
    print("=" * 70)
    print("TSPLIB INSTANCE AVAILABILITY CHECK")
    print("=" * 70)
    print(f"Time: {result['timestamp']}")
    print(f"Directory: {result['directory']}")
    print()
    
    print(f"📊 STATUS: {result['present_count']}/{result['total_required']} instances")
    print()
    
    if result["present"]:
        print("✅ PRESENT:")
        for item in result["present"]:
            print(f"   • {item['name']} ({item['size']:,} bytes)")
    
    if result["missing"]:
        print()
        print("❌ MISSING:")
        for instance in result["missing"]:
            print(f"   • {instance}")
    
    print()
    print("=" * 70)
    
    if result["complete"]:
        print("✅ ALL INSTANCES PRESENT!")
        print("TSPLIB Phase 2 evaluation can proceed.")
        return 0
    else:
        print(f"❌ INCOMPLETE: Missing {result['missing_count']} instances")
        print("Phase 2 evaluation cannot proceed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
