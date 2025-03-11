import re
import os

# Path to the markdown file
md_file_path = 'system-architecture.md'
# Path to the output directory
output_dir = 'mermaid_diagrams'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Read the markdown file
with open(md_file_path, 'r') as file:
    content = file.read()

# Regular expression to match Mermaid code blocks
mermaid_regex = r'```mermaid\n([\s\S]*?)```'

# Find all matches
matches = re.findall(mermaid_regex, content)

# Extract each Mermaid diagram and save to a file
for i, mermaid_code in enumerate(matches, 1):
    output_file = os.path.join(output_dir, f'diagram_{i}.mmd')
    with open(output_file, 'w') as file:
        file.write(mermaid_code)
    print(f'Saved diagram {i} to {output_file}')

print(f'Extracted {len(matches)} diagrams')

# Now create an updated version of the markdown with image placeholders
diagram_count = 0
def replace_with_image(match):
    global diagram_count
    diagram_count += 1
    return f'![Diagram {diagram_count}](./images/diagram_{diagram_count}.png)'

updated_content = re.sub(mermaid_regex, replace_with_image, content)

# Write the updated content to a new file
with open(md_file_path + '.updated', 'w') as file:
    file.write(updated_content)

print(f'Updated markdown saved to {md_file_path}.updated') 