import re

with open('/workspace/evovera/v11_publication_manuscript_draft.md', 'r') as f:
    original = f.read()

appendices_start = original.find('## Appendices')
if appendices_start == -1:
    appendices_start = original.find('## References')
    if appendices_start == -1:
        appendices_start = len(original)

main_content = original[:appendices_start].strip()
appendices = original[appendices_start:].strip()

with open('/workspace/evovera/v11_publication_manuscript_draft_with_v19_comparison.md', 'r') as f:
    updated = f.read()

comp_start = updated.find('## 7. Comparative Analysis: v11 vs v19 Algorithms')
if comp_start == -1:
    comp_start = updated.find('## 6. Comparative Analysis: v11 vs v19 Algorithms')
    if comp_start == -1:
        print("Could not find comparative analysis section")
        exit(1)

next_section_match = re.search(r'\n## [0-9]+\.', updated[comp_start + 50:])
if next_section_match:
    comp_end = comp_start + 50 + next_section_match.start()
else:
    comp_end = len(updated)

comparative_section = updated[comp_start:comp_end]

discussion_start = main_content.find('## 5. Discussion')
if discussion_start == -1:
    print("Could not find Discussion section in main content")
    exit(1)

next_after_discussion = re.search(r'\n## [0-9]+\.', main_content[discussion_start + 50:])
if next_after_discussion:
    discussion_end = discussion_start + 50 + next_after_discussion.start()
else:
    discussion_end = len(main_content)

final_content = (
    main_content[:discussion_end] + 
    '\n\n' + 
    '## 6. Comparative Analysis: v11 vs v19 Algorithms' + 
    comparative_section[comparative_section.find('\n'):] + 
    '\n\n' + 
    main_content[discussion_end:]
)

lines = final_content.split('\n')
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

final_with_appendices = renumbered_content + '\n\n' + appendices

with open('/workspace/evovera/v11_publication_manuscript_final.md', 'w') as f:
    f.write(final_with_appendices)

print("Successfully created final manuscript with comprehensive comparative analysis")
