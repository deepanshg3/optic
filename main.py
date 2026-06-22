import sys
import os
import time
import subprocess
from backend.core.logger import setup_logger
from backend.core.watcher import DockerWatcher
from backend.database.db_manager import init_db

# 🎯 Create the logger for the main file
logger = setup_logger("Main")

if __name__ == "__main__":
    streamlit_process = None
    try:
        logger.info("🚀 Booting Optic Core from Modular Layout...")
        
        # 1. Initialize the database
        init_db()
        
        # 2. Launch Streamlit Dashboard as a Child Process
        logger.info("🌐 Spinning up Streamlit Control Center...")
        ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'dashboard', 'ui.py'))
        
        # Popen runs the command in the background without blocking the script
        streamlit_process = subprocess.Popen(["streamlit", "run", ui_path])
        
        # Give the dashboard a brief moment to grab port 8501 before the terminal gets messy
        time.sleep(2)
        
        # 3. Configure our targets
        PROJECT_PATH = "~/Desktop/tic-tac-toe-main"
        TARGET_CONTAINER = "tictactoe-casualty"
        
        # 4. Boot the Watcher and start listening (This blocks the main thread)
        watcher = DockerWatcher(project_path=PROJECT_PATH, target_container=TARGET_CONTAINER)
        watcher.listen()
        
    except KeyboardInterrupt:
        logger.info("\n👋 Optic Core gracefully shutting down.")
        
        # Cleanup: Kill the Streamlit child process so it doesn't leave a zombie port open
        if streamlit_process:
            logger.info("🛑 Terminating Streamlit Dashboard...")
            streamlit_process.terminate()
            streamlit_process.wait()
            
        sys.exit(0)