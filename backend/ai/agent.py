import json
import re
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from backend.system.logger import setup_logger
from backend.ai.llm_api import OpticLLM
from backend.system.workspace_mapper import ContextManager
from backend.ai.prompts import DISPATCHER_PROMPT, RESOLVER_PROMPT
from backend.system.patcher import CodePatcher
from backend.docker.restarter import ContainerRestarter  # 🎯 IMPORT THE RESTARTER

logger = setup_logger("Analyzer")

class GraphState(TypedDict):
    project_path: str
    container_name: str  # Kept in memory to target the rebuild
    crash_logs: str
    directory_tree: str
    target_files: List[str]
    file_contents: str
    final_analysis: str
    patch_successful: bool
    restart_successful: bool  # Tracking recovery verification

class CrashAnalyzer:
    def __init__(self):
        self.llm = OpticLLM()
        
        workflow = StateGraph(GraphState)
        
        # Define all 5 nodes of the operational cycle
        workflow.add_node("dispatch", self.node_dispatch)
        workflow.add_node("fetch_files", self.node_fetch_files)
        workflow.add_node("resolve", self.node_resolve)
        workflow.add_node("patch_code", self.node_patch_code)
        workflow.add_node("restart_container", self.node_restart_container)  # 🎯 ADD NODE
        
        # Execution path
        workflow.set_entry_point("dispatch")
        workflow.add_edge("dispatch", "fetch_files")
        workflow.add_edge("fetch_files", "resolve")
        workflow.add_edge("resolve", "patch_code")
        workflow.add_edge("patch_code", "restart_container")  # Route patch to restart
        workflow.add_edge("restart_container", END)
        
        self.app = workflow.compile()

    def node_dispatch(self, state: GraphState) -> GraphState:
        logger.info("🧠 Step 1: Dispatcher analyzing logs to find target files...")
        user_msg = f"LOGS:\n{state['crash_logs']}\n\nDIRECTORY TREE:\n{state['directory_tree']}"
        response = self.llm.analyze(user_prompt=user_msg, system_prompt=DISPATCHER_PROMPT)
        clean_json = re.sub(r"```json\n|\n```", "", response.strip())
        try:
            target_files = json.loads(clean_json)
            logger.info(f"🎯 Dispatcher requested: {target_files}")
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from Dispatcher: {response}")
            target_files = []
        return {"target_files": target_files}

    def node_fetch_files(self, state: GraphState) -> GraphState:
        if not state.get("target_files"):
            logger.warning("No files requested. Proceeding with logs only.")
            return {"file_contents": "No files requested."}
        logger.info("📂 Step 2: Context Manager fetching requested files...")
        ctx = ContextManager(state['project_path'])
        contents = ctx.read_specific_files(state['target_files'])
        return {"file_contents": contents}

    def node_resolve(self, state: GraphState) -> GraphState:
        logger.info("🧠 Step 3: Resolver drafting the final fix...")
        user_msg = (
            f"CRASH LOGS:\n{state['crash_logs']}\n\n"
            f"DIRECTORY TREE:\n{state['directory_tree']}\n\n"
            f"FILE CONTENTS:\n{state['file_contents']}"
        )
        raw_answer = self.llm.analyze(user_prompt=user_msg, system_prompt=RESOLVER_PROMPT)
        clean_json = re.sub(r"```json\n|\n```", "", raw_answer.strip())
        return {"final_analysis": clean_json}

    def node_patch_code(self, state: GraphState) -> GraphState:
        logger.info("🛠️ Step 4: Patcher attempting to apply code fixes...")
        try:
            resolution_data = json.loads(state["final_analysis"])
            patches = resolution_data.get("patches", [])
            if not patches:
                logger.warning("No patches requested by the AI.")
                return {"patch_successful": False}
            patcher = CodePatcher(state["project_path"])
            success = patcher.apply_patches(patches)
            return {"patch_successful": success}
        except json.JSONDecodeError:
            logger.error(f"Failed to parse Resolver JSON output.")
            return {"patch_successful": False}

    def node_restart_container(self, state: GraphState) -> GraphState:
        """🎯 Step 5: Execute cold rebuild if patches were applied."""
        if not state.get("patch_successful"):
            logger.warning("Skipping restart because code patching failed or was skipped.")
            return {"restart_successful": False}
            
        logger.info("🔌 Step 5: Routing to Container Restarter for deployment...")
        restarter = ContainerRestarter()
        success = restarter.rebuild_and_restart(
            container_name=state["container_name"],
            project_path=state["project_path"]
        )
        return {"restart_successful": success}

    def run_analysis(self, project_path: str, container_name: str, crash_logs: str) -> str:
        logger.info("🚀 Starting Optic Analysis Pipeline...")
        ctx = ContextManager(project_path)
        tree = ctx.get_directory_tree()
        
        initial_state = {
            "project_path": project_path,
            "container_name": container_name,
            "crash_logs": crash_logs,
            "directory_tree": tree,
            "target_files": [],
            "file_contents": "",
            "final_analysis": "",
            "patch_successful": False,
            "restart_successful": False
        }
        
        final_state = self.app.invoke(initial_state)
        try:
            analysis_text = json.loads(final_state["final_analysis"]).get("analysis", final_state["final_analysis"])
        except:
            analysis_text = final_state["final_analysis"]
            
        return (
            f"{analysis_text}\n\n"
            f"🔹 Patch Successful: {final_state['patch_successful']}\n"
            f"🔹 Container Revived: {final_state['restart_successful']}"
        )