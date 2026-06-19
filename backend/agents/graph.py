import json
import re
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from backend.core.logger import setup_logger
from backend.agents.llm_api import OpticLLM
from backend.core.workspace_mapper import ContextManager
from backend.agents.prompts import DISPATCHER_PROMPT, RESOLVER_PROMPT
from backend.database.db_manager import create_incident # 🎯 NEW DB IMPORT

logger = setup_logger("Analyzer")

class GraphState(TypedDict):
    project_path: str
    container_name: str
    crash_logs: str
    directory_tree: str
    target_files: List[str]
    file_contents: str
    final_analysis: str # Holds the AI's JSON output

class CrashAnalyzer:
    def __init__(self):
        self.llm = OpticLLM()
        
        workflow = StateGraph(GraphState)
        
        # 🎯 We only need 3 nodes now! The AI just thinks, it doesn't execute.
        workflow.add_node("dispatch", self.node_dispatch)
        workflow.add_node("fetch_files", self.node_fetch_files)
        workflow.add_node("resolve", self.node_resolve)
        
        # Execution path
        workflow.set_entry_point("dispatch")
        workflow.add_edge("dispatch", "fetch_files")
        workflow.add_edge("fetch_files", "resolve")
        workflow.add_edge("resolve", END) # 🎯 Graph stops here!
        
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

    def run_analysis(self, project_path: str, container_name: str, crash_logs: str) -> int:
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
            "final_analysis": ""
        }
        
        # Run the AI Graph
        final_state = self.app.invoke(initial_state)
        
        # 🎯 NEW: Parse the AI's answer and save to Database instead of patching!
        ai_output = final_state["final_analysis"]
        
        try:
            parsed_data = json.loads(ai_output)
            diagnosis = parsed_data.get("analysis", "No diagnosis provided.")
            patch = parsed_data.get("patches", [])
        except json.JSONDecodeError:
            diagnosis = ai_output
            patch = []
            
        logger.info("🗄️ Step 4: Saving proposed fix to Database for human review...")
        
        incident_id = create_incident(
            container_name=container_name,
            crash_logs=crash_logs,
            ai_diagnosis=diagnosis,
            proposed_patch=patch
        )
        
        logger.info(f"✅ Analysis complete! Ticket #{incident_id} is waiting in the Dashboard.")
        return incident_id # Return the ticket number back to the Watcher