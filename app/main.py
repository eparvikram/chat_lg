from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.services import react_graph # Import the graph from your services file

# Initialize FastAPI app
app = FastAPI(
    title="LangGraph Chatbot API",
    description="An API for interacting with a LangGraph-based chatbot.",
    version="1.0.0"
)

# Pydantic model for the request body
class ChatRequest(BaseModel):
    message: str
    thread_id: str # Use a string for thread_id for more flexibility (e.g., UUIDs)

# Pydantic model for the response body
class ChatResponse(BaseModel):
    response: str
    thread_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint to chat with the LangGraph agent.
    - Takes a user message and a thread_id.
    - Invokes the graph to get a response.
    - Returns the AI's response.
    """
    try:
        # Configuration for the graph invocation, specifying the thread_id
        config = {"configurable": {"thread_id": request.thread_id}}
        
        # Prepare the input for the graph
        input_message = {"messages": [HumanMessage(content=request.message)]}
        
        # Invoke the graph to get the final state
        # We use .invoke() here for a simple request-response API call
        response_state = react_graph.invoke(input_message, config=config)
        
        # The response is in the 'messages' list; the last message is from the AI
        ai_message = response_state['messages'][-1]
        
        # Ensure the message is not empty and has content
        if not ai_message or not ai_message.content:
            raise HTTPException(status_code=500, detail="AI returned an empty response.")
            
        return ChatResponse(response=ai_message.content, thread_id=request.thread_id)

    except Exception as e:
        # Basic error handling
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to the Chatbot API. Please use the /docs endpoint to see the API documentation."}