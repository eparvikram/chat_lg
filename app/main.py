# app/main.py

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage, AIMessage # Import necessary message types
import logging

# Assuming your LangGraph service is in a 'service' module relative to the project root
# You might need to adjust this import based on your exact file structure
# For example, if 'service.py' is in the same directory as 'main.py' for the Docker context:
from .service import conversational_ai_service # Relative import for modules within the same package
                                             # If service.py is in the parent directory, you might need:
                                             # from ..service import conversational_ai_service
                                             # Or, for simplicity in a standalone backend folder:
                                             # from service import conversational_ai_service

# Set up logging (optional, but good for debugging)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Conversational AI Backend",
    description="API for the LangGraph-powered conversational AI.",
    version="1.0.0"
)

# --- CORS Configuration ---
# IMPORTANT: Adjust these origins based on where your frontend is hosted.
# For local development with index.html opened directly:
# "null" and "file://" are often needed.
# If you serve your HTML from a local dev server (e.g., http://localhost:3000 for React/Angular,
# or http://localhost:8000 for Python's http.server), add that specific origin.
origins = [
    "http://localhost",
    "http://localhost:8000", # Example if your UI is served on this port
    "http://localhost:8001", # If your UI is on this port, although rare for UI
    "http://127.0.0.1",
    "null",                   # For file:/// access (opening index.html directly)
    "file://",                # Another representation for file access
    "http://0.0.0.0:8001"     # To explicitly allow the reported origin from browser
    # Add your production frontend URL(s) here when deploying:
    # "https://your-frontend-domain.com",
    # "https://*.your-frontend-domain.com", # For subdomains
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers in the request
)
# --- END CORS Configuration ---


# Define a Pydantic model for incoming chat messages
# This helps FastAPI validate the request body
class ChatMessage(Request):
    message: str
    # You might also want to pass a thread_id from the UI
    thread_id: Optional[str] = "default_thread" # Provide a default thread_id

@app.get("/")
async def read_root():
    """Basic endpoint to check if the API is running."""
    return {"message": "Conversational AI Backend is running!"}

@app.post("/chat")
async def chat_endpoint(chat_message: ChatMessage):
    """
    Receives user messages and sends them to the conversational AI service.
    """
    user_message = chat_message.message
    thread_id = chat_message.thread_id # Get thread_id from the request

    logger.info(f"Received message for thread '{thread_id}': {user_message}")

    try:
        # Use your conversational AI service
        # Assumes service.py exposes 'conversational_ai_service' instance
        # If you want streaming, you'd adapt this to use StreamingResponse from FastAPI
        # and iterate over conversational_ai_service.stream_response
        ai_response_content = conversational_ai_service.invoke_response(
            user_message_content=user_message,
            thread_id=thread_id
        )
        logger.info(f"AI response for thread '{thread_id}': {ai_response_content}")
        return {"response": ai_response_content}
    

    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")