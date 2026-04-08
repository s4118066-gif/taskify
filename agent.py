import os
import logging
import datetime
import google.cloud.logging
from google.cloud import datastore
from dotenv import load_dotenv

# --- Framework & API Imports ---
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from mcp.server.fastmcp import FastMCP

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.tool_context import ToolContext

# --- 1. Setup Logging & Environment ---
try:
    cloud_logging_client = google.cloud.logging.Client()
    cloud_logging_client.setup_logging()
except Exception:
    logging.basicConfig(level=logging.INFO)

load_dotenv()
model_name = os.getenv("MODEL", "gemini-1.5-pro")

# --- 2. DATABASE SETUP ---
DB_ID = "sana"
db = datastore.Client(database=DB_ID)

mcp = FastMCP("WorkspaceTools")

# ---------------------------------------------------------
# 3. BULLETPROOF TOOLS
# ---------------------------------------------------------

@mcp.tool()
def add_task(title: str) -> str:
    """Adds a new task to Cloud Datastore."""
    try:
        key = db.key('Task')
        task = datastore.Entity(key=key)
        task.update({
            'title': title,
            'completed': False,
            'created_at': datetime.datetime.now()
        })
        db.put(task)
        return f"Success: Task '{title}' saved to {DB_ID} (ID: {task.key.id})."
    except Exception as e:
        return f"Database Error: {str(e)}"

@mcp.tool()
def list_tasks() -> str:
    """Fetches all tasks using a blank query to bypass index requirements."""
    try:
        query = db.query(kind='Task')
        all_entities = list(query.fetch())

        if not all_entities:
            return f"Your task list in {DB_ID} is currently empty."

        all_entities.sort(key=lambda x: x.get('created_at', datetime.datetime.min), reverse=True)

        task_list = []
        for task in all_entities:
            status = "✅️" if task.get('completed') else "⏳️"
            title = task.get('title') or "Untitled task"
            task_list.append(f"{status} {title} (ID: {task.key.id})")

        return f"📋 Cloud Tasks ({DB_ID}):\n" + "\n".join(task_list)
    except Exception as e:
        return f"Retrieval Error: {str(e)}"

@mcp.tool()
def complete_task(task_id: str) -> str:
    """Marks a task as complete using its numeric ID."""
    try:
        numeric_id = int(''.join(filter(str.isdigit, task_id)))
        key = db.key("Task", numeric_id)
        task = db.get(key)
        if task:
            task['completed'] = True
            db.put(task)
            return f"Success: Task {numeric_id} marked as complete in {DB_ID}."
        return f"Error: Task ID {numeric_id} not found in {DB_ID}."
    except Exception as e:
        return f"ID Error: {str(e)}"

@mcp.tool()
def add_note(title: str, content: str) -> str:
    """Saves a note to Cloud Datastore."""
    try:
        key = db.key("Note")
        note = datastore.Entity(key=key, exclude_from_indexes=['content'])
        note.update({
            'title': title,
            'content': content,
            'timestamp': datetime.datetime.now()
        })
        db.put(note)
        return f"Success: Note '{title}' archived (ID: {note.key.id})."
    except Exception as e:
        return f"Database Error: {str(e)}"

@mcp.tool()
def list_notes() -> str:
    """Lists all notes using the blank query method."""
    try:
        query = db.query(kind='Note')
        all_notes = list(query.fetch())
        if not all_notes:
            return "Your notebook is empty."

        all_notes.sort(key=lambda x: x.get('timestamp', datetime.datetime.min), reverse=True)
        return " Cloud Notes :\n" + "\n".join([f"- {n.get('title', 'Untitled')} (ID: {n.key.id})" for n in all_notes])
    except Exception as e:
        return f"Database Error: {str(e)}"

# ---------------------------------------------------------
# 4. MULTI-AGENT ORCHESTRATION
# ---------------------------------------------------------

def add_prompt_to_state(tool_context: ToolContext, prompt: str) -> dict[str, str]:
    tool_context.state["PROMPT"] = prompt
    return {"status": "success"}

workspace_coordinator = Agent(
    name="workspace_coordinator",
    model=model_name,
    description="Agent managing Cloud Datastore tasks and notes.",
    instructions="""
    You are an Executive Assistant. Use tools to satisfy the PROMPT provided in the shared state.
    1. For chores, use 'add_task'.
    2. To see tasks, use 'list_tasks'.
    3. To finish a task, use 'complete_task'.
    4. For info, use 'add_note' or 'list_notes'.
    USER REQUEST: {PROMPT}
    """,
    tools=[add_task, list_tasks, complete_task, add_note, list_notes],
    output_keys="execution_data"
)

response_formatter = Agent(
    name="response_formatter",
    model=model_name,
    description="Formats raw database output.",
    instructions="Summarize the EXECUTION_DATA for sahana: {execution_data}"
)

workspace_workflow = SequentialAgent(
    name="workspace_workflow",
    sub_agents=[workspace_coordinator, response_formatter]
)

root_agent = Agent(
    name="workspace_greeter",
    model=model_name,
    description="The main routing agent.",
    input_keys="user_input",
    instructions="""
    First, call 'add_prompt_to_state' using 'user_input'.
    Then, transfer to 'workspace_workflow'.
    """,
    tools=[add_prompt_to_state],
    sub_agents=[workspace_workflow]
)

# ---------------------------------------------------------
# 5. API ENDPOINT
# ---------------------------------------------------------

app = FastAPI()

class UserRequest(BaseModel):
    prompt: str

@app.post("/api/v1/workspace/chat")
async def chat(request: UserRequest):
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        enriched = f"[SYSTEM TIME: {now}]\nRequest: {request.prompt}"
        result = root_agent.invoke({"user_input": enriched})
        return {
            "status": "success",
            "reply": result.get("final_output", "Processed.")
        }
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)