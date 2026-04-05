import re

with open('/workspace/evovera/v11_publication_manuscript_final.md', 'r') as f:
    content = f.read()

first_comp_start = content.find('## 7. Comparative Analysis: v11 vs v19 Algorithms')
if first_comp_start == -1:
    print("Could not find first comparative analysis section")
    exit(1)

next_after_first = re.search(r'\n## [0-9]+\.', content[first_comp_start + 50:])
if next_after_first:
    first_comp_end = first_comp_start + 50 + next_after_first.start()
else:
    first_comp_end = len(content)

second_comp_start = content.find('## 7. Comparative Analysis: v11 vs v19 Algorithms', first_comp_end)
if second_comp_start == -1:
    print("No duplicate found, using current content")
    clean_content = content
else:
    next_after_second = re.search(r'\n## [0-9]+\.', content[second_comp_start + 50:])
    if next_after_second:
        second_comp_end = second_comp_start + 50 + next_after_second.start()
    else:
        second_comp_end = len(content)
    
    clean_content = content[:second_comp_start] + content[second_comp_end:]

with open('/workspace/evovera/v11_publication_manuscript_final_clean.md', 'w') as f:
    f.write(clean_content)

print("Created clean final manuscript without duplicate comparative analysis")
