from fastapi import FastAPI, HTTPException
from typing import Dict
from src.backend.models.server_models import StartChatResponse, ChatResponse, ChatMessage, ChatHistory
import uuid
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Chat Assistant API",
    description="A virtual assistant powered by LLM",
    version="1.0.0"
)

# In-memory storage for chat sessions (use a database in production)
chat_sessions: Dict[str, dict] = {}

# Endpoints
@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Chat Assistant API",
        "endpoints": {
            "start_chat": "/start_chat",
            "chat": "/chat/{session_id}"
        }
    }


@app.post("/start_chat", response_model=StartChatResponse)
def start_chat():
    """
    Initialize a new chat session.
    Returns a unique session_id to be used for subsequent chat messages.
    """
    session_id = str(uuid.uuid4())
    
    # Initialize session with empty message history
    chat_sessions[session_id] = {
        "created_at": datetime.now(),
        "messages": []
    }
    
    return StartChatResponse(
        session_id=session_id,
        message="Chat session created successfully. Use this session_id to send messages.",
        created_at=chat_sessions[session_id]["created_at"]
    )


@app.post("/chat/{session_id}", response_model=ChatResponse)
def chat_with_space(session_id: str, chat_message: ChatMessage):
    """
    Send a message to the chat assistant and receive a response.
    
    Args:
        session_id: The unique session identifier from start_chat
        chat_message: The user's message
    
    Returns:
        ChatResponse with the assistant's reply
    """
    # Check if session exists
    if session_id not in chat_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found. Please start a new chat session."
        )
    
    # Get the session
    session = chat_sessions[session_id]
    
    # Store user message
    session["messages"].append({
        "role": "user",
        "content": chat_message.message,
        "timestamp": datetime.now().isoformat()
    })
    
    # TODO: Replace this with actual LLM integration
    # For now, using a simple echo response
    assistant_response = f"Echo: {chat_message.message}"
    
    # In production, you would call your LLM here:
    # assistant_response = call_llm_api(
    #     messages=session["messages"],
    #     model="your-model"
    # )
    
    # Store assistant response
    session["messages"].append({
        "role": "assistant",
        "content": assistant_response,
        "timestamp": datetime.now().isoformat()
    })
    
    return ChatResponse(
        session_id=session_id,
        user_message=chat_message.message,
        assistant_response=assistant_response,
        timestamp=datetime.now()
    )


@app.get("/chat/{session_id}/history", response_model=ChatHistory)
def get_chat_history(session_id: str):
    """
    Retrieve the complete chat history for a session.
    """
    if session_id not in chat_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found."
        )
    
    return ChatHistory(
        session_id=session_id,
        messages=chat_sessions[session_id]["messages"]
    )


@app.delete("/chat/{session_id}")
def delete_session(session_id: str):
    """
    Delete a chat session and its history.
    """
    if session_id not in chat_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found."
        )
    
    del chat_sessions[session_id]
    return {"message": f"Session {session_id} deleted successfully"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=4005)