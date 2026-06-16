import docker
from backend.logger import setup_logger

# Create a specific logger for the Watcher module
logger = setup_logger("Watcher")

class DockerWatcher:
    def __init__(self):
        try:
            self.client = docker.from_env()
            logger.info("👁️ Optic Watcher initialized. Connected to Docker engine.")
        except Exception as e:
            logger.error(f"Failed to connect to Docker: {e}")
            raise

    def listen(self):
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
                        logs = container.logs(tail=15).decode('utf-8').strip()
                        
                        logger.info(f"📋 Raw Crash Logs:\n{'-'*50}\n{logs}\n{'-'*50}")
                        logger.info("🧠 Hand-off to LangGraph Collector pending.")
                        
                except docker.errors.NotFound:
                    logger.error(f"⚠️ Container {container_id[:12]} deleted before Optic could read the logs.")
                except docker.errors.NullResource:
                    pass