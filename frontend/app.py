import streamlit as st
import requests
import json

BACKEND_URL = "http://localhost:8000"

st.title("Scheduled Agent Runner")

# View Results
st.header("Past Results")
if st.button("Refresh Results"):
    try:
        response = requests.get(f"{BACKEND_URL}/results")
        results = response.json()
        st.json(results)
    except:
        st.error("Backend not running")

# Schedule Workflow
st.header("Schedule Workflow")
workflow = st.selectbox("Workflow", ["daily_update"])
cron = st.text_input("Cron Expression", "0 9 * * *")  # Daily at 9am
if st.button("Schedule"):
    try:
        data = {"workflow": workflow, "cron": cron}
        response = requests.post(f"{BACKEND_URL}/schedule", json=data)
        st.success(response.json()["message"])
    except:
        st.error("Failed to schedule")

# Manual Run
st.header("Manual Run")
if st.button("Run Now"):
    try:
        response = requests.post(f"{BACKEND_URL}/run/{workflow}")
        st.success(response.json()["message"])
    except:
        st.error("Failed to run")