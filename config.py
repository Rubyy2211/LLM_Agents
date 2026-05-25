from adapters.llm.ollama_llm import OllamaLLM
from adapters.retriever.chroma_retriever import ChromaRetriever
from domain.chatbot_service import ChatbotService
def build_chatbot():
    llm = OllamaLLM(base_url="http://localhost:11434/api", model="gemma2:27b")
    retriever = ChromaRetriever(collection_name="dni")
    return ChatbotService(llm=llm, retriever=retriever)