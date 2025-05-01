# chains.py

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI  # or your custom LLM wrapper
from pydantic import BaseModel, Field
from typing import Optional, List

from models import EventSlots  # 👈 Pydantic model to structure extracted data
from llm_config import get_llm  # 👈 Reusable LLM initialization

# -----------------------------------------
# Prompt: Convert free-text into event data
# -----------------------------------------
prompt = PromptTemplate.from_template(
    """You are an assistant that extracts structured event‐creation parameters
    from a human request. Output must be strict JSON matching the Pydantic model.

    Human: "{input}"
    """
)

# -----------------------------------------
# Parser: Enforce structured Pydantic output
# -----------------------------------------
parser = PydanticOutputParser(pydantic_object=EventSlots)

# -----------------------------------------
# LLM: Load chat model (e.g., OpenAI, Azure)
# -----------------------------------------
llm = get_llm()

# -----------------------------------------
# Chain: Prompt → LLM → JSON Parser
# -----------------------------------------
chain = prompt | llm | parser
