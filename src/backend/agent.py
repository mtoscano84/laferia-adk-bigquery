import os
import json
import asyncio
from datetime import datetime
import certifi
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fix SSL certificate verification issues on macOS
os.environ['SSL_CERT_FILE'] = certifi.where()

# Using Gemini API (Global) - Requires GEMINI_API_KEY in environment
# Do not force Vertex AI
if "GOOGLE_GENAI_USE_VERTEXAI" in os.environ:
    del os.environ["GOOGLE_GENAI_USE_VERTEXAI"]

from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.cloud import bigquery
from google.genai import types
import google.auth
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ADK Imports
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode

# --- Configuration ---
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("PROJECT_ID") or "mtoscano-dev-sandbox"
DATASET_ID = os.environ.get("BIGQUERY_DATASET", "feria_sevilla_2025")

# Ensure project is set for default client behavior
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID

MODEL_ID = "gemini-3-flash-preview" # Standard foundational model

app = FastAPI(title="Feria de Sevilla AI Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_chart(query: str, title: str, chart_type: str = "bar") -> str:
    """Creates a chart from a SQL query and saves it as chart.png in the frontend directory.
    
    Args:
        query: The SQL query to run. The first column is used for X axis. Subsequent columns are plotted.
        title: The title of the chart.
        chart_type: 'bar' or 'line'.
        
    Returns:
        A message indicating success and instructions for the agent.
    """
    print(f"📊 [create_chart] Called with query: {query}, type: {chart_type}")
    try:
        client = bigquery.Client()
        df = client.query(query).to_dataframe()
        
        if df.empty:
            return "ERROR: No data found for this query."
            
        plt.figure(figsize=(12, 6))
        x_col = df.columns[0]
        
        if chart_type == "line":
            if len(df.columns) == 3:
                # Check for scale difference to use dual axis
                col1 = df.columns[1]
                col2 = df.columns[2]
                max1 = df[col1].max()
                max2 = df[col2].max()
                
                if max1 > 0 and max2 > 0 and (max1 / max2 > 20 or max2 / max1 > 20):
                    # Use dual Y-axis
                    fig, ax1 = plt.subplots(figsize=(12, 6))
                    
                    color = 'tab:blue'
                    ax1.set_xlabel(x_col, fontsize=12)
                    ax1.set_ylabel(col1, color=color, fontsize=12)
                    ax1.plot(df[x_col], df[col1], marker='o', color=color, linewidth=2, label=col1)
                    ax1.tick_params(axis='y', labelcolor=color)
                    
                    ax2 = ax1.twinx()
                    color = 'tab:orange'
                    ax2.set_ylabel(col2, color=color, fontsize=12)
                    ax2.plot(df[x_col], df[col2], marker='s', color=color, linewidth=2, label=col2)
                    ax2.tick_params(axis='y', labelcolor=color)
                    
                    plt.title(title, fontsize=16, fontweight='bold')
                    fig.tight_layout()
                    ax1.grid(True, linestyle='--', alpha=0.5)
                else:
                    # Standard line plot
                    for col in df.columns[1:]:
                        plt.plot(df[x_col], df[col], marker='o', linewidth=2, label=col)
                    plt.legend()
                    plt.title(title, fontsize=16, fontweight='bold')
                    plt.xlabel(x_col, fontsize=12)
                    plt.ylabel("Valor", fontsize=12)
                    plt.grid(True, linestyle='--', alpha=0.5)
            else:
                # Standard line plot for other cases
                for col in df.columns[1:]:
                    plt.plot(df[x_col], df[col], marker='o', linewidth=2, label=col)
                plt.legend()
                plt.title(title, fontsize=16, fontweight='bold')
                plt.xlabel(x_col, fontsize=12)
                plt.ylabel("Valor", fontsize=12)
                plt.grid(True, linestyle='--', alpha=0.5)
        else:
            # Bar chart
            if len(df.columns) > 2:
                df.plot(x=x_col, kind='bar', ax=plt.gca())
            else:
                plt.bar(df[x_col], df[df.columns[1]])
            plt.title(title, fontsize=16, fontweight='bold')
            plt.xlabel(x_col, fontsize=12)
            plt.ylabel("Valor", fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.5)
                
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        chart_path = "chart.png"
        plt.savefig(chart_path)
        plt.close()
        print(f"📊 [create_chart] Chart saved successfully to {chart_path}")
        
        return "SUCCESS: Chart generated. You MUST output the markdown image link `![Chart](chart.png)` in your response so the user can see it. Then you can interpret the data shown in the chart."
    except Exception as e:
        print(f"❌ [create_chart] Error: {str(e)}")
        return f"ERROR: Failed to generate chart: {str(e)}"

SYSTEM_PROMPT = f"""
You are 'Curro', an expert data analyst for the Feria de Sevilla. You help users understand operational insights and business intelligence regarding the event.

You have access to first-party tools to explore and query BigQuery databases.
The Google Cloud Project ID is '{PROJECT_ID}' and the Dataset ID is '{DATASET_ID}'. You can discover the available tables and their schemas using the provided tools. You must always qualify tables with `{PROJECT_ID}.{DATASET_ID}.table_name` in your SQL queries.

Guidelines:
1.  **Query**: Use the `execute_sql` tool to run optimized queries.
2.  **Synthesize**: Provide a clear, human-readable summary of the data retrieved.
3.  **Charts**: Use it only when the user explicitly asks for a chart, graph, or visual representation. Call the `create_chart` tool DIRECTLY with the SQL query. The tool supports `chart_type='bar'` and `chart_type='line'`.
4.  **Privacy**: Do NOT mention the technical Project ID ('{PROJECT_ID}') or Dataset ID ('{DATASET_ID}') in your responses to the user. Keep it natural and do not expose internal technical identifiers.
5.  **Language**: Respond in the same language the user used to ask the question. Keep "Feria de Sevilla" in Spanish.

Focus only on data related to the Feria de Sevilla.
"""

# --- ADK Initialization ---
GEMINI_MODEL = "gemini-3-flash-preview"
AGENT_NAME = "feria_agent"
APP_NAME = "feria_app"
USER_ID = "default_user"
SESSION_ID = "default_session"

# Use Application Default Credentials (ADC)
application_default_credentials, _ = google.auth.default()
credentials_config = BigQueryCredentialsConfig(
    credentials=application_default_credentials
)
tool_config = BigQueryToolConfig(write_mode=WriteMode.BLOCKED)

bigquery_toolset = BigQueryToolset(
    credentials_config=credentials_config,
    bigquery_tool_config=tool_config
)

bigquery_agent = Agent(
    model=GEMINI_MODEL,
    name=AGENT_NAME,
    description="Agent to answer questions about Feria de Sevilla data in BigQuery.",
    instruction=SYSTEM_PROMPT,
    tools=[bigquery_toolset, create_chart],
)

session_service = InMemorySessionService()
# Create session synchronously or use a helper
# The sample uses asyncio.run to create session. We can do that too.
session = asyncio.run(
    session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
)

runner = Runner(
    agent=bigquery_agent,
    app_name=APP_NAME,
    session_service=session_service
)

# --- Tracing Setup (Placeholder or Actual if package exists) ---
try:
    import mcp_toolbox.tracing as tracing
except ImportError:
    # Fallback/Mock tracing if module is missing
    class MockTracing:
        @staticmethod
        def trace(name=None):
            def decorator(func):
                def wrapper(*args, **kwargs):
                    print(f"🔍 [Mock Trace] Starting {name or func.__name__}")
                    return func(*args, **kwargs)
                return wrapper
            return decorator

        @staticmethod
        def span(name):
            class MockSpan:
                def __enter__(self):
                    print(f"🔍 [Mock Span] Entering {name}")
                def __exit__(self, exc_type, exc_val, exc_tb):
                    print(f"🔍 [Mock Span] Exiting {name}")
                def set_attribute(self, key, value):
                    print(f"🔍 [Mock Span] Attribute {key} = {value}")
            return MockSpan()
    
    tracing = MockTracing()
    


from fastapi.responses import FileResponse

@app.get("/api/chart.png")
async def get_chart():
    if os.path.exists("chart.png"):
        return FileResponse("chart.png")
    raise HTTPException(status_code=404, detail="Chart not found")

class Message(BaseModel):
    text: str

class ChatResponse(BaseModel):
    response: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(message: Message):
    """
    Endpoint to receive messages from the frontend and process with the AI Agent.
    """
    user_query = message.text
    
    try:
        content = types.Content(role="user", parts=[types.Part(text=user_query)])
        events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)
        
        final_response = "No response from agent."
        for event in events:
            print(f"🤖 [Agent Event]: {event}")
            if event.is_final_response():
                final_response = event.content.parts[0].text
                
        return ChatResponse(response=final_response)

    except Exception as e:
         print(f"❌ [Agent Error]: {str(e)}")
         return ChatResponse(response=f"Error in agent processing: {str(e)}")

# CLI running
if __name__ == "__main__":
    import uvicorn
    # In production, use standard port or get from env
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting FeriaBot Backend on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
