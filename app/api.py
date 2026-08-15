"""FastAPI application for the Question-Answer Agent."""

from fastapi import FastAPI, Header
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import uuid

from app.agent import QuestionAnswerAgent
from app.memory import ConversationMemory

# Initialize FastAPI app
app = FastAPI(
    title="Agentic AI Q&A Helper",
    description="A rule-based agentic AI system for question answering with memory and tool use.",
    version="1.0.0",
)

# Initialize agent with memory
memory = ConversationMemory(window_size=10)
agent = QuestionAnswerAgent(memory)


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(..., description="The user's message or question")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    type: str = Field(..., description="Query type: 'factual' or 'conversational'")
    answer: str = Field(..., description="The agent's answer")
    memory_context: List[Dict[str, str]] = Field(
        ..., description="Recent message history in the session"
    )


@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    x_session_id: Optional[str] = Header(None),
) -> ChatResponse:
    """
    Process a user message and return an answer.

    Args:
        request: ChatRequest containing the user's message.
        x_session_id: Optional session ID from X-Session-Id header.
                     If not provided, a new session ID is generated.

    Returns:
        ChatResponse with the agent's answer and memory context.
    """
    # Generate or use provided session ID
    session_id = x_session_id or str(uuid.uuid4())

    # Validate message
    if not request.message or not request.message.strip():
        return ChatResponse(
            type="error",
            answer="Please provide a non-empty message.",
            memory_context=[],
        )

    # Process the message through the agent
    result = agent.process_message(session_id, request.message)

    return ChatResponse(
        type=result["type"],
        answer=result["answer"],
        memory_context=result["memory_context"],
    )


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Agentic AI Q&A Helper"}


@app.get("/")
def root():
    """Root endpoint with basic info."""
    return {
        "message": "Welcome to the Agentic AI Question-Answer Helper",
        "endpoints": {
            "chat": "POST /chat - Submit a question or message",
            "docs": "/docs - Interactive API documentation (Swagger UI)",
            "health": "GET /health - Health check",
        },
    }
