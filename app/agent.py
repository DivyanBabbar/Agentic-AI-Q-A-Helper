"""Rule-based agent for question answering with classification and tool use."""

from typing import Dict, List, Tuple
from app.tools import DictionarySearchTool
from app.memory import ConversationMemory


class QuestionAnswerAgent:
    """
    A rule-based agent that classifies queries and uses tools to answer them.

    This is a lightweight, rule-based agent designed for educational purposes.
    It does NOT use an LLM. Query classification is based on simple heuristics.
    """

    def __init__(self, memory: ConversationMemory):
        """
        Initialize the agent.

        Args:
            memory: A ConversationMemory instance for session management.
        """
        self.memory = memory
        self.tool = DictionarySearchTool()
        self.factual_keywords = {
            "what",
            "who",
            "where",
            "when",
            "which",
            "how many",
            "how much",
            "is",
            "are",
            "was",
            "were",
            "capital",
            "largest",
            "smallest",
            "define",
            "explain",
        }
        self.conversational_keywords = {
            "hello",
            "hi",
            "how are you",
            "thank you",
            "thanks",
            "please",
            "good morning",
            "good afternoon",
            "good evening",
            "bye",
            "goodbye",
            "see you",
            "nice",
            "awesome",
            "great",
        }

    def classify_query(self, message: str) -> str:
        """
        Classify a query as factual or conversational using rule-based heuristics.

        Args:
            message: The user's message.

        Returns:
            Either "factual" or "conversational".
        """
        normalized = message.lower().strip()

        # Check for conversational patterns
        for keyword in self.conversational_keywords:
            if keyword in normalized:
                # But "how are you" might ask for facts too, so check context
                if "capital" in normalized or "what" in normalized:
                    return "factual"
                return "conversational"

        # Check for factual patterns
        for keyword in self.factual_keywords:
            if keyword in normalized:
                return "factual"

        # Default: if it's a complete sentence without question marks, assume conversational
        if "?" not in message:
            return "conversational"

        # If unsure, default to factual for queries with question marks
        return "factual"

    def process_message(self, session_id: str, user_message: str) -> Dict:
        """
        Process a user message and generate a response.

        Args:
            session_id: Unique session identifier.
            user_message: The user's message.

        Returns:
            A dictionary containing:
            - type: "factual" or "conversational"
            - answer: The generated answer
            - memory_context: Recent message history for context
        """
        # Store the user message in memory
        self.memory.add_message(session_id, "user", user_message)

        # Classify the query
        query_type = self.classify_query(user_message)

        # Generate response based on classification
        if query_type == "factual":
            answer = self.tool.search(user_message)
        else:
            answer = self._generate_conversational_response(user_message)

        # Store the assistant response in memory
        self.memory.add_message(session_id, "assistant", answer)

        # Get session history for context
        memory_context = self.memory.get_session_history(session_id)

        return {
            "type": query_type,
            "answer": answer,
            "memory_context": memory_context,
        }

    def _generate_conversational_response(self, message: str) -> str:
        """
        Generate a simple conversational response.

        This is NOT powered by an LLM. It uses simple template-based responses.

        Args:
            message: The user's message.

        Returns:
            A conversational response.
        """
        normalized = message.lower().strip()

        if any(
            word in normalized
            for word in ["hello", "hi", "hey", "greetings"]
        ):
            return "Hello! I'm an Agentic AI Question-Answer Helper. I can answer factual questions or have a brief conversation. How can I help you?"

        if any(word in normalized for word in ["how are you", "how's it going"]):
            return "I'm functioning well, thank you for asking! I'm ready to help you with questions or conversation."

        if any(word in normalized for word in ["thank you", "thanks"]):
            return "You're welcome! Feel free to ask me more questions."

        if any(word in normalized for word in ["bye", "goodbye", "see you"]):
            return "Goodbye! Feel free to reach out anytime you have questions."

        # Default conversational response
        return "That's interesting! If you have any factual questions, I'd be happy to help. Otherwise, feel free to chat!"
