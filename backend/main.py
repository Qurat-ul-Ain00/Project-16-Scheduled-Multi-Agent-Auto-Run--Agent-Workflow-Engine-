from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio
import json
import os
from datetime import datetime
import uuid

app = FastAPI()
scheduler = AsyncIOScheduler()

# Mock agents
def research_agent():
    return {"data": "Research data: Market trends show increase in AI adoption."}

def summary_agent():
    return {"summary": "Summary: AI is growing rapidly."}

def insight_agent():
    return {"insight": "Insight: Invest in AI stocks."}

agents = {
    "research": research_agent,
    "summary": summary_agent,
    "insight": insight_agent
}

# Workflow definition
workflows = {
    "daily_update": ["research", "summary", "insight"]
}

# Storage
RESULTS_FILE = "results.json"

def load_results():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_results(results):
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=4)

class ScheduleRequest(BaseModel):
    workflow: str
    cron: str  # e.g., "0 9 * * *" for daily at 9am

@app.on_event("startup")
async def startup_event():
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    await scheduler.shutdown()

async def run_workflow(workflow_name: str):
    if workflow_name not in workflows:
        print(f"Workflow {workflow_name} not found")
        return
    session_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    results = []
    for agent_name in workflows[workflow_name]:
        if agent_name in agents:
            result = agents[agent_name]()
            results.append({"agent": agent_name, "result": result})
        else:
            results.append({"agent": agent_name, "error": "Agent not found"})
    
    run_data = {
        "session_id": session_id,
        "timestamp": timestamp,
        "workflow": workflow_name,
        "results": results
    }
    
    all_results = load_results()
    all_results.append(run_data)
    save_results(all_results)
    
    # Notification: minimal, just print
    print(f"Workflow {workflow_name} completed. Session: {session_id}")

@app.post("/schedule")
async def schedule_workflow(request: ScheduleRequest):
    if request.workflow not in workflows:
        raise HTTPException(status_code=400, detail="Workflow not found")
    
    job_id = f"{request.workflow}_{uuid.uuid4()}"
    scheduler.add_job(run_workflow, CronTrigger.from_crontab(request.cron), id=job_id, args=[request.workflow])
    return {"job_id": job_id, "message": "Scheduled"}

@app.get("/results")
async def get_results():
    return load_results()

@app.post("/run/{workflow}")
async def manual_run(workflow: str):
    await run_workflow(workflow)
    return {"message": "Run completed"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
