from ollama import Client
from langchain_litellm import ChatLiteLLM
from catalog.config import Settings

MESSAGE_CONTENT = (
    "You are a professional data librarian specializing in dataset discovery. "
    "Your role is to help researchers find relevant datasets in the catalog. "
    "When answering discovery questions:\n"
    "- List the relevant datasets found in the catalog\n"
    "- Briefly explain why each dataset matches the user's query\n"
    "- Highlight key characteristics (keywords, descriptions) that make them relevant\n"
    "- Results include a relevance distance score (lower = more relevant). "
    "- Prioritize datasets with lower distance scores in your response.\n"
    "- If multiple datasets are found, organize them by relevance\n"
    "- Be direct and concise - focus on what datasets ARE available\n"
    "- If the query asks about existence (like 'is there'), give a clear yes/no answer first, then list the datasets\n"
    "- If you don't know answers just say you don't know. Don't try to make up an answer.\n"
    "Use the provided context from the catalog to give accurate, evidence-based responses."
)


class OllamaBot:
    def __init__(self):
        """Initializes the OllamaBot with API credentials from environment variables."""
        settings = Settings()
        self.OLLAMA_API_KEY = settings.ollama_api_key
        self.OLLAMA_BASE_URL = settings.ollama_api_url
        self.OLLAMA_MODEL = settings.ollama_model

        if not self.OLLAMA_API_KEY:
            raise ValueError("OLLAMA_API_KEY environment variable is not set.")
        if not self.OLLAMA_BASE_URL:
            raise ValueError("OLLAMA_API_URL environment variable is not set.")
        if not self.OLLAMA_MODEL:
            raise ValueError("OLLAMA_MODEL environment variable is not set.")

        self.client = Client(
            host=self.OLLAMA_BASE_URL,
            headers={"Authorization": "Bearer " + self.OLLAMA_API_KEY},
        )

    def chat(self, question: str, context: str) -> str:
        """
        Sends a chat message to the Ollama model with the given question and context.

        :param question: The user's question.
        :param context: The context to provide to the model.
        :return: The model's response.
        """

        messages = [
            {
                "role": "system",
                "content": MESSAGE_CONTENT,
            },
            {
                "role": "user",
                "content": f"Context: {context}\n\nQuestion: {question}",
            },
        ]

        resp = self.client.chat(self.OLLAMA_MODEL, messages=messages, stream=False)
        return resp["message"]["content"]

    def expand_query(self, query: str) -> str:
        """
        Expands a user's query using the Ollama model.

        :param query: The original user query.
        :return: The expanded query.
        """
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that expands user queries to include relevant keywords and synonyms for better dataset discovery.  Do not provide instruction on how to use, just the epanded query",
            },
            {
                "role": "user",
                "content": f"Expand the following query to include relevant keywords and synonyms:\n\n{query}",
            },
        ]

        resp = self.client.chat(self.OLLAMA_MODEL, messages=messages, stream=False)
        return resp["message"]["content"]

class VerdeBot:
    def __init__(self):
        """Initializes the VerdeBot with API credentials from environment variables."""
        settings = Settings()
        self.VERDE_API_KEY = settings.verde_api_key
        self.VERDE_URL = settings.verde_url
        self.VERDE_MODEL = settings.verde_model

        if not self.VERDE_API_KEY:
            raise ValueError("VERDE_API_KEY environment variable is not set.")
        if not self.VERDE_URL:
            raise ValueError("VERDE_URL environment variable is not set.")
        if not self.VERDE_MODEL:
            raise ValueError("VERDE_MODEL environment variable is not set.")

    def chat(self, question: str, context: str) -> str:
        llm = ChatLiteLLM(
            model=f"litellm_proxy/{self.VERDE_MODEL}",
            api_key=self.VERDE_API_KEY,
            api_base=self.VERDE_URL,
        )

        response = llm.invoke(question)
        return response.content
