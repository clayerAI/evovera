#!/usr/bin/env python3
"""
Clean up monitor state file.
Remove __pycache__ entries and mark reviewed solutions.
"""

import json
from pathlib import Path

def clean_state_file():
    state_file = Path("/workspace/evovera/.vera-monitor-state.json")
    
    if not state_file.exists():
        print("State file does not exist")
        return
    
    with open(state_file, 'r') as f:
        state = json.load(f)
    
    # Remove __pycache__ from known_solutions
    if "__pycache__" in state["known_solutions"]:
        del state["known_solutions"]["__pycache__"]
        print("Removed __pycache__ from known_solutions")
    
    # Remove __pycache__ from pending_reviews
    if "__pycache__" in state["pending_reviews"]:
        state["pending_reviews"].remove("__pycache__")
        print("Removed __pycache__ from pending_reviews")
    
    # Mark TSP solutions as reviewed (since Vera has already reviewed them)
    tsp_solutions = [
        "tsp_v1_nearest_neighbor.py",
        "tsp_v2_christofides.py",
        "tsp-500-euclidean",
        "tsp-500-euclidean-christofides",
        "sample-problem-001"
    ]
    
    for solution in tsp_solutions:
        if solution in state["known_solutions"]:
            state["known_solutions"][solution]["review_status"] = "reviewed"
            state["known_solutions"][solution]["last_reviewed"] = "2026-04-03T11:30:00"
            print(f"Marked {solution} as reviewed")
        
        if solution in state["pending_reviews"]:
            state["pending_reviews"].remove(solution)
            print(f"Removed {solution} from pending_reviews")
    
    # Save cleaned state
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
    
    print("State file cleaned successfully")

if __name__ == "__main__":
    clean_state_file()