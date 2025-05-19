#!/usr/bin/env python
import os
import re
import logging

"""
This script fixes indentation issues in Discord cog files.
It adds the required __init__ method if it's missing and fixes class indentation.
"""

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def fix_cog_file(file_path):
    """Fix indentation issues in a cog file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip files that already have proper init method
        if "__init__" in content and "self.bot = bot" in content:
            logger.info(f"Skipping {file_path} - already has __init__ method")
            return
        
        # Find the cog class
        class_match = re.search(r'class\s+(\w+)\(commands\.Cog\):\s*\n\s*"""([^"]*?)"""', content)
        if not class_match:
            logger.warning(f"No Cog class found in {file_path}")
            return
        
        class_name = class_match.group(1)
        class_docstring = class_match.group(2)
        
        # Prepare the fixed content with proper indentation
        fixed_content = content.split('"""' + class_docstring + '"""', 1)
        
        if len(fixed_content) != 2:
            logger.warning(f"Couldn't process {file_path} properly")
            return
        
        header = fixed_content[0] + '"""' + class_docstring + '"""'
        rest = fixed_content[1]
        
        # Fix any immediate indented content after class definition
        if rest.strip() and not rest.lstrip().startswith('\n'):
            first_line = rest.lstrip().split('\n', 1)[0]
            # Find the command or method this indented line belongs to
            method_name = "unknown_method"
            if "@commands" in first_line:
                method_match = re.search(r'async\s+def\s+(\w+)', rest)
                if method_match:
                    method_name = method_match.group(1)
            
            logger.info(f"Fixing indentation for possible method {method_name} in {file_path}")
            
            # Build initialization method
            init_method = f"""
    def __init__(self, bot):
        self.bot = bot
        logger.info(f"{class_name} cog initialized")
    
"""
            # Find all indented lines at the class level
            indented_line_pattern = r'\n\s{8}[^\s]'
            if re.search(indented_line_pattern, rest):
                # There are indented lines - move them to a method
                if "@commands" not in rest[:200]:
                    # Add a command decorator if needed
                    command_method = f"""    @commands.command(name="{method_name}")
    @commands.has_permissions(manage_guild=True)
    async def {method_name}(self, ctx, *args):
        \"\"\"Auto-generated method from fixing indentation\"\"\"
"""
                    fixed_rest = init_method + command_method + rest
                else:
                    fixed_rest = init_method + rest
            else:
                fixed_rest = init_method + rest
        else:
            # Just add initialization method
            init_method = f"""
    def __init__(self, bot):
        self.bot = bot
        logger.info(f"{class_name} cog initialized")
"""
            fixed_rest = init_method + rest
        
        # Write the fixed content back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(header + fixed_rest)
        
        logger.info(f"Fixed {file_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return False

def fix_all_cogs():
    """Fix all cog files in the cogs directory"""
    cogs_dir = 'cogs'
    fixed_count = 0
    
    for filename in os.listdir(cogs_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            file_path = os.path.join(cogs_dir, filename)
            if fix_cog_file(file_path):
                fixed_count += 1
    
    logger.info(f"Fixed indentation in {fixed_count} cog files")

if __name__ == '__main__':
    fix_all_cogs()