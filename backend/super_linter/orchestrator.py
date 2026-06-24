import os
import sys
import shutil

# Import our three specialized cloud modules
from parser import SuperLinterParser
from healer import CloudHealer
from github import GitHubDeliveryDriver

def main():
    print("🚀 Booting up Optic Cloud Orchestrator...")

    # 1. Gather Cloud Environment Variables
    workspace_root = os.getenv("GITHUB_WORKSPACE")
    if not workspace_root:
        print("❌ ERROR: GITHUB_WORKSPACE environment variable not found. Are we in the cloud?")
        sys.exit(1)

    # Safety Check: The brain needs power
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ CRITICAL: GOOGLE_API_KEY is missing from environment secrets!")
        sys.exit(1)
        
    if not os.getenv("GEMINI_MODEL_NAME"):
        print("❌ CRITICAL: GEMINI_MODEL_NAME is missing from environment secrets!")
        sys.exit(1)

    # === DYNAMIC LOG DETECTION ENGINE ===
    # Define our three target log paths
    sentry_log_path = os.path.join(workspace_root, "sentry-alert.log")
    docker_log_path = os.path.join(workspace_root, "docker-crash.log")
    linter_log_path = os.path.join(workspace_root, "super-linter.log")
    
    log_file_path = None
    pipeline_mode = None

    # Check for Sentry Production Alerts FIRST (Highest Priority)
    if os.path.exists(sentry_log_path):
        log_file_path = sentry_log_path
        pipeline_mode = "sentry"
        print("🚨 STATE DETECTED: Running in LIVE SENTRY PRODUCTION HEALING mode.")
    # Check for Docker crash logs next
    elif os.path.exists(docker_log_path):
        log_file_path = docker_log_path
        pipeline_mode = "docker"
        print("🐳 STATE DETECTED: Running in LIVE DOCKER CONTAINER HEALING mode.")
    # Fallback to Super Linter logs
    elif os.path.exists(linter_log_path):
        log_file_path = linter_log_path
        pipeline_mode = "linter"
        print("📄 STATE DETECTED: Running in SUPER LINTER SYNTAX HEALING mode.")
    else:
        print("❌ ERROR: Neither sentry-alert.log, docker-crash.log, nor super-linter.log was found in the workspace!")
        sys.exit(1)
    # ====================================

    # --- THE EXECUTION PIPELINE ---

    # Phase 1: Parse the Logs
    print(f"\n🔍 Phase 1: Parsing {pipeline_mode.upper()} Logs...")
    
    if pipeline_mode == "sentry":
        # Sentry sends raw text, not Linter syntax. Bypass the parser and read it directly!
        with open(log_file_path, "r") as f:
            raw_error = f.read().strip()
            
        if raw_error:
            # 🚨 THE FIX: Disguise the Sentry string as a structured Linter dictionary
            parsed_errors = [{
                "file_path": "src/App.js", # <--- ⚠️ CHANGE THIS to the actual file where your crash button lives! (e.g., App.js, script.js, index.html)
                "error_message": f"SENTRY PRODUCTION CRASH: {raw_error}",
                "line": "UNKNOWN"
            }]
            print(f"✅ Sentry Error Extracted and Packaged: {raw_error}")
        else:
            parsed_errors = []
            print("⚠️ Sentry log file was empty.")
    else:
        # Docker and Linter logs still use the strict SuperLinter parser
        parser = SuperLinterParser(log_file_path)
        parsed_errors = parser.parse_errors()

    if not parsed_errors:
        print(f"✅ No critical errors found in the parsed {pipeline_mode} logs. Optic Bot going back to sleep.")
        sys.exit(0)

    # Phase 2: Heal the Code
    print("\n🧠 Phase 2: Engaging Gemini AI Healer...")
    healer = CloudHealer(workspace_root)
    heal_success = healer.heal_files(parsed_errors)

    if not heal_success:
        print("❌ AI Healer encountered a fatal error during patching. Aborting pipeline.")
        sys.exit(1)

    # === 🚨 EXTENDED JANITOR CLEANUP BLOCK 🚨 ===
    print("\n🧹 Cleaning up workspace before commit...")
    
    # 1. Clean up whichever log file triggered this workflow
    if os.path.exists(log_file_path):
        os.remove(log_file_path)
        print(f"   -> Deleted active tracking log: {os.path.basename(log_file_path)}")
        
    # 2. Delete the cloned brain so it doesn't pollute the Tic-Tac-Toe repo
    optic_brain_path = os.path.join(workspace_root, "optic_brain")
    if os.path.exists(optic_brain_path):
        shutil.rmtree(optic_brain_path)
        print("   -> Deleted optic_brain folder")
    # =======================================

    # Phase 3: Deliver the Pull Request
    print("\n🚚 Phase 3: Delivering the Pull Request...")
    # Pass the mode into the driver so it knows which breadcrumb to drop!
    driver = GitHubDeliveryDriver(workspace_root)
    delivery_success = driver.deliver_patch(mode=pipeline_mode)

    if delivery_success:
        print(f"\n🎉 SUCCESS: Optic Bot has successfully fixed your {pipeline_mode} issues!")
    else:
        print("\n⚠️ Pipeline finished, but delivery phase aborted (no changes detected or push failed).")

if __name__ == "__main__":
    main()