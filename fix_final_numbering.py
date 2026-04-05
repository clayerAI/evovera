import re

with open('/workspace/evovera/v11_publication_manuscript_final_clean.md', 'r') as f:
    content = f.read()

content = content.replace('## 7. Comparative Analysis: v11 vs v19 Algorithms', '## 6. Comparative Analysis: v11 vs v19 Algorithms')

lines = content.split('\n')
renumbered_lines = []
section_counter = 0

for line in lines:
    if line.startswith('## '):
        match = re.match(r'## ([0-9]+)\.', line)
        if match:
            section_num = int(match.group(1))
            if section_num >= 6:
                section_counter = section_num - 1
                line = re.sub(r'## [0-9]+\.', f'## {section_counter}.', line)
            else:
                section_counter = section_num
    renumbered_lines.append(line)

renumbered_content = '\n'.join(renumbered_lines)

with open('/workspace/evovera/v11_publication_manuscript_complete.md', 'w') as f:
    f.write(renumbered_content)

print("Created final manuscript with correct section numbering")
