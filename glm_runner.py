import subprocess
import os
import streamlit as st

def run_glm():

    st.info("🚀 Running GLM Engine... please wait")

    result = subprocess.run(
        ["python", "glm_engine.py"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        st.success("✅ GLM completed successfully!")
        st.text(result.stdout)
        return True
    else:
        st.error("❌ GLM failed!")
        st.text(result.stderr)
        return False