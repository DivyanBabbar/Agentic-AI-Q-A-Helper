"""Dictionary-based search tool for factual queries."""


class DictionarySearchTool:
    """A simple factual search tool using a Python dictionary."""

    def __init__(self):
        """Initialize the tool with a set of example facts."""
        self.knowledge_base = {
            "capital of india": "New Delhi is the capital of India.",
            "capital of france": "Paris is the capital of France.",
            "capital of japan": "Tokyo is the capital of Japan.",
            "capital of germany": "Berlin is the capital of Germany.",
            "capital of brazil": "Brasília is the capital of Brazil.",
            "largest planet": "Jupiter is the largest planet in our solar system.",
            "smallest planet": "Mercury is the smallest planet in our solar system.",
            "earth's atmosphere": "Earth's atmosphere is primarily composed of nitrogen (78%) and oxygen (21%).",
            "boiling point of water": "Water boils at 100 degrees Celsius at sea level.",
            "freezing point of water": "Water freezes at 0 degrees Celsius at sea level.",
            "python language": "Python is a high-level, interpreted programming language known for its simplicity.",
            "fastapi": "FastAPI is a modern web framework for building APIs with Python, known for speed and automatic documentation.",
            "what is machine learning": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.",
            "what is deep learning": "Deep learning is a subset of machine learning based on neural networks with multiple layers (deep neural networks).",
        }

    def search(self, query: str) -> str:
        """
        Search the knowledge base for a factual answer.

        Args:
            query: The search query string.

        Returns:
            A factual answer if found, otherwise a "not found" message.
        """
        # Normalize the query: lowercase and strip whitespace
        normalized_query = query.lower().strip()

        # Direct lookup
        if normalized_query in self.knowledge_base:
            return self.knowledge_base[normalized_query]

        # Check for partial matches (for queries that might have extra words)
        for key, value in self.knowledge_base.items():
            if key in normalized_query or normalized_query in key:
                return value

        # No match found
        return f"I don't have information about '{query}' in my knowledge base. Please ask about a different topic or rephrase your question."
