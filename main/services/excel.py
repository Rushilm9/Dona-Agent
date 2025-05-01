# ✅ Necessary Imports
import pandas as pd
import os
import datetime
from datetime import timedelta, time
import textwrap
import difflib
import base64
from pandasai import SmartDataframe
from langchain_openai import AzureChatOpenAI
import numpy as np

# ✅ Load Azure OpenAI LLM configuration
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    temperature=0.7,  # Balanced creativity + reliability
)

# ------------------------------------------------------------
# ✅ Query Enhancement Logic — Auto-extends user intent
# ------------------------------------------------------------
def enhance_query(query: str) -> str:
    """
    Adds intelligent context/instructions to the query 
    based on keywords like chart, name, or date.

    Returns:
        Enhanced query string.
    """
    graph_keywords = ["chart", "graph", "plot", "trend"]
    name_keywords = ["employee", "customer", "name", "people", "person"]
    date_keywords = ["date", "time", "month", "year", "day", "duration"]

    query_lower = query.lower()
    base = ""
    added_something = False

    if any(kw in query_lower for kw in graph_keywords):
        base += (
            "If creating a chart or plot, use figsize=(12,6), wrap any x-axis labels longer than 20 characters "
            "onto multiple lines (e.g. via textwrap.fill), set xtick rotation=90 and ha='center', "
            "and save the PNG with bbox_inches='tight'. "
        )
        added_something = True

    if any(kw in query_lower for kw in name_keywords):
        base += (
            "Only return unique values. Always use the difflib library to perform similarity searches "
            "within the DataFrame and return any rows containing the query value. "
        )
        added_something = True

    if any(kw in query_lower for kw in date_keywords):
        base += (
            "Always check column types using df['col'].dtype (avoid pd.api, pd.core, etc). "
            "Convert formats gracefully with errors='coerce'. Use yyyy/mm/dd in final output. "
            "Show durations in hours. Return only unique values. "
        )
        added_something = True

    if not added_something:
        base += "Please provide unique values only. "

    return base + query

# ------------------------------------------------------------
# ✅ Main Function: AI-Powered Excel/CSV Question Answering
# ------------------------------------------------------------
async def ask_question_to_excel(file_path: str, question: str) -> dict:
    """
    Uses SmartDataFrame + Azure OpenAI to answer questions from Excel or CSV.

    Args:
        file_path (str): Path to the uploaded file
        question (str): User's natural language query

    Returns:
        dict: JSON-safe response from SmartDataFrame
    """
    # Enhance user input with intelligent hints
    enhanced_question = enhance_query(question)

    # Read file based on type
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    # Initialize SmartDataFrame with powerful custom config
    smart_df = SmartDataframe(
        df,
        config={
            "llm": llm,
            "whitelisted_libraries": ["repl", "textwrap", "base64"],
            "custom_whitelisted_dependencies": [
                "difflib", "datetime", "timedelta", "time", "pandas", "textwrap"
            ],
            "globals": {
                "pd": pd,
                "datetime": datetime,
                "timedelta": timedelta,
                "ValueError": ValueError,
                "time": time,
                "Exception": Exception,
                "textwrap": textwrap,
                "difflib": difflib,
                "base64": base64
            },
            "verbose": True,
            "enable_cache": False,
            "enforce_privacy": False,
            "save_charts": True,
            "show_code": True,
            "enable_retries": True,
            "max_retries": 5,
            "use_error_correction_framework": True
        }
    )

    # Ask the enhanced question to the LLM-powered dataframe
    response = smart_df.chat(enhanced_question)

    # ✅ Normalize output for JSON responses
    if isinstance(response, dict):
        if "value" in response and isinstance(response["value"], pd.DataFrame):
            response["value"] = response["value"].to_dict(orient="records")

        # Convert NumPy ints to Python ints (for serialization)
        if "total" in response and isinstance(response["total"], (np.integer,)):
            response["total"] = int(response["total"])

        if "amount" in response and isinstance(response["amount"], (np.integer,)):
            response["amount"] = int(response["amount"])

    return response
