"""Comprehensive tests for the Agentic AI Q&A Helper."""

import pytest
from fastapi.testclient import TestClient

from app.agent import QuestionAnswerAgent
from app.memory import ConversationMemory
from app.tools import DictionarySearchTool
from app.api import app


class TestDictionarySearchTool:
    """Tests for the DictionarySearchTool."""

    def test_tool_initialization(self):
        """Test that the tool initializes with a knowledge base."""
        tool = DictionarySearchTool()
        assert tool.knowledge_base is not None
        assert len(tool.knowledge_base) > 0

    def test_search_exact_match(self):
        """Test searching for an exact match."""
        tool = DictionarySearchTool()
        result = tool.search("capital of india")
        assert "New Delhi" in result

    def test_search_case_insensitive(self):
        """Test that search is case-insensitive."""
        tool = DictionarySearchTool()
        result = tool.search("CAPITAL OF FRANCE")
        assert "Paris" in result

    def test_search_not_found(self):
        """Test searching for non-existent fact."""
        tool = DictionarySearchTool()
        result = tool.search("unicorn population in madagascar")
        assert "don't have information" in result.lower()


class TestConversationMemory:
    """Tests for the ConversationMemory class."""

    def test_memory_initialization(self):
        """Test that memory initializes correctly."""
        memory = ConversationMemory(window_size=5)
        assert memory.window_size == 5
        assert len(memory.sessions) == 0

    def test_add_message(self):
        """Test adding messages to memory."""
        memory = ConversationMemory()
        memory.add_message("session1", "user", "Hello")
        memory.add_message("session1", "assistant", "Hi there!")

        history = memory.get_session_history("session1")
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["message"] == "Hello"
        assert history[1]["role"] == "assistant"
        assert history[1]["message"] == "Hi there!"

    def test_sliding_window_enforcement(self):
        """Test that the sliding window limits message retention."""
        memory = ConversationMemory(window_size=4)

        # Add 6 messages
        for i in range(6):
            memory.add_message("session1", "user" if i % 2 == 0 else "assistant", f"Message {i}")

        # Only the last 4 should be retained
        history = memory.get_session_history("session1")
        assert len(history) == 4
        # The oldest message should be Message 2, not Message 0
        assert "Message 2" in history[0]["message"]

    def test_separate_session_memories(self):
        """Test that different sessions have separate memories."""
        memory = ConversationMemory()

        memory.add_message("session1", "user", "Hello from session 1")
        memory.add_message("session2", "user", "Hello from session 2")

        history1 = memory.get_session_history("session1")
        history2 = memory.get_session_history("session2")

        assert len(history1) == 1
        assert len(history2) == 1
        assert "session 1" in history1[0]["message"]
        assert "session 2" in history2[0]["message"]

    def test_get_nonexistent_session(self):
        """Test getting history for a session that doesn't exist."""
        memory = ConversationMemory()
        history = memory.get_session_history("nonexistent")
        assert history == []

    def test_clear_session(self):
        """Test clearing a session's memory."""
        memory = ConversationMemory()
        memory.add_message("session1", "user", "Hello")
        assert len(memory.get_session_history("session1")) == 1

        memory.clear_session("session1")
        assert len(memory.get_session_history("session1")) == 0


class TestQuestionAnswerAgent:
    """Tests for the QuestionAnswerAgent."""

    def test_agent_initialization(self):
        """Test that the agent initializes correctly."""
        memory = ConversationMemory()
        agent = QuestionAnswerAgent(memory)
        assert agent.memory is memory
        assert agent.tool is not None

    def test_classify_factual_query(self):
        """Test classification of factual queries."""
        memory = ConversationMemory()
        agent = QuestionAnswerAgent(memory)

        assert agent.classify_query("What is the capital of India?") == "factual"
        assert agent.classify_query("Who is the president?") == "factual"
        assert agent.classify_query("Where is Paris?") == "factual"
        assert agent.classify_query("When was Python created?") == "factual"

    def test_classify_conversational_query(self):
        """Test classification of conversational queries."""
        memory = ConversationMemory()
        agent = QuestionAnswerAgent(memory)

        assert agent.classify_query("Hello!") == "conversational"
        assert agent.classify_query("How are you?") == "conversational"
        assert agent.classify_query("Thanks a lot!") == "conversational"
        assert agent.classify_query("Tell me about history.") == "conversational"

    def test_factual_query_uses_tool(self):
        """Test that factual queries use the search tool."""
        memory = ConversationMemory()
        agent = QuestionAnswerAgent(memory)

        result = agent.process_message("session1", "What is the capital of Japan?")

        assert result["type"] == "factual"
        assert "Tokyo" in result["answer"]

    def test_conversational_query_response(self):
        """Test that conversational queries generate appropriate responses."""
        memory = ConversationMemory()
        agent = QuestionAnswerAgent(memory)

        result = agent.process_message("session1", "Hello!")

        assert result["type"] == "conversational"
        assert len(result["answer"]) > 0

    def test_memory_storage_during_processing(self):
        """Test that messages are stored in memory during processing."""
        memory = ConversationMemory()
        agent = QuestionAnswerAgent(memory)

        agent.process_message("session1", "What is the largest planet?")

        history = memory.get_session_history("session1")
        assert len(history) == 2  # User message + assistant response
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"

    def test_multiple_turns_in_session(self):
        """Test processing multiple turns in the same session."""
        memory = ConversationMemory()
        agent = QuestionAnswerAgent(memory)

        agent.process_message("session1", "Hello!")
        agent.process_message("session1", "What is Python?")
        agent.process_message("session1", "Thanks!")

        history = memory.get_session_history("session1")
        assert len(history) == 6  # 3 turns × 2 messages per turn


class TestFastAPIIntegration:
    """Tests for the FastAPI integration."""

    def test_chat_endpoint_factual(self):
        """Test the /chat endpoint with a factual query."""
        client = TestClient(app)

        response = client.post(
            "/chat",
            json={"message": "What is the capital of India?"},
            headers={"X-Session-Id": "test_session1"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "factual"
        assert data["session_id"] == "test_session1"
        assert "New Delhi" in data["answer"]
        assert len(data["memory_context"]) == 2

    def test_chat_endpoint_conversational(self):
        """Test the /chat endpoint with a conversational query."""
        client = TestClient(app)

        response = client.post(
            "/chat",
            json={"message": "Hello!"},
            headers={"X-Session-Id": "test_session2"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "conversational"
        assert len(data["answer"]) > 0

    def test_chat_endpoint_without_session_id(self):
        """Test that endpoint generates a session ID if not provided."""
        client = TestClient(app)

        response = client.post("/chat", json={"message": "Hello!"})

        assert response.status_code == 200
        data = response.json()
        assert data["answer"] is not None
        assert len(data["session_id"]) == 36

    def test_chat_endpoint_empty_message(self):
        """Test that endpoint handles empty messages."""
        client = TestClient(app)

        response = client.post(
            "/chat",
            json={"message": ""},
            headers={"X-Session-Id": "test_session3"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "non-empty" in data["answer"].lower()

    def test_health_check(self):
        """Test the health check endpoint."""
        client = TestClient(app)

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self):
        """Test the root endpoint."""
        client = TestClient(app)

        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "endpoints" in data

    def test_session_persistence(self):
        """Test that session memory persists across requests."""
        client = TestClient(app)

        # First request
        response1 = client.post(
            "/chat",
            json={"message": "Hello!"},
            headers={"X-Session-Id": "persistent_session"},
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1["memory_context"]) == 2

        # Second request in same session
        response2 = client.post(
            "/chat",
            json={"message": "What is Python?"},
            headers={"X-Session-Id": "persistent_session"},
        )
        assert response2.status_code == 200
        data2 = response2.json()
        # Memory should now have 4 messages (2 from first turn + 2 from second turn)
        assert len(data2["memory_context"]) == 4
