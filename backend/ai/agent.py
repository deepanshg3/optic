import json
import re
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from backend.system.logger import setup_logger
from backend.ai.llm_api import OpticLLM
from backend.system.workspace_mapper import ContextManager
from backend.ai.prompts import DISPATCHER_PROMPT, RESOLVER_PROMPT

logger = setup_logger("Analyzer")

# 1. Define the State (The memory that passes between nodes)
class GraphState(TypedDict):
    project_path: str
    crash_logs: str
    directory_tree: str
    target_files: List[str]
    file_contents: str
    final_analysis: str

class CrashAnalyzer:
    def __init__(self):
        self.llm = OpticLLM()
        
        # Build the LangGraph workflow
        workflow = StateGraph(GraphState)
        
        # Add our three nodes
        workflow.add_node("dispatch", self.node_dispatch)
        workflow.add_node("fetch_files", self.node_fetch_files)
        workflow.add_node("resolve", self.node_resolve)
        
        # Connect the nodes in order
        workflow.set_entry_point("dispatch")
        workflow.add_edge("dispatch", "fetch_files")
        workflow.add_edge("fetch_files", "resolve")
        workflow.add_edge("resolve", END)
        
        self.app = workflow.compile()

    def node_dispatch(self, state: GraphState) -> GraphState:
        """Call 1: Ask Gemini which files we need to read."""
        logger.info("🧠 Step 1: Dispatcher analyzing logs to find target files...")
        
        user_msg = f"LOGS:\n{state['crash_logs']}\n\nDIRECTORY TREE:\n{state['directory_tree']}"
        response = self.llm.analyze(user_prompt=user_msg, system_prompt=DISPATCHER_PROMPT)
        
        # Clean the response just in case Gemini accidentally adds markdown tags
        clean_json = re.sub(r"```json\n|\n```", "", response.strip())
        
        try:
            target_files = json.loads(clean_json)
            logger.info(f"🎯 Dispatcher requested: {target_files}")
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from Dispatcher: {response}")
            target_files = [] # Fallback
            
        return {"target_files": target_files}

    def node_fetch_files(self, state: GraphState) -> GraphState:
        """Step 2: Python reads the files from the hard drive."""
        if not state.get("target_files"):
            logger.warning("No files requested. Proceeding with logs only.")
            return {"file_contents": "No files requested."}
            
        logger.info("📂 Step 2: Context Manager fetching requested files...")
        ctx = ContextManager(state['project_path'])
        contents = ctx.read_specific_files(state['target_files'])
        return {"file_contents": contents}

    def node_resolve(self, state: GraphState) -> GraphState:
        """Call 3: Gemini reads the code and provides the fix."""
        logger.info("🧠 Step 3: Resolver drafting the final fix...")
        
        user_msg = (
            f"CRASH LOGS:\n{state['crash_logs']}\n\n"
            f"DIRECTORY TREE:\n{state['directory_tree']}\n\n"
            f"FILE CONTENTS:\n{state['file_contents']}"
        )
        
        final_answer = self.llm.analyze(user_prompt=user_msg, system_prompt=RESOLVER_PROMPT)
        return {"final_analysis": final_answer}

    def run_analysis(self, project_path: str, crash_logs: str) -> str:
        """The main entry point to trigger the graph."""
        logger.info("🚀 Starting Optic Analysis Pipeline...")
        
        # Generate the directory tree immediately
        ctx = ContextManager(project_path)
        tree = ctx.get_directory_tree()
        
        initial_state = {
            "project_path": project_path,
            "crash_logs": crash_logs,
            "directory_tree": tree,
            "target_files": [],
            "file_contents": "",
            "final_analysis": ""
        }
        
        # Run the LangGraph state machine
        final_state = self.app.invoke(initial_state)
        return final_state["final_analysis"]