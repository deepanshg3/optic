import sys
import os
import time
import ast
import json
import subprocess
import re

# Ensure Python can find your backend folders
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from backend.database.db_manager import create_incident, get_connection
from backend.agents.llm_api import OpticLLM

# --- PROMPTS ---

# 🚨 THE FIX: Aggressive, strict-enforcement prompt
UNIVERSAL_PATCH_PROMPT = """You are an elite Polyglot Site Reliability Engineer.
You are fixing syntax or structural errors caught by native Git pre-commit scanners across multiple files.

CRITICAL RULE: You MUST output ONLY a raw JSON array. Do NOT wrap the JSON in markdown blocks (no ```json).

The JSON must exactly match this schema and contain an object for EVERY file provided:
[
  {
    "file_path": "the exact file path provided",
    "search_block": "EXACT lines of code to replace. Must be a perfect substring match including indentation. strictly do not autofix it, write the exact lines as per the error",
    "replace_block": "The new lines of code to insert."
  }
]

PATCHING RULES (STRICT ENFORCEMENT):
1. NO PARTIAL LINES: The `search_block` MUST start at the very beginning of a line and end at the very end of a line. 
2. INCLUDE GARBAGE: If a line has trailing syntax errors (e.g., `print("hi")")")`), you MUST include the entire string, garbage included, in the `search_block` so it gets completely overwritten.
3. EXACT MATCH: Copy the target lines exactly as they appear in the snippet, including all leading indentation. Do not invent spaces.
4. NO EXTRA NEWLINES: Do not add extra `\\n` at the end of your `search_block` unless it actually exists in the snippet.
5. Keep the block short (1-3 complete lines).
"""

# --- THE SNIPPET EXTRACTOR ---

def extract_line_number(error_msg):
    match = re.search(r'(?:line\s+|[:\(])(\d+)(?:[:\)])?', error_msg.lower())
    if match:
        return int(match.group(1))
    return 1 

def get_code_snippet(source_code, target_line, up=15, down=5):
    lines = source_code.split('\n')
    start = max(0, target_line - 1 - up)
    end = min(len(lines), target_line + down)
    snippet_lines = lines[start:end]
    return '\n'.join(snippet_lines)

# --- THE TRAFFIC ROUTER (SCANNERS) ---

def check_syntax(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception as e:
        return None, f"Could not read file: {e}"

    if filepath.endswith('.py'):
        try:
            ast.parse(source, filename=filepath)
            return source, None
        except SyntaxError as e:
            return source, f"SyntaxError on line {e.lineno}: {e.msg}\nCode: {e.text}"

    elif filepath.endswith('.json'):
        try:
            json.loads(source)
            return source, None
        except json.JSONDecodeError as e:
            return source, f"JSONDecodeError: {e.msg} at line {e.lineno}"

    elif filepath.endswith(('.js', '.html', '.css', '.ts', '.jsx', '.tsx', '.yaml', '.yml')):
        print(f"⚡ Running native Prettier scan on {filepath}...")
        try:
            result = subprocess.run(
                ["npx", "prettier", "--check", filepath], 
                capture_output=True, 
                text=True
            )
            if result.returncode == 0:
                return source, None
            else:
                error_output = result.stderr if result.stderr else result.stdout
                return source, f"Prettier caught a syntax/formatting error:\n{error_output}"
        except FileNotFoundError:
            return source, "ERROR: Node.js/npx is not installed. Cannot run Prettier."

    return source, None

# --- THE FIXER (HEALER) ---

def ask_llm_for_mega_patch(batched_context):
    """Sends the combined context of ALL broken files to OpticLLM."""
    print(f"🧠 Native scanners caught errors. Waking up Optic LLM for the Mega-Patch...")
    
    llm = OpticLLM()
    user_prompt = f"Please fix the following files based on their error logs and snippets:\n\n{batched_context}"
    
    raw_response = llm.analyze(user_prompt=user_prompt, system_prompt=UNIVERSAL_PATCH_PROMPT)
    
    try:
        clean_text = raw_response.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"❌ LLM failed to generate a valid JSON patch: {e}")
        return []
    
# --- MAIN PIPELINE ---

def main():
    staged_files = sys.argv[1:]
    errors_found = []

    for filepath in staged_files:
        if not os.path.exists(filepath): 
            continue
            
        source_code, error = check_syntax(filepath)
        if error:
            errors_found.append((filepath, error, source_code))

    if not errors_found:
        sys.exit(0)

    print(f"\n🚨 Optic Super Linter intercepted structural errors in {len(errors_found)} file(s)!")
    
    combined_logs = ""
    combined_context = ""
    
    for filepath, error_msg, full_source in errors_found:
        print(f"   -> {filepath}: {error_msg.splitlines()[0]}") 
        
        combined_logs += f"--- {filepath} ---\n{error_msg}\n\n"
        
        error_line = extract_line_number(error_msg)
        snippet = get_code_snippet(full_source, error_line, up=15, down=5)
        combined_context += f"File: {filepath}\nError: {error_msg}\nSnippet:\n{snippet}\n\n"

    real_mega_patch = ask_llm_for_mega_patch(combined_context)

    incident_id = create_incident(
        container_name="Local-Laptop",
        incident_type="BUILD_LINTER",
        crash_logs=combined_logs.strip(),
        ai_diagnosis=f"Pre-commit gate intercepted {len(errors_found)} broken file(s).",
        proposed_patch=real_mega_patch
    )

    print(f"\n⏳ Mega-Ticket #{incident_id} created. Waiting for your review on the Dashboard...")

    while True:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM incidents WHERE id = ?", (incident_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            status = row['status']
            if status == 'RESOLVED_PROCEED':
                print(f"✅ Dashboard Approved! All files patched. Finishing commit...")
                sys.exit(0)
            elif status == 'REJECTED':
                print(f"🚫 Dashboard Rejected! Aborting the commit.")
                sys.exit(1)

        time.sleep(2)

if __name__ == "__main__":
    main()