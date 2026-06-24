import os
import json
import sys

# Ensure Optic can find your existing modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.agents.llm_api import OpticLLM
from backend.core.workspace_mapper import ContextManager

# --- PROMPTS ---
DETECTIVE_PROMPT = """You are an elite AI debugging detective.
A production crash occurred. Here is the project directory tree.
Identify the single file most likely to contain the code causing this error based on standard web development patterns.

CRITICAL RULE: Return ONLY a raw JSON object. No markdown, no explanations.
{
  "target_file": "relative/path/to/suspect_file.js"
}
"""

UNIVERSAL_CLOUD_PROMPT = """You are an elite Polyglot Site Reliability Engineer operating in a headless CI/CD cloud environment.
You are fixing errors to ensure production stability.

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

# --- THE AGENT ---
class CloudHealer:
    def __init__(self, workspace_root):
        self.workspace_root = workspace_root
        self.llm = OpticLLM()
        
    def hunt_for_file(self, error_msg):
        """Step 1 of Agentic Workflow: Scan the repo and find the broken file."""
        print("\n🕵️ Engaging Agentic Detective Mode...")
        # Using your existing workspace_mapper!
        manager = ContextManager(self.workspace_root)
        tree = manager.get_directory_tree()
        
        user_prompt = f"Production Crash Error:\n{error_msg}\n\nProject Structure:\n{tree}"
        print("🗺️ Sending directory map to Gemini to locate the bug...")
        
        raw_response = self.llm.analyze(user_prompt=user_prompt, system_prompt=DETECTIVE_PROMPT)
        
        try:
            clean_text = raw_response.replace('```json', '').replace('```', '').strip()
            data = json.loads(clean_text)
            target = data.get("target_file")
            print(f"🎯 AI Detective pinpointed the suspect file: {target}")
            return target
        except Exception as e:
            print(f"❌ AI Detective failed to pinpoint the file: {e}\nRaw: {raw_response}")
            return None

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
            numbered_lines.append(f"{i+1} | {line}")
            
        return '\n'.join(numbered_lines), lines
        
    def heal_files(self, parsed_errors):
        """Takes the errors, asks Gemini, and overwrites the files."""
        if not parsed_errors:
            print("✅ No errors to heal. Optic Bot is sleeping...")
            return True
            
        print(f"🧠 Waking up Cloud Optic LLM to heal {len(parsed_errors)} errors...")
        
        batched_context = ""
        file_cache = {} 
        
        for error in parsed_errors:
            filepath = error['file_path']
            
            # === AGENTIC INTERCEPTION ===
            if filepath == "UNKNOWN":
                filepath = self.hunt_for_file(error['error_msg'])
                if not filepath:
                    print("⏭️ Skipping this error because the Detective couldn't find the file.")
                    continue
                error['file_path'] = filepath
            # ==============================
            
            clean_path = filepath.replace(self.workspace_root + "/", "").strip("/")
            
            if clean_path not in file_cache:
                numbered_code, original_lines = self.get_numbered_file(clean_path)
                if numbered_code:
                    file_cache[clean_path] = original_lines
                    batched_context += f"\n==================\nFile: {clean_path}\n"
                    batched_context += f"Full Source Code:\n{numbered_code}\n\n"
            
            batched_context += f"Error Report for {clean_path}:\n{error['error_msg']}\n"

        if not file_cache:
            print("❌ Aborting: No valid files were found to heal.")
            return False

        user_prompt = f"Please fix the following files based on their error logs:\n\n{batched_context}"
        print("🤖 Sending full file context to Gemini to generate the patch...")
        raw_response = self.llm.analyze(user_prompt=user_prompt, system_prompt=UNIVERSAL_CLOUD_PROMPT)
        
        try:
            clean_text = raw_response.replace('```json', '').replace('```', '').strip()
            mega_patch = json.loads(clean_text)
        except Exception as e:
            print(f"❌ LLM failed to generate a valid JSON patch: {e}\nRaw Response: {raw_response}")
            return False

        print("💉 Applying AI patches to the cloud workspace...")
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
                
                new_file_content = '\n'.join(prefix + [new_code] + suffix)
                file_cache[filepath] = new_file_content.split('\n')
                
                full_path = os.path.join(self.workspace_root, filepath)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(new_file_content)
                
                print(f"  -> ✅ Patched {filepath} (Lines {start}-{end})")
                
        return True

if __name__ == "__main__":
    print("Agentic CloudHealer loaded.")