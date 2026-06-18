import os
from backend.system.logger import setup_logger

logger = setup_logger("Patcher")

class CodePatcher:
    def __init__(self, project_path: str):
        self.project_path = project_path

    def apply_patches(self, patches: list) -> bool:
        """
        Takes a list of patch JSON objects and safely applies them to the local files.
        Returns True if all patches succeed, False if any fail.
        """
        all_success = True
        
        for patch in patches:
            file_path = patch.get("file_path")
            search_block = patch.get("search_block")
            # Default to empty string if it's a deletion
            replace_block = patch.get("replace_block", "") 

            if not file_path or not search_block:
                logger.error("❌ Invalid patch format: missing file_path or search_block.")
                all_success = False
                continue

            full_path = os.path.join(self.project_path, file_path)
            
            if not os.path.exists(full_path):
                logger.error(f"❌ File not found for patching: {full_path}")
                all_success = False
                continue

            try:
                # 1. Read the original file
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 2. Strict matching validation
                if search_block not in content:
                    logger.error(f"❌ Search block mismatch in {file_path}. The AI likely hallucinated indentation or spacing.")
                    logger.debug(f"EXPECTED BLOCK:\n{search_block}")
                    all_success = False
                    continue

                # 3. Apply the patch
                new_content = content.replace(search_block, replace_block)

                # 4. Write it back to the drive
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                logger.info(f"✅ Successfully patched: {file_path}")

            except Exception as e:
                logger.error(f"❌ Fatal error while patching {file_path}: {e}")
                all_success = False

        return all_success