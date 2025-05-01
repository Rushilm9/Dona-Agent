# main.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4
import os
import shutil

# Models and Agent Setup
from models import QueryRequest, QueryResponse
from agent_setup import get_chained_agent

# Routers (modular APIs)
from task_event_api import router as task_event_router
from contact_api import router as contacts_router
from email_api import router as email_team_router

# File Q&A Services
from services.summarize_pdf import summarize_text
from services.excel import ask_question_to_excel
from services.pdf_utils import extract_text_from_pdf

# -------------------------------------------
# FastAPI App Initialization
# -------------------------------------------
app = FastAPI(
    title="Donna Assistant API",
    version="1.0",
    description="FastAPI wrapper for Donna Assistant with tool tracking"
)

# -------------------------------------------
# CORS Configuration
# -------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For public demo purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------
# API Routers for modular endpoints
# -------------------------------------------
app.include_router(task_event_router, prefix="/api", tags=["Task & Event APIs"])
app.include_router(email_team_router, prefix="/api", tags=["Email & Teams APIs"])
app.include_router(contacts_router, prefix="/api", tags=["Contacts"])

# -------------------------------------------
# In-memory session-based file store
# -------------------------------------------
session_store = {}

class ChatRequest(BaseModel):
    session_id: str
    question: str

# -------------------------------------------
# Welcome endpoint
# -------------------------------------------
@app.get("/")
async def root():
    return {"message": "Welcome to Donna Assistant API"}

# -------------------------------------------
# Upload a file (PDF/Excel/CSV) for QA
# -------------------------------------------
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(('.pdf', '.xls', '.xlsx', '.csv')):
        raise HTTPException(status_code=400, detail="Only PDF, Excel, or CSV files are supported.")

    temp_folder = "temp"
    os.makedirs(temp_folder, exist_ok=True)

    session_id = str(uuid4())
    file_extension = os.path.splitext(file.filename)[-1].lower()
    temp_file_path = os.path.join(temp_folder, f"{session_id}{file_extension}")

    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_type = "pdf" if file_extension == ".pdf" else "excel"
    extracted_text = extract_text_from_pdf(temp_file_path) if file_type == "pdf" else None

    session_store[session_id] = {
        "file_path": temp_file_path,
        "file_type": file_type,
        "pdf_text": extracted_text,
        "chat_history": []
    }

    return {"session_id": session_id, "file_type": file_type}

# -------------------------------------------
# Chat with uploaded PDF or Excel file
# -------------------------------------------
@app.post("/chat/")
async def chat_with_file(chat_request: ChatRequest):
    session_id = chat_request.session_id
    question = chat_request.question

    session = session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    file_path = session["file_path"]
    file_type = session["file_type"]
    chat_history = session.get("chat_history", [])

    try:
        if file_type == "pdf":
            document_text = session.get("pdf_text", "")
            if not document_text:
                raise HTTPException(status_code=500, detail="PDF content is empty or not parsed.")
            answer = summarize_text(document_text, question)

        elif file_type == "excel":
            answer = await ask_question_to_excel(file_path, question)

        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")

        chat_history.append({"user": question, "assistant": answer})
        session["chat_history"] = chat_history

        return {"session_id": session_id, "answer": answer, "chat_history": chat_history}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------------------
# Main Assistant Agent Endpoint (LLM + Tools)
# -------------------------------------------
agent_runner = get_chained_agent()

@app.post("/ask", response_model=QueryResponse)
async def ask(request: QueryRequest):
    """
    Main endpoint to query Donna AI Assistant.
    Uses LangChain Agent with Microsoft Graph tools.
    """
    try:
        agent_result = await agent_runner(request.query)
        return QueryResponse(
            question=request.query,
            tool_used=agent_result.tool_used,
            response=agent_result.output,
            human_feedback="👍 Good"
        )
    except Exception as e:
        return QueryResponse(
            question=request.query,
            tool_used="error",
            response=f"❌ Failed: {str(e)}",
            human_feedback="👎 Error"
        )
