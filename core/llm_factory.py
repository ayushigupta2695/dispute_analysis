from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

def get_llm(provider="openai", temperature=0):
    if provider == "openai":
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=temperature
        )
    elif provider == "groq":
        return ChatGroq(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=temperature
        )
    else:
        raise ValueError("Unsupported LLM provider")
