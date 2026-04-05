#!/usr/bin/env python3
import re

with open('run_phase3_final.py', 'r') as f:
    content = f.read()

# Fix the broken line
content = re.sub(
    r'print\(f"Overall statistical significance: p = \{p_value:.6f\} {\'\(significant\'.*',
    '        print(f"Overall statistical significance: p = {p_value:.6f} {\"(significant)\" if p_value < 0.05 else \"(not significant)\"}")',
    content,
    flags=re.DOTALL
)

with open('run_phase3_final.py', 'w') as f:
    f.write(content)

print("Fixed syntax error")
