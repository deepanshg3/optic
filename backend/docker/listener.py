import docker
import os
from backend.system.logger import setup_logger
from backend.ai.agent import CrashAnalyzer

logger = setup_logger("Watcher")

class DockerWatcher:
    # 1. Accept the target_container argument
    def __init__(self, project_path: str, target_container: str):
        self.project_path = os.path.expanduser(project_path)
        self.target_container = target_container
        self.analyzer = CrashAnalyzer()
        
        try:
            self.client = docker.from_env()
            logger.info("👁️ Optic Watcher initialized. Connected to Docker engine.")
        except Exception as e:
            logger.error(f"Failed to connect to Docker: {e}")
            raise

    def listen(self):
        logger.info(f"Targeting Project Directory: {self.project_path}")
        logger.info(f"Targeting Container Name: {self.target_container}")
        logger.info("Listening for container crashes...")
        
        for event in self.client.events(decode=True):
            if event.get('Type') == 'container' and event.get('Action') == 'die':
                
                container_id = event.get('id') or event.get('Actor', {}).get('ID')
                if not container_id:
                    continue
                
                try:
                    container = self.client.containers.get(container_id)
                    
                    # 🎯 2. THE TARGET LOCK FILTER
                    if container.name != self.target_container:
                        continue # Silently ignore crashes from other apps
                        
                    exit_code = event.get('Actor', {}).get('Attributes', {}).get('exitCode')
                    
                    if str(exit_code) != "0":
                        logger.warning(f"🚨 CRASH DETECTED: [{container.name}] (Exit Code: {exit_code})")
                        
                        logs = container.logs(tail=30).decode('utf-8').strip()
                        logger.info("🧠 Handing off to LangGraph Analyzer...")
                        
                        try:
                            analysis_result = self.analyzer.run_analysis(
                                project_path=self.project_path, 
                                container_name=container.name,
                                crash_logs=logs
                            )
                            logger.info(f"\n{'='*60}\n✅ AI DIAGNOSIS & FIX\n{'='*60}\n{analysis_result}\n{'='*60}\n")
                        except Exception as ai_error:
                            logger.error(f"❌ AI Analysis Failed: {ai_error}")
                        
                except docker.errors.NotFound:
                    logger.error(f"⚠️ Container {container_id[:12]} deleted before Optic could read the logs.")
                
                # 🎯 ADD THIS NEW BLOCK HERE
                except docker.errors.APIError as e:
                    if e.response is not None and e.response.status_code == 409:
                        logger.warning(f"⚠️ Container {container_id[:12]} is being forcefully removed. Logs are unavailable.")
                    else:
                        logger.error(f"❌ Docker API Error: {e}")
                
                except docker.errors.NullResource:
                    pass