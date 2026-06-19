import sys
import os
from backend.core.logger import setup_logger
from backend.core.watcher import DockerWatcher
from backend.database.db_manager import init_db

# 🎯 Create the logger for the main file
logger = setup_logger("Main")

if __name__ == "__main__":
    try:
        logger.info("🚀 Booting Optic Core from Modular Layout...")
        
        # 1. Initialize the database
        init_db()
        
        # 2. Configure our targets
        PROJECT_PATH = "~/Desktop/tic-tac-toe-main"
        TARGET_CONTAINER = "tictactoe-casualty"
        
        # 3. Boot the Watcher and start listening
        watcher = DockerWatcher(project_path=PROJECT_PATH, target_container=TARGET_CONTAINER)
        watcher.listen()
        
    except KeyboardInterrupt:
        logger.info("👋 Optic Core gracefully shutting down.")
        sys.exit(0)