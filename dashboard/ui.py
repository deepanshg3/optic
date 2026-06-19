import streamlit as st
import json
import os
import time
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database.db_manager import get_pending_incidents, update_incident_status
from backend.execution.patcher import CodePatcher
from backend.execution.restarter import ContainerRestarter

# --- GLOBAL CONFIG ---
# Hardcoding the target path to match our Watcher daemon
PROJECT_PATH = os.path.expanduser("~/Desktop/tic-tac-toe-main")

# --- UI SETUP ---
st.set_page_config(page_title="Optic Control Center", page_icon="👁️", layout="wide")
st.title("👁️ Optic Control Center")
st.markdown("### Human-in-the-Loop Approval Gate")

# Fetch all PENDING tickets from the SQLite database
incidents = get_pending_incidents()

if not incidents:
    st.success("✅ System Nominal. No pending crashes require your attention.")
    if st.button("Refresh Queue"):
        st.rerun()
else:
    st.warning(f"⚠️ {len(incidents)} container(s) awaiting your review.")
    
    # Loop through each pending crash and build a visual report card
    for incident in incidents:
        with st.expander(f"🚨 Ticket #{incident['id']} | Target: {incident['container_name']} | 🕒 {incident['timestamp']}", expanded=True):
            
            # Create a 2-column layout for easy reading
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Raw Crash Logs")
                st.code(incident['crash_logs'], language="bash")
                
            with col2:
                st.subheader("AI Diagnosis")
                st.write(incident['ai_diagnosis'])
                
            st.subheader("Proposed Code Changes")
            try:
                # The database stores the patch as a string, we load it back into JSON for the UI
                patch_data = json.loads(incident['proposed_patch'])
                st.json(patch_data)
            except json.JSONDecodeError:
                st.warning("No structured patch data was provided by the AI.")
                patch_data = []

            st.markdown("---")
            
            # --- ACTION BUTTONS ---
            btn_col1, btn_col2 = st.columns([1, 5])
            
            with btn_col1:
                if st.button(f"✅ Approve & Deploy Fix", key=f"approve_{incident['id']}", type="primary"):
                    with st.spinner("Rewriting code and rebuilding Docker container..."):
                        try:
                            # 1. Apply the Source Code Patch
                            if patch_data:
                                patcher = CodePatcher(PROJECT_PATH)
                                patcher.apply_patches(patch_data)
                            
                            # 2. Trigger the Cold Rebuild and CAPTURE the result
                            restarter = ContainerRestarter()
                            rebuild_success = restarter.rebuild_and_restart(
                                container_name=incident['container_name'], 
                                project_path=PROJECT_PATH
                            )
                            
                            # 3. ONLY update the ledger if the rebuild actually succeeded
                            if rebuild_success:
                                update_incident_status(incident['id'], 'RESOLVED')
                                st.success("✅ Verified: Container successfully revived and is running!")
                                time.sleep(2)
                                st.rerun() 
                            else:
                                st.error("❌ Rebuild Failed: The backend could not verify the container is running. Check terminal logs.")
                            
                        except Exception as e:
                            st.error(f"Deployment encountered a critical error: {e}")
                            
            with btn_col2:
                if st.button(f"❌ Reject Patch", key=f"reject_{incident['id']}"):
                    update_incident_status(incident['id'], 'REJECTED')
                    st.info("Ticket rejected. Removing from queue...")
                    time.sleep(1)
                    st.rerun()