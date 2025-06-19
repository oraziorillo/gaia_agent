from langchain_ollama.chat_models import ChatOllama
from langchain_openai.chat_models import ChatOpenAI

chat_llama_3_1_8b_instruct_ollama = ChatOllama(
    model="llama3.1:8b-instruct-q8_0",
    temperature=0.0, 
    seed=42,
    top_p=0.95
)

chat_gpt_4o_mini = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0, 
    seed=42,
    top_p=0.95 
)