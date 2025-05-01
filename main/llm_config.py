# llm_config.py

import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

# Load environment variables from .env file
load_dotenv()

# ------------------------------
# Azure OpenAI Configuration
# ------------------------------
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# ------------------------------
# Return initialized LLM client
# ------------------------------
def get_llm():
    """
    Return an instance of AzureChatOpenAI model 
    configured for deterministic tool invocation.
    
    Returns:
        AzureChatOpenAI: Ready-to-use LLM client
    """
    llm = AzureChatOpenAI(
        azure_deployment=AZURE_OPENAI_DEPLOYMENT_NAME,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        openai_api_version="2024-05-01-preview",
        api_key=AZURE_OPENAI_API_KEY,
        temperature=0.0  # Ensures predictable tool usage
    )
    return llm

# Make this function accessible when imported with *
__all__ = ["get_llm"]
