import os
import sys
import shutil  # <-- 🚨 ADDED FOR CLEANUP

# Import our three specialized cloud modules
from parser import SuperLinterParser
from healer import CloudHealer
from github import GitHubDeliveryDriver

def main():
    print("🚀 Booting up Optic Cloud Orchestrator...")

    # 1. Gather Cloud Environment Variables
    # GitHub Actions automatically injects 'GITHUB_WORKSPACE' (the path to the repo)
    workspace_root = os.getenv("GITHUB_WORKSPACE")
    if not workspace_root:
        print("❌ ERROR: GITHUB_WORKSPACE environment variable not found. Are we in the cloud?")
        sys.exit(1)

    # We will tell Super Linter to save its TEXT report to this exact path
    log_file_path = os.path.join(workspace_root, "super-linter.log")

    # Safety Check: The brain needs power
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ CRITICAL: GOOGLE_API_KEY is missing from environment secrets!")
        sys.exit(1)
        
    if not os.getenv("GEMINI_MODEL_NAME"):
        print("❌ CRITICAL: GEMINI_MODEL_NAME is missing from environment secrets!")
        sys.exit(1)

    # --- THE EXECUTION PIPELINE ---

    # Phase 1: Parse the Logs
    print("\n🔍 Phase 1: Parsing Super Linter Logs...")
    parser = SuperLinterParser(log_file_path)
    parsed_errors = parser.parse_errors()

    if not parsed_errors:
        print("✅ No critical errors found in the parsed logs. Optic Bot going back to sleep.")
        sys.exit(0)

    # Phase 2: Heal the Code
    print("\n🧠 Phase 2: Engaging Gemini AI Healer...")
    healer = CloudHealer(workspace_root)
    heal_success = healer.heal_files(parsed_errors)

    if not heal_success:
        print("❌ AI Healer encountered a fatal error during patching. Aborting pipeline.")
        sys.exit(1)

    # === 🚨 NEW JANITOR CLEANUP BLOCK 🚨 ===
    print("\n🧹 Cleaning up workspace before commit...")
    
    # 1. Delete the log file so GitHub Push Protection doesn't block the token
    if os.path.exists(log_file_path):
        os.remove(log_file_path)
        print("   -> Deleted super-linter.log")
        
    # 2. Delete the cloned brain so it doesn't pollute the Tic-Tac-Toe repo
    optic_brain_path = os.path.join(workspace_root, "optic_brain")
    if os.path.exists(optic_brain_path):
        shutil.rmtree(optic_brain_path)
        print("   -> Deleted optic_brain folder")
    # =======================================

    # Phase 3: Deliver the Pull Request
    print("\n🚚 Phase 3: Delivering the Pull Request...")
    driver = GitHubDeliveryDriver(workspace_root)
    delivery_success = driver.deliver_patch()

    if delivery_success:
        print("\n🎉 SUCCESS: Optic Bot has successfully analyzed, patched, and submitted the fix!")
    else:
        print("\n⚠️ Pipeline finished, but delivery phase aborted (no changes detected or push failed).")

if __name__ == "__main__":
    main()