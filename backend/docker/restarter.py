import docker
from backend.system.logger import setup_logger

logger = setup_logger("Restarter")

class ContainerRestarter:
    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            logger.error(f"Failed to connect to Docker Daemon in Restarter: {e}")

    def rebuild_and_restart(self, container_name: str, project_path: str) -> bool:
        """
        Executes a full 'Cold Rebuild' by deleting the broken container, 
        rebuilding its image from the patched source, and launching a fresh instance.
        """
        logger.info(f"🔄 Initiating Cold Rebuild for: [{container_name}]")
        
        try:
            # 1. Inspect the dead container to get its blueprint
            old_container = self.client.containers.get(container_name)
            image_name = old_container.attrs['Config']['Image']
            
            # Save the port mappings so we don't lose external access
            # Format looks like: {'3000/tcp': [{'HostIp': '', 'HostPort': '3000'}]}
            ports = old_container.attrs['HostConfig']['PortBindings'] or {}
            
            # Clean up the format for the run() command
            run_ports = {}
            for container_port, host_bindings in ports.items():
                if host_bindings:
                    run_ports[container_port] = host_bindings[0]['HostPort']

            # 2. Nuke the old dead container to free up the name
            logger.info("🗑️ Removing corrupted container...")
            old_container.remove(force=True)

            # 3. Rebuild the image from the newly patched directory
            logger.info(f"🏗️ Rebuilding image '{image_name}'... (This may take a minute)")
            self.client.images.build(path=project_path, tag=image_name, rm=True)

            # 4. Spin up the new container
            logger.info("🚀 Launching patched container...")
            self.client.containers.run(
                image_name,
                name=container_name,
                detach=True,
                ports=run_ports
            )
            
            logger.info(f"✅ [{container_name}] successfully rebuilt and running!")
            logger.info(f"👁️ Optic is now actively monitoring the new [{container_name}] instance.")
            return True

        except docker.errors.BuildError as e:
            logger.error(f"❌ Docker Build Failed. The AI patch might be invalid.")
            for line in e.build_log:
                if 'stream' in line:
                    logger.error(line['stream'].strip())
            return False
        except docker.errors.NotFound:
            logger.error(f"❌ Could not find container [{container_name}] to rebuild.")
            return False
        except Exception as e:
            logger.error(f"❌ Fatal error during rebuild: {e}")
            return False