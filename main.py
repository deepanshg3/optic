import sys
import os

from backend.docker.listener import DockerWatcher
from backend.system.logger import setup_logger

logger = setup_logger("Main")

TARGET_APP_PATH = "~/Desktop/tic-tac-toe-main"
TARGET_CONTAINER_NAME = "tictactoe-casualty"  # 🎯 ADD THIS

def main():
    logger.info("🚀 Booting Optic Core...")
    try:
        # Pass the target container name to the watcher
        watcher = DockerWatcher(
            project_path=TARGET_APP_PATH, 
            target_container=TARGET_CONTAINER_NAME
        )
        watcher.listen()
    except KeyboardInterrupt:
        logger.info("🛑 Optic shutting down gracefully.")
    except Exception as e:
        logger.critical(f"❌ Fatal Error: {e}")

if __name__ == "__main__":
    main()