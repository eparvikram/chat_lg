from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
import os


load_dotenv()

# Fetch the OpenAI key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file. Please add it.")

# 1. Initialize the LLM
# We use gpt-4o for its advanced conversational abilities
llm = ChatOpenAI(
    model="gpt-4o",
    api_key=openai_api_key,
    temperature=0
)

# 2. Define the agent function
def conv_assistant(state: MessagesState) -> MessagesState:
    """
    A conversational assistant agent that greets the user and processes their request.
    
    Args:
        state (MessagesState): The current state of the conversation, including all messages.
        
    Returns:
        MessagesState: The updated state with the assistant's response.
    """
    
    # System message defining the assistant's role and instructions
    sys_msg_conv = SystemMessage(content="""
    **Your Core Responsibilities:**
    1. Welcome the user and politely ask how to assist.
    2. Understand the user's request.
    3. Decide to:
       - Handle the request directly (if it's a simple clarification or meta-task).
       - Route to a specialized agent (e.g., Frontend, Backend, Database) for technical tasks.
    4. Always maintain a polite and helpful tone.
    Start by greeting the user and asking how you can help.
    """)

    # Get the current messages from the state
    messages = state["messages"]
    
    # Invoke the LLM with the system message and the conversation history
    updated_response = llm.invoke([sys_msg_conv] + messages)
    
    # Return the new state with the AI's response appended
    return {"messages": [updated_response]}

# 3. Create the LangGraph state graph
builder = StateGraph(MessagesState)


builder.add_node("conv_assistant", conv_assistant)


builder.add_edge(START, "conv_assistant")
builder.add_edge("conv_assistant", END)


memory = MemorySaver()
react_graph = builder.compile(checkpointer=memory)