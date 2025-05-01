from langchain_openai import AzureChatOpenAI
import os
from dotenv import load_dotenv

# ✅ Load environment variables from .env file
load_dotenv()

# ✅ Initialize the Azure OpenAI LLM client
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

# -------------------------------------------------------
# ✅ Main Function: Summarize or answer questions from text
# -------------------------------------------------------
def summarize_text(document_text: str, question: str) -> str:
    """
    Uses Azure OpenAI to analyze and summarize or extract answers 
    from a business report or long document.

    Args:
        document_text (str): Full text extracted from a PDF or document.
        question (str): A specific question asked by the user.

    Returns:
        str: The assistant’s concise and relevant answer.
    """
    prompt = f"""
You are an AI assistant helping a business analyst. Given the following business report, answer the question accurately and concisely.

Business Report:
\"\"\" 
{document_text} 
\"\"\"

Question: {question}
Answer:"""

    # Call the model with the crafted prompt
    response = llm.invoke(prompt)
    return response.content
