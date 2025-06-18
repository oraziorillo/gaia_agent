from langchain_ollama.chat_models import ChatOllama

chat_llama_3_1_8b_instruct_ollama = ChatOllama(
    model="llama3.1:8b-instruct-q8_0",
    temperature=0.0, 
    seed=42,
    top_p=0.95
)