import os
import json
import sys

# Ensure Optic can find your existing LLM class
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.agents.llm_api import OpticLLM

# 🚨 The Cloud-Strict Prompt
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
1. `start_line` and `end_line` are the EXACT integer line numbers from the provided code that contain the error.
2. If the error is on a single line, start_line and end_line will be the SAME number.
3. Your `replace_block` must contain the FULL FIXED CODE for those specific lines, keeping original indentation.
4. Do NOT include line numbers in your replace_block output. Just the raw valid code.
"""

class CloudHealer:
    def __init__(self, workspace_root):
        """
        workspace_root is the absolute path to where Tic-Tac-Toe 
        is downloaded on the GitHub server (usually /github/workspace)
        """
        self.workspace_root = workspace_root
        self.llm = OpticLLM()
        
    def get_numbered_file(self, file_path):
        """Extracts the FULL broken code file directly from the repository with line numbers."""
        full_path = os.path.join(self.workspace_root, file_path)
        
        if not os.path.exists(full_path):
            print(f"⚠️ Warning: Could not find {full_path} on the cloud hard drive.")
            return None, []
            
        with open(full_path, 'r', encoding='utf-8') as f:
            lines = f.read().split('\n')
            
        numbered_lines = []
        for i, line in enumerate(lines):
            # i+1 because humans and linters read Line 1, not Line 0
            numbered_lines.append(f"{i+1} | {line}")
            
        return '\n'.join(numbered_lines), lines
        
    def heal_files(self, parsed_errors):
        """Takes the errors from parser.py, asks Gemini, and overwrites the files."""
        if not parsed_errors:
            print("✅ No errors to heal. Optic Bot is sleeping...")
            return True
            
        print(f"🧠 Waking up Cloud Optic LLM to heal {len(parsed_errors)} broken files...")
        
        # 1. Build the Mega-Context for the LLM
        batched_context = ""
        file_cache = {} # Stores the original file lines so we can rewrite them later
        
        for error in parsed_errors:
            filepath = error['file_path']
            
            # Strip the workspace root so it's a clean relative path (e.g. test_ui.html)
            clean_path = filepath.replace(self.workspace_root + "/", "").strip("/")
            
            # Read the whole file (if we haven't already for a previous error)
            if clean_path not in file_cache:
                numbered_code, original_lines = self.get_numbered_file(clean_path)
                if numbered_code:
                    file_cache[clean_path] = original_lines
                    batched_context += f"\n==================\nFile: {clean_path}\n"
                    batched_context += f"Full Source Code:\n{numbered_code}\n\n"
            
            # Append the exact linter error block below the file context
            batched_context += f"Linter Error Report for {clean_path}:\n{error['error_msg']}\n"

        # 2. Call Gemini for the Mega-Patch
        user_prompt = f"Please fix the following files based on their Super Linter error logs:\n\n{batched_context}"
        print("🤖 Sending full file context to Gemini...")
        raw_response = self.llm.analyze(user_prompt=user_prompt, system_prompt=UNIVERSAL_CLOUD_PROMPT)
        
        try:
            clean_text = raw_response.replace('```json', '').replace('```', '').strip()
            mega_patch = json.loads(clean_text)
        except Exception as e:
            print(f"❌ LLM failed to generate a valid JSON patch: {e}\nRaw Response: {raw_response}")
            return False

        # 3. Apply the Patches directly to the Hard Drive
        print("💉 Applying AI patches to the cloud workspace...")
        
        # Sort patches from bottom to top so line numbers don't shift while applying
        mega_patch.sort(key=lambda x: x.get("start_line", 0), reverse=True)
        
        for patch in mega_patch:
            filepath = patch.get("file_path")
            start = patch.get("start_line")
            end = patch.get("end_line")
            new_code = patch.get("replace_block", "")
            
            if filepath in file_cache and start and end:
                lines = file_cache[filepath]
                
                prefix = lines[:start-1]
                suffix = lines[end:]
                
                # Rebuild the entire file with the AI's new code injected in the middle
                new_file_content = '\n'.join(prefix + [new_code] + suffix)
                
                # Update our cache with the newly injected code in case there are multiple patches for this file
                file_cache[filepath] = new_file_content.split('\n')
                
                # Overwrite the actual file on the server
                full_path = os.path.join(self.workspace_root, filepath)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(new_file_content)
                
                print(f"  -> ✅ Patched {filepath} (Lines {start}-{end})")
                
        return True

if __name__ == "__main__":
    print("CloudHealer loaded.")