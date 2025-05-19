import os
import re

def clean_file(file_path):
    """Clean a file by removing verbose docstrings"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match docstrings with Args: sections
    pattern = r'""".*?Args:.*?"""'
    
    # Replace with simple docstrings
    def replace_docstring(match):
        docstring = match.group(0)
        lines = docstring.split('\n')
        
        # Extract the first line of the docstring (description)
        description = lines[0].strip('"').strip()
        if not description:
            # If the first line is empty, try to get the second line
            if len(lines) > 1:
                description = lines[1].strip()
        
        # Create a simplified docstring
        return f'"""{description}"""'
    
    # Replace the docstrings
    modified_content = re.sub(pattern, replace_docstring, content, flags=re.DOTALL)
    
    if content != modified_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        return True
    
    return False

def clean_directory(directory):
    """Clean all Python files in a directory and its subdirectories"""
    cleaned_files = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if clean_file(file_path):
                    cleaned_files += 1
                    print(f"Cleaned {file_path}")
    
    print(f"Cleaned {cleaned_files} files")

if __name__ == "__main__":
    clean_directory('cogs')