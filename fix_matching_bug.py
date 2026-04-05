import sys
sys.path.append('.')

# Test the formulas
dist = 100
centrality = 0.5

# Original formulas
within_original = dist * (1 - 0.8 * centrality)
between_original = dist * (1 - 0.3 * centrality)

# Current optimized formulas  
within_current = dist * 0.8 * (1 - 0.5 * centrality)
between_current = dist * 0.3 * (1 - 0.5 * centrality)

# Correct optimized formulas (should match original)
within_correct = dist * (1 - 0.8 * centrality)
between_correct = dist * (1 - 0.3 * centrality)

print("Original formulas:")
print(f"  Within community (0.8): {within_original:.2f}")
print(f"  Between community (0.3): {between_original:.2f}")
print()
print("Current optimized (WRONG):")
print(f"  Within community: {within_current:.2f} (error: {within_current/within_original:.1%})")
print(f"  Between community: {between_current:.2f} (error: {between_current/between_original:.1%})")
print()
print("Correct optimized (should match original):")
print(f"  Within community: {within_correct:.2f}")
print(f"  Between community: {between_correct:.2f}")

# Test with centrality = 0
centrality = 0.0
within_original0 = dist * (1 - 0.8 * centrality)
within_current0 = dist * 0.8 * (1 - 0.5 * centrality)
print(f"\nWith centrality=0:")
print(f"  Original: {within_original0:.2f}")
print(f"  Current: {within_current0:.2f} (20% lower!)")
