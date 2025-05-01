# search_tool.py

# TavilySearchResults is a LangChain-compatible web search tool
from langchain_community.tools.tavily_search import TavilySearchResults

# ----------------------------------------
# Tool: Web search using Tavily API
# Usage: Returns top 2 relevant results
# ----------------------------------------
search_tool = TavilySearchResults(max_results=2)
