import os

# Set your root directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(ROOT_DIR, 'project_tree_output.txt')

# File types to include for content printing
ALLOWED_EXTENSIONS = {
    '.py', '.html', '.json', '.css', '.js', '.txt', '.md', '.csv'
}

def print_tree(path, prefix='', output_lines=None):
    """Recursively builds a tree view of the directory with file contents."""
    if output_lines is None:
        output_lines = []

    try:
        contents = sorted(os.listdir(path))
    except Exception as e:
        output_lines.append(prefix + f"[Error accessing {path}]: {e}")
        return output_lines

    pointers = ['├── '] * (len(contents) - 1) + ['└── ']
    for pointer, name in zip(pointers, contents):
        full_path = os.path.join(path, name)
        output_lines.append(prefix + pointer + name)

        if os.path.isdir(full_path):
            extension = '│   ' if pointer == '├── ' else '    '
            print_tree(full_path, prefix + extension, output_lines)
        else:
            _, ext = os.path.splitext(name)
            if ext.lower() in ALLOWED_EXTENSIONS:
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        output_lines.append(prefix + '     ↓↓↓ FILE CONTENT ↓↓↓')
                        for line in f:
                            output_lines.append(prefix + '     ' + line.rstrip())
                        output_lines.append(prefix + '     ↑↑↑ END OF FILE ↑↑↑\n')
                except Exception as e:
                    output_lines.append(prefix + f'     [Error reading file: {e}]\n')
    return output_lines

if __name__ == '__main__':
    tree_output = ['.']
    tree_output = print_tree(ROOT_DIR, output_lines=tree_output)

    # Write to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(tree_output))

    # Print file content
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        print(f.read())
