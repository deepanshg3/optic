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
PROJECT_PATH = os.path.expanduser("~/Desktop/tic-tac-toe-main")

# --- UI SETUP ---
st.set_page_config(page_title="Optic Control Center", page_icon="👁️", layout="wide")
st.title("👁️ Optic Control Center")
st.markdown("### Human-in-the-Loop Approval Gate")

# Fetch all active PENDING items from the database
incidents = get_pending_incidents()

if not incidents:
    st.success("✅ System Nominal. No pending issues require your attention.")
    if st.button("Refresh Queue"):
        st.rerun()
else:
    st.warning(f"⚠️ {len(incidents)} gate ticket(s) awaiting your validation.")
    
    for incident in incidents:
        incident_type = incident.get('incident_type', 'RUNTIME_SENTRY')
        ticket_id = incident['id']
        
        with st.expander(f"🚨 Ticket #{ticket_id} | Type: {incident_type} | Target: {incident['container_name']}", expanded=True):
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Raw Crash Logs")
                st.code(incident['crash_logs'], language="bash")
                
            with col2:
                st.subheader("AI Diagnosis")
                st.write(incident['ai_diagnosis'])
                
            st.subheader("Proposed Code Changes")
            try:
                patch_data = json.loads(incident['proposed_patch'])
                st.json(patch_data)
            except json.JSONDecodeError:
                st.warning("No structured patch layout provided.")
                patch_data = []

            st.markdown("---")
            
            # --- ACTION GATE PIPELINE ---
            btn_col1, btn_col2 = st.columns([1, 5])
            
            with btn_col1:
                is_linter = (incident_type == 'BUILD_LINTER')
                button_label = "✅ Fix & Continue Commit" if is_linter else "✅ Approve & Deploy Fix"
                
                if st.button(button_label, key=f"approve_{ticket_id}", type="primary"):
                    with st.spinner("Executing core automated remediation sequence..."):
                        try:
                            patcher = CodePatcher(PROJECT_PATH)
                            
                            # 1. Universal Patch Application (No more branching here!)
                            if patch_data:
                                patch_success = patcher.apply_patches(patch_data)
                                if not patch_success:
                                    st.error("❌ Patch application failed. Check the backend logs.")
                                    st.stop()
                                    
                            # 2. Branch Post-Execution Routine
                            if is_linter:
                                # Build-Time: Unfreeze terminal
                                update_incident_status(ticket_id, 'RESOLVED_PROCEED')
                                st.success("✅ Codebase repaired! Hook released. Local Git transaction finalizing...")
                                time.sleep(1.5)
                                st.rerun()
                            else:
                                # Run-Time: Restart Docker container
                                restarter = ContainerRestarter()
                                rebuild_success = restarter.rebuild_and_restart(
                                    container_name=incident['container_name'], 
                                    project_path=PROJECT_PATH
                                )
                                
                                if rebuild_success:
                                    update_incident_status(ticket_id, 'RESOLVED')
                                    st.success("✅ Container pipeline successfully verified online!")
                                    time.sleep(1.5)
                                    st.rerun() 
                                else:
                                    st.error("❌ Rebuild Interrupted: Verification target failed healthchecks.")
                                
                        except Exception as e:
                            st.error(f"Deployment pipeline failure: {e}")
                            
            with btn_col2:
                reject_label = "🚫 Abort Commit" if is_linter else "❌ Reject Patch"
                
                if st.button(reject_label, key=f"reject_{ticket_id}"):
                    update_incident_status(ticket_id, 'REJECTED')
                    st.info("Ticket transaction aborted. Cleaning queue...")
                    time.sleep(1)
                    st.rerun()