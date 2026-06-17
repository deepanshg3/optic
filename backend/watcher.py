import docker
import os
from backend.logger import setup_logger
from backend.analyzer import CrashAnalyzer

# Create a specific logger for the Watcher module
logger = setup_logger("Watcher")

class DockerWatcher:
    # We now pass the project path in when we start the watcher
    def __init__(self, project_path: str):
        self.project_path = os.path.expanduser(project_path)
        self.analyzer = CrashAnalyzer()  # Boot up the LangGraph Brain
        
        try:
            self.client = docker.from_env()
            logger.info("👁️ Optic Watcher initialized. Connected to Docker engine.")
        except Exception as e:
            logger.error(f"Failed to connect to Docker: {e}")
            raise

    def listen(self):
        logger.info(f"Targeting Project Directory: {self.project_path}")
        logger.info("Listening for container crashes...")
        
        for event in self.client.events(decode=True):
            if event.get('Type') == 'container' and event.get('Action') == 'die':
                
                container_id = event.get('id') or event.get('Actor', {}).get('ID')
                if not container_id:
                    continue
                
                try:
                    container = self.client.containers.get(container_id)
                    exit_code = event.get('Actor', {}).get('Attributes', {}).get('exitCode')
                    
                    if str(exit_code) != "0":
                        logger.warning(f"🚨 CRASH DETECTED: [{container.name}] (Exit Code: {exit_code})")
                        
                        # Bumped to 30 lines to grab the full stack trace
                        logs = container.logs(tail=30).decode('utf-8').strip()
                        
                        logger.info("🧠 Handing off to LangGraph Analyzer...")
                        
                        # --- THE AI TRIGGER ---
                        try:
                            analysis_result = self.analyzer.run_analysis(
                                project_path=self.project_path, 
                                crash_logs=logs
                            )
                            logger.info(f"\n{'='*60}\n✅ AI DIAGNOSIS & FIX\n{'='*60}\n{analysis_result}\n{'='*60}\n")
                        except Exception as ai_error:
                            logger.error(f"❌ AI Analysis Failed: {ai_error}")
                        
                except docker.errors.NotFound:
                    logger.error(f"⚠️ Container {container_id[:12]} deleted before Optic could read the logs.")
                except docker.errors.NullResource:
                    pass