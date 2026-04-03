"""
Sample solution for demonstration purposes.
Problem: Find the maximum subarray sum (Kadane's algorithm)
"""

def max_subarray_sum(arr):
    """
    Find the maximum sum of any contiguous subarray.
    
    Args:
        arr: List of integers (can be positive or negative)
    
    Returns:
        Maximum sum of any contiguous subarray
    """
    if not arr:
        return 0
    
    max_ending_here = max_so_far = arr[0]
    
    for num in arr[1:]:
        max_ending_here = max(num, max_ending_here + num)
        max_so_far = max(max_so_far, max_ending_here)
    
    return max_so_far

# Example usage
if __name__ == "__main__":
    test_cases = [
        ([-2, 1, -3, 4, -1, 2, 1, -5, 4], 6),  # Standard case
        ([1, 2, 3, 4, 5], 15),  # All positive
        ([-1, -2, -3, -4], -1),  # All negative
        ([], 0),  # Empty array
    ]
    
    for arr, expected in test_cases:
        result = max_subarray_sum(arr)
        print(f"arr={arr}, expected={expected}, result={result}, {'PASS' if result == expected else 'FAIL'}")