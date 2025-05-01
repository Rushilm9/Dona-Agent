# llm_observer.py

from langchain_core.prompts import PromptTemplate
from llm_config import get_llm

# Load the Azure LLM model
llm = get_llm()

# ------------------------------------------
# Prompt: Review tool output from LLM agent
# ------------------------------------------
observation_prompt = PromptTemplate.from_template(
    """
    You are reviewing a tool's output for a professional assistant.

    Context:
    - Original User Request: "{user_input}"
    - Tool Used: "{tool_used}"
    - Tool Output: "{tool_output}"

    Your Tasks:
    - If the tool output correctly fulfills the user request, format it nicely and return.
    - ⚡ Important: If the tool output shows a clear status or error like "conflict with meeting", "no availability", "contact not found", etc., **accept it** and **politely inform the user**.
    - ⚡ Important: If the tool correctly interprets casual references like 'tomorrow', 'today', 'next week' into proper dates based on system date, you can consider it correct.

    ONLY reply either:
    - A clear final message to user (formatted nicely).
    - OR "NOT COMPLETE" if it is totally wrong or confusing.
    """
)

# -------------------------------------------------------
# Observer Function: Uses LLM to validate tool response
# -------------------------------------------------------
async def observe_tool_output(user_input: str, tool_used: str, tool_output: str) -> str:
    """
    Determine whether a tool output is complete and valid.

    Args:
        user_input (str): Original query from the user.
        tool_used (str): Name of the tool that was triggered.
        tool_output (str): Raw output returned by the tool.

    Returns:
        str: Cleaned up response for the user or "NOT COMPLETE" if invalid.
    """
    # Format prompt with actual values
    formatted_prompt = observation_prompt.format(
        user_input=user_input,
        tool_used=tool_used,
        tool_output=tool_output
    )

    try:
        response = await llm.ainvoke(formatted_prompt)
        return response.content.strip()
    except Exception as e:
        print(f"❌ [DEBUG] LLM Observation Error: {e}")
        return "NOT COMPLETE"
