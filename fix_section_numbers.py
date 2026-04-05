import re

with open('/workspace/evovera/v11_publication_manuscript_draft_with_v19_comparison.md', 'r') as f:
    content = f.read()

comp_start = content.find('## 6. Comparative Analysis: v11 vs v19 Algorithms')
if comp_start == -1:
    print("Could not find comparative analysis section")
    exit(1)

next_section_match = re.search(r'\n## [0-9]+\.', content[comp_start + 50:])
if next_section_match:
    comp_end = comp_start + 50 + next_section_match.start()
else:
    comp_end = len(content)

comparative_section = content[comp_start:comp_end]
content_without_comp = content[:comp_start] + content[comp_end:]

discussion_start = content_without_comp.find('## 5. Discussion')
if discussion_start == -1:
    print("Could not find Discussion section")
    exit(1)

next_after_discussion = re.search(r'\n## [0-9]+\.', content_without_comp[discussion_start + 50:])
if next_after_discussion:
    discussion_end = discussion_start + 50 + next_after_discussion.start()
else:
    discussion_end = len(content_without_comp)

new_content = (
    content_without_comp[:discussion_end] + 
    '\n' + 
    '## 6. Comparative Analysis: v11 vs v19 Algorithms' + 
    comparative_section[comparative_section.find('\n'):] + 
    '\n' + 
    content_without_comp[discussion_end:]
)

lines = new_content.split('\n')
renumbered_lines = []
section_counter = 0

for line in lines:
    if line.startswith('## '):
        match = re.match(r'## ([0-9]+)\.', line)
        if match:
            section_num = int(match.group(1))
            if section_num >= 6:
                section_counter = section_num + 1
                line = re.sub(r'## [0-9]+\.', f'## {section_counter}.', line)
            else:
                section_counter = section_num
    renumbered_lines.append(line)

renumbered_content = '\n'.join(renumbered_lines)

with open('/workspace/evovera/v11_publication_manuscript_draft_with_v19_comparison.md', 'w') as f:
    f.write(renumbered_content)

print("Successfully fixed section numbering")
