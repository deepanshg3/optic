import os
from pathlib import Path
from typing import List

# Aggressive filtering to keep the AI prompt small and lightning fast
# 🚨 ADDED 'optic_brain' HERE SO THE AI DOESN'T SCAN ITSELF!
IGNORE_DIRS = {'.git', 'node_modules', '.venv', '__pycache__', 'build', 'dist', '.vscode', '.idea', 'optic_brain'}
IGNORE_FILES = {'package-lock.json', 'yarn.lock', '.DS_Store'}
IGNORE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.mp4', '.mp3', '.pdf', '.webp'}

class ContextManager:
    def __init__(self, target_project_path: str):
        self.project_path = Path(target_project_path).expanduser().resolve()

    def get_directory_tree(self) -> str:
        """Generates a clean text representation of the project structure."""
        tree_lines = [f"📁 {self.project_path.name}/"]
        
        for root, dirs, files in os.walk(self.project_path):
            # IN-PLACE directory filtering (This makes it instantly skip node_modules)
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in IGNORE_DIRS]
            
            current_dir = Path(root)
            
            if current_dir == self.project_path:
                level = 0
            else:
                level = len(current_dir.relative_to(self.project_path).parts)
                
            indent = ' ' * 4 * level
            sub_indent = ' ' * 4 * (level + 1)
            
            if level > 0:
                tree_lines.append(f"{indent}📂 {current_dir.name}/")
                
            # File filtering
            for file in files:
                if (not file.startswith('.') and 
                    file not in IGNORE_FILES and 
                    not any(file.endswith(ext) for ext in IGNORE_EXTENSIONS)):
                    
                    tree_lines.append(f"{sub_indent}📄 {file}")
                    
        return "\n".join(tree_lines)

    def read_specific_files(self, relative_filepaths: List[str]) -> str:
        """Takes a list of filenames from the LLM and grabs their actual code."""
        combined_code = ""
        
        for filepath in relative_filepaths:
            full_path = (self.project_path / filepath).resolve()
            
            if not str(full_path).startswith(str(self.project_path)):
                combined_code += f"\n--- FILE: {filepath} ---\n[Error: Access Denied - Outside Project Scope]\n"
                continue
                
            try:
                if full_path.exists() and full_path.is_file():
                    content = full_path.read_text(encoding='utf-8')
                    combined_code += f"\n--- FILE: {filepath} ---\n```\n{content}\n```\n"
                else:
                    combined_code += f"\n--- FILE: {filepath} ---\n[Error: File Not Found]\n"
            except Exception as e:
                combined_code += f"\n--- FILE: {filepath} ---\n[Error reading file: {e}]\n"
                
        return combined_code

# Quick local test pointing to your actual app
if __name__ == "__main__":
    # Pointing directly to your target directory
    target_app_path = "~/Desktop/tic-tac-toe-main"
    
    manager = ContextManager(target_app_path)
    print("Testing Directory Tree Generation on Target App:")
    print("-" * 30)
    print(manager.get_directory_tree())