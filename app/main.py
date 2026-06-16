import sys
import os

# Ensure Python can find the 'backend' package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.watcher import DockerWatcher
from backend.logger import setup_logger

logger = setup_logger("Main")

def main():
    logger.info("🚀 Booting Optic Core...")
    try:
        watcher = DockerWatcher()
        watcher.listen()
    except KeyboardInterrupt:
        logger.info("🛑 Optic shutting down gracefully.")
    except Exception as e:
        logger.critical(f"❌ Fatal Error: {e}")

if __name__ == "__main__":
    main()