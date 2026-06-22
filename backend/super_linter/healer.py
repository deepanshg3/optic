import os
import json
import sys

# Ensure Optic can find your existing LLM class
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.agents.llm_api import OpticLLM

# 🚨 The Cloud-Strict Prompt (Using the Line-Number bypass we perfected!)
UNIVERSAL_CLOUD_PROMPT = """You are an elite Polyglot Site Reliability Engineer operating in a headless CI/CD cloud environment.
You are fixing syntax errors caught by GitHub Super Linter.

CRITICAL RULE: You MUST output ONLY a raw JSON array. Do NOT wrap the JSON in markdown blocks.

The JSON must exactly match this schema:
[
  {
    "file_path": "the exact file path provided",
    "start_line": <INT>,
    "end_line": <INT>,
    "replace_block": "The new lines of code to insert."
  }
]

PATCHING RULES:
1. `start_line` and `end_line` are the EXACT integer line numbers from the provided snippet that contain the error.
2. If the error is on a single line, start_line and end_line will be the SAME number.
3. Your `replace_block` must contain the FULL FIXED CODE for those specific lines, keeping original indentation.
"""

class CloudHealer:
    def __init__(self, workspace_root):
        """
        workspace_root is the absolute path to where Tic-Tac-Toe 
        is downloaded on the GitHub server (usually /github/workspace)
        """
        self.workspace_root = workspace_root
        self.llm = OpticLLM()
        
    def get_numbered_snippet(self, file_path, target_line, up=10, down=5):
        """Extracts the broken code directly from the Tic-Tac-Toe repository."""
        full_path = os.path.join(self.workspace_root, file_path)
        
        if not os.path.exists(full_path):
            print(f"⚠️ Warning: Could not find {full_path} on the cloud hard drive.")
            return None, []
            
        with open(full_path, 'r', encoding='utf-8') as f:
            lines = f.read().split('\n')
            
        start = max(0, target_line - 1 - up)
        end = min(len(lines), target_line + down)
        
        snippet = []
        for i in range(start, end):
            # i+1 because humans and linters read Line 1, not Line 0
            snippet.append(f"{i+1} | {lines[i]}")
            
        return '\n'.join(snippet), lines
        
    def heal_files(self, parsed_errors):
        """Takes the errors from parser.py, asks Gemini, and overwrites the files."""
        if not parsed_errors:
            print("✅ No errors to heal. Optic Bot is sleeping...")
            return True
            
        print(f"🧠 Waking up Cloud Optic LLM to heal {len(parsed_errors)} errors...")
        
        # 1. Build the Mega-Context for the LLM
        batched_context = ""
        file_cache = {} # Stores the original file lines so we can rewrite them later
        
        for error in parsed_errors:
            filepath = error['file_path']
            
            # The Super Linter often spits out absolute paths like /github/workspace/test_ui.html
            # We strip the workspace root so it's a clean relative path (test_ui.html)
            clean_path = filepath.replace(self.workspace_root + "/", "")
            
            snippet, original_lines = self.get_numbered_snippet(clean_path, error['line'])
            
            if snippet:
                file_cache[clean_path] = original_lines
                batched_context += f"File: {clean_path}\nError Rule: {error['error_rule']}\nMessage: {error['error_msg']}\nSnippet:\n{snippet}\n\n"

        # 2. Call Gemini for the Mega-Patch
        user_prompt = f"Please fix the following files based on their Super Linter error logs:\n\n{batched_context}"
        raw_response = self.llm.analyze(user_prompt=user_prompt, system_prompt=UNIVERSAL_CLOUD_PROMPT)
        
        try:
            clean_text = raw_response.replace('```json', '').replace('```', '').strip()
            mega_patch = json.loads(clean_text)
        except Exception as e:
            print(f"❌ LLM failed to generate a valid JSON patch: {e}\nRaw Response: {raw_response}")
            return False

        # 3. Apply the Patches directly to the Hard Drive
        print("💉 Applying AI patches to the cloud workspace...")
        for patch in mega_patch:
            filepath = patch.get("file_path")
            start = patch.get("start_line")
            end = patch.get("end_line")
            new_code = patch.get("replace_block", "")
            
            if filepath in file_cache and start and end:
                lines = file_cache[filepath]
                
                # Math check: Arrays are 0-indexed. 
                # If error is line 12 to 12, we want to replace lines[11:12]
                prefix = lines[:start-1]
                suffix = lines[end:]
                
                # Rebuild the entire file with the AI's new code injected in the middle
                new_file_content = '\n'.join(prefix + [new_code] + suffix)
                
                # Overwrite the actual file on the server
                full_path = os.path.join(self.workspace_root, filepath)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(new_file_content)
                
                print(f"  -> ✅ Patched {filepath} (Lines {start}-{end})")
                
        return True

if __name__ == "__main__":
    print("CloudHealer loaded.")