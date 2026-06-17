import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.watcher import DockerWatcher
from backend.logger import setup_logger

logger = setup_logger("Main")

# Point this exactly to the app you are monitoring
TARGET_APP_PATH = "~/Desktop/tic-tac-toe-main"

def main():
    logger.info("🚀 Booting Optic Core...")
    try:
        watcher = DockerWatcher(project_path=TARGET_APP_PATH)
        watcher.listen()
    except KeyboardInterrupt:
        logger.info("🛑 Optic shutting down gracefully.")
    except Exception as e:
        logger.critical(f"❌ Fatal Error: {e}")

if __name__ == "__main__":
    main()