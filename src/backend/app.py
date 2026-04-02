from fastapi import FastAPI, HTTPException
from src.backend.models.server_models import StartChatResponse, ChatResponse, ChatMessage, ChatHistory
from src.backend.database_handlers.sq3_handler import ChatDatabase
from src.backend.space_assistants.llama_assistant import SpaceChatAssistant
import uuid
from datetime import datetime
import uvicorn
from dotenv import load_dotenv
from os import environ

load_dotenv('src/backend/.env')

app = FastAPI(
    title="Chat Assistant API",
    description="A virtual assistant powered by LLM",
    version="1.0.0"
)

db = ChatDatabase(db_path='./chat_sessions.db')
space_assistant = SpaceChatAssistant(
    prompt_templates_path='src/backend/prompts/llama_prompts',
    model_name=environ['MODEL_NAME']
)

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
    
    chat_session = db.create_session(session_id)
    
    return StartChatResponse(
        session_id=session_id,
        message="Chat session created successfully. Use this session_id to send messages.",
        created_at=chat_session["created_at"]
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

    current_session = db.get_session(session_id)

    # Check if session exists
    if not current_session:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found. Please start a new chat session."
        )
    
    if current_session['status'] == 'closed':
        raise HTTPException(
            status_code=410,
            detail=f"Session {session_id} found but is already closed! Please start a new chat session."
        )

    
    chat_history = db.get_messages(
        session_id=session_id
    )
        
    # TODO: Replace this with actual LLM integration
    # For now, using a simple echo response
    assistant_response, should_chat_end = space_assistant(
        current_user_message=chat_message.message,
        chat_history=chat_history
    )

    # Store user and assistant messages for history tracking.
    db.add_message(
        session_id=session_id,
        role="user",
        content=chat_message.message
    )
    
    db.add_message(
        session_id=session_id,
        role="assistant",
        content= assistant_response
    )

    if should_chat_end:
        # Session has reached a natural end as determined by the assistant.
        db.close_session(session_id)
    
    return ChatResponse(
        session_id=session_id,
        user_message=chat_message.message,
        assistant_response=assistant_response,
        timestamp=datetime.now(),
        session_ended=should_chat_end
    )


@app.get("/chat/{session_id}/history", response_model=ChatHistory)
def get_chat_history(session_id: str):
    """
    Retrieve the complete chat history for a session.
    """

    current_session = db.get_session(session_id)

    if not current_session:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found."
        )
        
    chat_messages = db.get_messages(
        session_id=session_id
    )
    
    return ChatHistory(
        session_id=session_id,
        messages=chat_messages,
        session_ended=current_session['status'] == 'closed'
    )


@app.delete("/chat/{session_id}")
def delete_session(session_id: str):
    """
    Delete a chat session and its history.
    """
    if not db.session_exists(session_id):
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found."
        )
    
    db.delete_session(session_id)
    return {"message": f"Session {session_id} deleted successfully"}

@app.post("/end_chat/{session_id}")
def end_chat(session_id: str):
    """
    Marks a chat session as closed in the DB. This is triggered
    manually by the user via the frontend.
    """

    current_session = db.get_session(session_id)

    if not current_session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")

    if current_session['status'] == 'closed':
        raise HTTPException(status_code=410, detail=f"Session {session_id} is already closed.")

    db.close_session(session_id)
    return {"message": f"Session {session_id} ended successfully."}


if __name__ == "__main__":
    uvicorn.run(app, host=environ['HOST_NAME'], port=int(environ['HOST_PORT']))