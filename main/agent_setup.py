# donna_agent.py

import re
from datetime import date
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.agents import AgentAction

# Local modules
from llm_config import get_llm
from models import AgentResult
from llm_observer import observe_tool_output

# Tools from Microsoft Graph integrations
from graph_tools.tasks import tools as task
from graph_tools.events import tools as event
from graph_tools.presence_tools import tools as presence_tools
from graph_tools.teams_tools import tools as teams_tools
from graph_tools.user_management_tools import tools as user_tool
from graph_tools.contacts_tools import tools as contact
from graph_tools.email_tools import tools as email
from search_tool import search_tool

# Combine all tools into one list
all_tools = email + contact + user_tool + teams_tools + presence_tools + event + task + [search_tool]

# -------------------------
# Contextual behavior rules
# -------------------------
context = {
    "task": {
        "tool": "create_task",
        "analysis": "If task title or time is missing, ask the user before calling the tool.",
        "format": "Task added: Follow up with client at 3 PM."
    },
    "meeting": {
        "tool": "add_calendar_event_with_availability_check",
        "analysis": "If meeting time is missing, ask the user.",
        "format": "Meeting scheduled with Jane at 2 PM on Thursday."
    },
    "email": {
        "tool": "send_email,get_user_contacts",
        "analysis": "If recipient and body are present, ask the user to confirm before sending. Append 'Best regards, Rushil Mehta' during formatting.",
        "format": "Send email to Alex confirming project status. Confirm body before sending."
    }
}

# -------------------------
# Helper functions
# -------------------------
def beautify_context(context):
    """Convert dict context into readable bullet format."""
    return "\n".join(
        f"{k.capitalize()}:\n" + "\n".join([f"- {ik.capitalize()}: {iv}" for ik, iv in v.items()])
        for k, v in context.items()
    )

def contains_time(text):
    """Detect if the text contains time-related expressions."""
    patterns = [
        r"\b\d{1,2}(:\d{2})?\s?(AM|PM)\b", r"\btomorrow\b", r"\btonight\b", r"\bevening\b",
        r"\bmorning\b", r"\bafternoon\b", r"\bnoon\b", r"\bnext week\b"
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)

# -------------------------
# Memory management
# -------------------------
def save_pending_action(memory, action_type, details):
    """Store a pending action in memory."""
    clear_pending_action(memory)
    memory.add_ai_message(f"__PENDING__:type={action_type},details={details}")

def get_pending_action(memory):
    """Extract the most recent pending action."""
    for message in reversed(memory.messages):
        if message.type == "ai" and message.content.startswith("__PENDING__"):
            parts = message.content.replace("__PENDING__:", "").split(",")
            return {"type": parts[0].split("=")[1], "details": parts[1].split("=")[1]}
    return None

def clear_pending_action(memory):
    """Clear any existing pending action."""
    memory.messages = [m for m in memory.messages if not (m.type == "ai" and m.content.startswith("__PENDING__"))]

# -------------------------
# In-memory chat sessions
# -------------------------
session_memory_store = {}

def get_memory(session_id="clippy-session"):
    """Fetch or create chat memory for a session."""
    if session_id not in session_memory_store:
        session_memory_store[session_id] = ChatMessageHistory(session_id=session_id)
    return session_memory_store[session_id]

# -------------------------
# System prompt definition
# -------------------------
system_prompt = ChatPromptTemplate.from_messages([
    ("system", f"You are Donna, a professional admin assistant. Today is {date.today().strftime('%B %d, %Y')}."), 
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# -------------------------
# Main agent function
# -------------------------
def get_chained_agent(session_id="clippy-session"):
    """Builds the LangChain agent pipeline for Donna."""
    llm = get_llm()
    memory = get_memory(session_id)

    agent = create_tool_calling_agent(llm=llm, tools=all_tools, prompt=system_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=all_tools, verbose=True)

    runnable_agent = RunnableWithMessageHistory(
        agent_executor,
        lambda session_id: memory,
        input_messages_key="input",
        history_messages_key="chat_history"
    )

    async def run_full_chain(user_input: str):
        pending_action = get_pending_action(memory)

        # Prepare historical conversation and context for LLM polishing
        full_history = "\n".join(
            [f"User: {msg.content}" if msg.type == "human" else f"Assistant: {msg.content}"
             for msg in memory.messages if not msg.content.startswith("__PENDING__")]
        )
        safe_context_text = beautify_context(context)

        polish_prompt = PromptTemplate.from_template(
            """
            Conversation history:
            {recent_history}

            New input:
            {user_input}

            Context:
            {context}

            Instructions:
            - If responding to a pending action (task, meeting, email), complete it.
            - Always confirm email body with user before sending.
            - Append "Best regards, Rushil Mehta" to email body during formatting.
            - Ask for missing time if creating a task or meeting without time.
            - For email, use actual contact email if known.
            - There should be no placeholder in final emails.
            - Avoid repeating previous questions. Only ask once and reuse memory.
            """
        )

        try:
            formatted = polish_prompt.format(
                recent_history=full_history,
                user_input=user_input,
                context=safe_context_text
            )
            llm_response = await llm.ainvoke(formatted)
            polished_output = llm_response.content.strip()
        except Exception:
            return AgentResult(output="I couldn't process that. Can you clarify?", tool_used="error")

        # Handle continuation from pending state
        if pending_action:
            state_input = f"{pending_action['details']} at {user_input}"
            clear_pending_action(memory)
        else:
            state_input = polished_output

            if "task" in polished_output.lower() and not contains_time(user_input):
                save_pending_action(memory, "task", polished_output)
                return AgentResult(output="What time should I set for this task?", tool_used="waiting_for_time")

            if "meeting" in polished_output.lower() and not contains_time(user_input):
                save_pending_action(memory, "event", polished_output)
                return AgentResult(output="When would you like to schedule this meeting?", tool_used="waiting_for_time")

            if "send email" in polished_output.lower():
                contact_list = await search_tool.invoke({"query": "get_user_contacts"})
                recipient_email = None
                for contact in contact_list.get("contacts", []):
                    if contact["name"].lower() in polished_output.lower():
                        recipient_email = contact["email"]
                        break

                if not recipient_email:
                    save_pending_action(memory, "email", polished_output)
                    return AgentResult(output="Whom should I send this email to?", tool_used="waiting_for_recipient")

                if "confirm" not in polished_output.lower():
                    save_pending_action(memory, "email", polished_output)
                    return AgentResult(output="Please confirm the email body before sending.", tool_used="waiting_for_email_confirmation")

        # Invoke final tool execution via the agent
        result = await runnable_agent.ainvoke(
            {"input": state_input},
            config={
                "configurable": {"session_id": session_id},
                "run": {"metadata": {"return_intermediate_steps": True}}
            }
        )

        # Store final results and intermediate steps
        steps = result.get("intermediate_steps", [])
        output = result.get("output", "No response.")
        memory.add_user_message(user_input)
        memory.add_ai_message(output)

        # Post-process intermediate tool usage
        if not steps:
            return AgentResult(output=output, tool_used="final_output")

        action, observation = steps[0]
        if isinstance(action, AgentAction):
            observer_result = await observe_tool_output(user_input, action.tool, observation)
            if observer_result != "NOT COMPLETE":
                memory.add_ai_message(observer_result)
                return AgentResult(output="✅ Done. Let me know if you need anything else.", tool_used=action.tool)

        return AgentResult(output="✅ Action complete.", tool_used="fallback")

    return run_full_chain
