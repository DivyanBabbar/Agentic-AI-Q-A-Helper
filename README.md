# Agentic AI Question–Answer Helper

## Overview

This is a **lightweight, rule-based agentic AI application** designed to demonstrate core concepts in agent architecture, including query classification, tool usage, short-term memory management, and API integration.

**Important:** This project uses a **rule-based classifier** and a **dictionary-based knowledge tool**, NOT machine learning or LLMs. It is intended as an educational implementation suitable for understanding agentic AI concepts at a college level.

## Features

- **Query Classification**: Automatically distinguishes between factual and conversational queries using rule-based heuristics
- **Tool Usage**: Integrates a simple dictionary search tool for factual queries
- **Short-Term Memory**: Maintains session-specific conversation history with a configurable sliding window
- **Session Handling**: Supports multiple concurrent sessions with isolated memory contexts
- **FastAPI Integration**: Provides a REST API with automatic Swagger documentation
- **Comprehensive Testing**: Full test suite covering all components

## Architecture

```
User
  ↓
FastAPI /chat Endpoint
  ↓
QuestionAnswerAgent
  ├─ Classify Query
  │  ├─ Factual      → DictionarySearchTool (returns fact from knowledge base)
  │  └─ Conversational → Template-based Response
  ├─ Store in Memory
  ├─ Return Response
  ↓
ConversationMemory (Session-specific)
  ├─ User Message
  ├─ Assistant Response
  └─ Sliding Window (keep last N messages)
  ↓
JSON Response with Memory Context
```

## Project Structure

```
Agentic-AI-Q-A-Helper/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── agent.py                 # Rule-based agent logic
│   ├── api.py                   # FastAPI application
│   ├── memory.py                # Session memory management
│   └── tools.py                 # Dictionary search tool
├── tests/
│   ├── __init__.py              # Tests package
│   └── test_agent.py            # Comprehensive test suite
├── .gitignore                   # Git ignore rules
├── README.md                    # This file
└── requirements.txt             # Python dependencies
```

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DivyanBabbar/Agentic-AI-Q-A-Helper.git
   cd Agentic-AI-Q-A-Helper
   ```

2. **Create a virtual environment:**
   
   **Windows (PowerShell):**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
   
   **Windows (Command Prompt):**
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate.bat
   ```
   
   **macOS/Linux:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the API

### Start the development server:

```bash
uvicorn app.api:app --reload
```

The API will be available at:
- **Main API**: http://127.0.0.1:8000
- **Interactive Docs (Swagger UI)**: http://127.0.0.1:8000/docs
- **Alternative Docs (ReDoc)**: http://127.0.0.1:8000/redoc

### Available Endpoints

- `POST /chat` - Submit a question or message
- `GET /health` - Health check
- `GET /` - API information

## API Usage

### Basic Example: Factual Query

**Using curl:**
```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -H "X-Session-Id: user123" \
  -d '{"message": "What is the capital of India?"}'
```

**Expected Response:**
```json
{
  "type": "factual",
  "answer": "New Delhi is the capital of India.",
  "memory_context": [
    {
      "role": "user",
      "message": "What is the capital of India?"
    },
    {
      "role": "assistant",
      "message": "New Delhi is the capital of India."
    }
  ]
}
```

### Basic Example: Conversational Query

**Using curl:**
```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -H "X-Session-Id: user123" \
  -d '{"message": "Hello!"}'
```

**Expected Response:**
```json
{
  "type": "conversational",
  "answer": "Hello! I'm an Agentic AI Question-Answer Helper. I can answer factual questions or have a brief conversation. How can I help you?",
  "memory_context": [
    {
      "role": "user",
      "message": "What is the capital of India?"
    },
    {
      "role": "assistant",
      "message": "New Delhi is the capital of India."
    },
    {
      "role": "user",
      "message": "Hello!"
    },
    {
      "role": "assistant",
      "message": "Hello! I'm an Agentic AI Question-Answer Helper..."
    }
  ]
}
```

### Session Management

Sessions are identified by the `X-Session-Id` HTTP header. If no session ID is provided, a unique one is automatically generated:

```bash
# First request in a session
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -H "X-Session-Id: session_abc123" \
  -d '{"message": "What is Python?"}'

# Second request in the same session
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -H "X-Session-Id: session_abc123" \
  -d '{"message": "Tell me more about it."}'
```

The memory context will show the full conversation history for the session (limited by the sliding window).

## Testing

### Run the complete test suite:

```bash
pytest
```

### Run with verbose output:

```bash
pytest -v
```

### Run specific test file:

```bash
pytest tests/test_agent.py -v
```

### Run specific test class:

```bash
pytest tests/test_agent.py::TestConversationMemory -v
```

### Test Coverage

The test suite includes:

✓ **DictionarySearchTool**
  - Tool initialization
  - Exact match search
  - Case-insensitive search
  - Not-found handling

✓ **ConversationMemory**
  - Message addition
  - Sliding window enforcement
  - Separate session isolation
  - Session clearing

✓ **QuestionAnswerAgent**
  - Factual query classification
  - Conversational query classification
  - Tool usage for factual queries
  - Conversational response generation
  - Memory storage during processing
  - Multi-turn session handling

✓ **FastAPI Integration**
  - `/chat` endpoint with factual queries
  - `/chat` endpoint with conversational queries
  - Automatic session ID generation
  - Empty message handling
  - Health check endpoint
  - Session persistence across requests

### Test Execution Result

Running `pytest` will output:
```
tests/test_agent.py::TestDictionarySearchTool::test_tool_initialization PASSED
tests/test_agent.py::TestDictionarySearchTool::test_search_exact_match PASSED
tests/test_agent.py::TestDictionarySearchTool::test_search_case_insensitive PASSED
tests/test_agent.py::TestDictionarySearchTool::test_search_not_found PASSED
tests/test_agent.py::TestConversationMemory::test_memory_initialization PASSED
tests/test_agent.py::TestConversationMemory::test_add_message PASSED
tests/test_agent.py::TestConversationMemory::test_sliding_window_enforcement PASSED
tests/test_agent.py::TestConversationMemory::test_separate_session_memories PASSED
tests/test_agent.py::TestConversationMemory::test_get_nonexistent_session PASSED
tests/test_agent.py::TestConversationMemory::test_clear_session PASSED
tests/test_agent.py::TestQuestionAnswerAgent::test_agent_initialization PASSED
tests/test_agent.py::TestQuestionAnswerAgent::test_classify_factual_query PASSED
tests/test_agent.py::TestQuestionAnswerAgent::test_classify_conversational_query PASSED
tests/test_agent.py::TestQuestionAnswerAgent::test_factual_query_uses_tool PASSED
tests/test_agent.py::TestQuestionAnswerAgent::test_conversational_query_response PASSED
tests/test_agent.py::TestQuestionAnswerAgent::test_memory_storage_during_processing PASSED
tests/test_agent.py::TestQuestionAnswerAgent::test_multiple_turns_in_session PASSED
tests/test_agent.py::TestFastAPIIntegration::test_chat_endpoint_factual PASSED
tests/test_agent.py::TestFastAPIIntegration::test_chat_endpoint_conversational PASSED
tests/test_agent.py::TestFastAPIIntegration::test_chat_endpoint_without_session_id PASSED
tests/test_agent.py::TestFastAPIIntegration::test_chat_endpoint_empty_message PASSED
tests/test_agent.py::TestFastAPIIntegration::test_health_check PASSED
tests/test_agent.py::TestFastAPIIntegration::test_root_endpoint PASSED
tests/test_agent.py::TestFastAPIIntegration::test_session_persistence PASSED

======================== 24 passed in X.XXs ========================
```

## Example Response

### Full Conversational Example

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -H "X-Session-Id: demo_user" \
  -d '{"message": "What is the largest planet?"}'
```

**Response:**
```json
{
  "type": "factual",
  "answer": "Jupiter is the largest planet in our solar system.",
  "memory_context": [
    {
      "role": "user",
      "message": "What is the largest planet?"
    },
    {
      "role": "assistant",
      "message": "Jupiter is the largest planet in our solar system."
    }
  ]
}
```

## Limitations

### Current Implementation

1. **Dictionary Knowledge Base is Limited**: The tool only has ~15 facts. Real systems would use web search, APIs, or vector databases.

2. **Classification is Rule-Based**: Query classification uses simple keyword matching and heuristics, NOT machine learning or LLMs. This means it can misclassify edge cases.

3. **Conversational Responses are Template-Based**: Responses to conversational queries are generated from templates, NOT from an actual language model. The responses are limited and simplistic.

4. **Memory is In-Process and Volatile**: All memory is stored in RAM and is lost when the server restarts. There is no persistent storage.

5. **No Real-Time Web Access**: The agent cannot access live data, APIs, or the internet (by design).

6. **Limited Intent Recognition**: The agent recognizes only basic patterns and keywords. Sophisticated NLU is not implemented.

7. **No Multi-Turn Context Understanding**: While memory is tracked, the agent does not deeply understand conversation context or anaphora resolution.

### What This Project Is NOT

- ❌ This is NOT a full LLM-powered system
- ❌ This is NOT production-grade
- ❌ This does NOT use neural networks or deep learning
- ❌ This does NOT have persistent memory
- ❌ This does NOT connect to external APIs
- ❌ This is NOT a chatbot replacement

### What This Project IS

- ✅ An educational demonstration of agentic AI concepts
- ✅ A working implementation of query classification and tool use
- ✅ An example of session-based memory management
- ✅ A complete FastAPI-based REST API
- ✅ Fully tested and documented code
- ✅ Suitable for learning and prototyping

## Future Improvements

### Potential Enhancements

1. **LLM Integration**: Replace rule-based classification and template responses with calls to an LLM (OpenAI, Anthropic, Hugging Face, etc.)

2. **Vector Database**: Use embeddings and vector search (e.g., Pinecone, Weaviate, FAISS) instead of keyword matching for better fact retrieval

3. **Persistent Storage**: Add a database (PostgreSQL, MongoDB) to persist conversation history and user sessions

4. **Web Search Tool**: Integrate a real search API (Google Custom Search, Bing) for factual queries

5. **Advanced Intent Classification**: Use a dedicated NLU model (e.g., from Hugging Face) for more accurate query classification

6. **Multi-Model Tool Use**: Support multiple tools (calculator, weather, news, etc.) with dynamic tool selection

7. **Prompt Engineering**: Implement a prompt management system for more sophisticated LLM interactions

8. **Authentication**: Add user authentication and authorization

9. **Rate Limiting**: Implement rate limiting and quota management

10. **Monitoring**: Add logging, metrics, and observability for production deployment

## Code Quality

- **Type Hints**: Used throughout for clarity and IDE support
- **Docstrings**: All classes and major functions documented
- **Testing**: 24 comprehensive tests covering all components
- **No Hardcoded Secrets**: No API keys, passwords, or sensitive data in code
- **Clean Separation**: Modules are logically organized and independently testable
- **Clear Names**: Variables and functions have descriptive, self-documenting names

## Author

Created as an educational project demonstrating agentic AI concepts.

## License

Open source for educational purposes.

## Questions or Contributions?

Feel free to open issues or submit pull requests!
