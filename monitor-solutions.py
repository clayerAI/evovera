#!/usr/bin/env python3
"""
Monitor for new Evo solutions and trigger Vera reviews.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
import hashlib

class SolutionMonitor:
    def __init__(self, repo_path="/workspace/evovera"):
        self.repo_path = Path(repo_path)
        self.solutions_dir = self.repo_path / "solutions"
        self.reviews_dir = self.repo_path / "reviews"
        self.state_file = self.repo_path / ".vera-monitor-state.json"
        
        # Ensure directories exist
        self.solutions_dir.mkdir(exist_ok=True)
        self.reviews_dir.mkdir(exist_ok=True)
        
        # Load previous state
        self.state = self.load_state()
    
    def load_state(self):
        """Load monitoring state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return {
            "last_check": None,
            "known_solutions": {},
            "pending_reviews": []
        }
    
    def save_state(self):
        """Save monitoring state to file."""
        self.state["last_check"] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def get_solution_hash(self, solution_path):
        """Calculate hash of solution directory or file contents."""
        hash_obj = hashlib.md5()
        
        # Handle both directories and files
        if solution_path.is_dir():
            for root, dirs, files in os.walk(solution_path):
                # Exclude __pycache__ directories
                dirs[:] = [d for d in dirs if d != '__pycache__']
                # Sort for consistent hashing
                dirs.sort()
                files.sort()
                
                for file in files:
                    # Skip .pyc files and other cache files
                    if file.endswith('.pyc') or file == '.DS_Store':
                        continue
                        
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'rb') as f:
                            while chunk := f.read(8192):
                                hash_obj.update(chunk)
                    except (IOError, OSError):
                        # Skip files we can't read
                        pass
        else:
            # It's a file
            try:
                with open(solution_path, 'rb') as f:
                    while chunk := f.read(8192):
                        hash_obj.update(chunk)
            except (IOError, OSError):
                pass
        
        return hash_obj.hexdigest()
    
    def check_for_new_solutions(self):
        """Check for new or updated solutions."""
        print(f"Checking for solutions in {self.solutions_dir}")
        
        new_solutions = []
        updated_solutions = []
        
        # Find all solution items (both directories and files)
        for item in self.solutions_dir.iterdir():
            # Skip __pycache__ directories and .pyc files
            if item.name == '__pycache__' or item.name.endswith('.pyc') or item.name == '.DS_Store':
                continue
                
            # Check if it's a solution (directory or .py file)
            is_solution = False
            if item.is_dir():
                # Directory solution (legacy format)
                is_solution = True
            elif item.is_file() and item.suffix == '.py':
                # Flat file solution (new format)
                # Check if it's a solution file (starts with problem identifier)
                if item.name.startswith(('tsp_', 'problem_', 'solution_')):
                    is_solution = True
            
            if not is_solution:
                continue
                
            solution_name = item.name
            solution_hash = self.get_solution_hash(item)
            
            if solution_name not in self.state["known_solutions"]:
                # New solution
                print(f"  Found NEW solution: {solution_name}")
                new_solutions.append(solution_name)
                self.state["known_solutions"][solution_name] = {
                    "hash": solution_hash,
                    "first_seen": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "review_status": "pending",
                    "type": "directory" if item.is_dir() else "file"
                }
                self.state["pending_reviews"].append(solution_name)
                
            elif self.state["known_solutions"][solution_name]["hash"] != solution_hash:
                # Updated solution
                print(f"  Found UPDATED solution: {solution_name}")
                updated_solutions.append(solution_name)
                self.state["known_solutions"][solution_name]["hash"] = solution_hash
                self.state["known_solutions"][solution_name]["last_updated"] = datetime.now().isoformat()
                self.state["known_solutions"][solution_name]["review_status"] = "needs_review"
                if solution_name not in self.state["pending_reviews"]:
                    self.state["pending_reviews"].append(solution_name)
        
        return new_solutions, updated_solutions
    
    def get_pending_reviews(self):
        """Get list of solutions needing review."""
        return self.state.get("pending_reviews", [])
    
    def mark_review_complete(self, solution_name):
        """Mark a solution as reviewed."""
        if solution_name in self.state["known_solutions"]:
            self.state["known_solutions"][solution_name]["review_status"] = "reviewed"
            self.state["known_solutions"][solution_name]["last_reviewed"] = datetime.now().isoformat()
        
        if solution_name in self.state["pending_reviews"]:
            self.state["pending_reviews"].remove(solution_name)
    
    def run_monitoring_cycle(self):
        """Run one monitoring cycle."""
        print(f"\n=== Vera Monitoring Cycle {datetime.now().isoformat()} ===")
        
        new, updated = self.check_for_new_solutions()
        
        if new:
            print(f"\nNew solutions detected: {', '.join(new)}")
            print("Vera should review these solutions.")
        
        if updated:
            print(f"\nUpdated solutions detected: {', '.join(updated)}")
            print("Vera should re-review these solutions.")
        
        pending = self.get_pending_reviews()
        if pending:
            print(f"\nPending reviews: {', '.join(pending)}")
        else:
            print("\nNo pending reviews.")
        
        self.save_state()
        print(f"\nState saved to {self.state_file}")
        
        return new + updated

def main():
    """Main monitoring function."""
    monitor = SolutionMonitor()
    
    # Run monitoring cycle
    changes = monitor.run_monitoring_cycle()
    
    # Return exit code based on whether changes were detected
    return 0 if not changes else 1

if __name__ == "__main__":
    exit(main())