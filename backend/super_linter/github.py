import os
import subprocess
import time

class GitHubDeliveryDriver:
    def __init__(self, workspace_root):
        """
        Initializes the driver in the Tic-Tac-Toe workspace.
        Requires GITHUB_TOKEN to be present in the environment variables.
        """
        self.workspace_root = workspace_root
        
        # Change the working directory to the Tic-Tac-Toe repo
        os.chdir(self.workspace_root)

    def run_cmd(self, command):
        """Helper function to run terminal commands and return the output."""
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True
        )
        if result.returncode != 0:
            print(f"⚠️ Command failed: {command}")
            print(f"Error: {result.stderr.strip()}")
        return result.returncode == 0, result.stdout.strip()

    def has_changes(self):
        """Checks if the LLM actually modified any files."""
        success, output = self.run_cmd("git status --porcelain")
        return bool(output) # Returns True if there are modified files

    def deliver_patch(self, mode="linter"):
        """Creates a branch, commits the fixes, and opens a PR based on the crash mode."""
        if not self.has_changes():
            print("✅ No files were changed by the LLM. Aborting PR delivery.")
            return False

        print(f"📦 Packaging AI {mode.upper()} fixes for delivery...")

        # 1. Configure the Cloud Git User
        self.run_cmd('git config --global user.name "Optic Bot 🤖"')
        self.run_cmd('git config --global user.email "optic-bot@github.actions"')

        # === 🚨 DYNAMIC BREADCRUMB ROUTER 🚨 ===
        timestamp = int(time.time())
        
        if mode == "docker":
            branch_name = f"optic-docker-fix-{timestamp}"
            commit_msg = "🐳 Optic Auto-Healer: Fixed Docker Runtime Crash"
            pr_title = "🐳 Optic Bot: Docker Runtime Crash Fix"
            pr_body = (
                "### 🚨 Docker Container Crash Intercepted\n"
                "The Optic Auto-Healer detected a crash during the 10-second Docker test drive. "
                "Gemini AI has analyzed the container logs and generated this patch.\n\n"
                "**Merging this PR will automatically trigger a new Docker test drive to verify the fix.**"
            )
        else:
            branch_name = f"optic-linter-fix-{timestamp}"
            commit_msg = "🤖 Optic Auto-Healer: Fixed Super Linter Syntax Errors"
            pr_title = "🤖 Optic Bot: Code Quality Fixes"
            pr_body = (
                "### 🚨 Super Linter Intercepted Errors\n"
                "Optic Bot caught structural or syntax errors during your recent push. "
                "Gemini AI has analyzed the logs and generated this patch.\n\n"
                "**Please review the file changes before merging.**"
            )
        # =======================================

        # 2. Create the uniquely named branch
        print(f"🌿 Creating new branch: {branch_name}")
        self.run_cmd(f"git checkout -b {branch_name}")

        # 3. Add and Commit the fixed files
        self.run_cmd("git add .")
        self.run_cmd(f'git commit -m "{commit_msg}"')

        # 4. Push the branch to the cloud repository
        print("🚀 Pushing branch to origin...")
        success, _ = self.run_cmd(f"git push origin {branch_name}")
        
        if not success:
            print("❌ Failed to push branch. Check token permissions.")
            return False

        # 5. Open the Pull Request
        print("📝 Opening Pull Request...")
        pr_command = f'gh pr create --title "{pr_title}" --body "{pr_body}" --base main --head {branch_name}'
        pr_success, pr_output = self.run_cmd(pr_command)

        if pr_success:
            print(f"✅ Pull Request successfully created! URL: {pr_output}")
            return True
        else:
            print("❌ Failed to create Pull Request.")
            return False

if __name__ == "__main__":
    print("GitHubDeliveryDriver loaded.")