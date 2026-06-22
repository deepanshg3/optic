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

    def deliver_patch(self):
        """Creates a branch, commits the fixes, and opens a PR."""
        if not self.has_changes():
            print("✅ No files were changed by the LLM. Aborting PR delivery.")
            return False

        print("📦 Packaging AI fixes for delivery...")

        # 1. Configure the Cloud Git User (So GitHub knows who is committing)
        self.run_cmd('git config --global user.name "Optic Bot 🤖"')
        self.run_cmd('git config --global user.email "optic-bot@github.actions"')

        # 2. Create a unique branch name using the current timestamp
        branch_name = f"optic-auto-fix-{int(time.time())}"
        
        print(f"🌿 Creating new branch: {branch_name}")
        self.run_cmd(f"git checkout -b {branch_name}")

        # 3. Add and Commit the fixed files
        self.run_cmd("git add .")
        self.run_cmd('git commit -m "🤖 Optic Auto-Healer: Fixed Super Linter Syntax Errors"')

        # 4. Push the branch to the cloud repository
        print("🚀 Pushing branch to origin...")
        success, _ = self.run_cmd(f"git push origin {branch_name}")
        
        if not success:
            print("❌ Failed to push branch. Check token permissions.")
            return False

        # 5. Open the Pull Request using the pre-installed GitHub CLI
        print("📝 Opening Pull Request...")
        pr_title = "🤖 Optic Bot: Code Quality Fixes"
        pr_body = (
            "### 🚨 Super Linter Intercepted Errors\n"
            "Optic Bot caught structural or syntax errors during your recent push. "
            "Gemini AI has analyzed the logs and generated this patch.\n\n"
            "**Please review the file changes before merging.**"
        )
        
        # The 'gh' CLI uses the GITHUB_TOKEN automatically from the environment
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