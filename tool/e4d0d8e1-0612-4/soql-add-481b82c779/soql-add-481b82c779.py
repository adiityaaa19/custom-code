from mcp.server.fastmcp import FastMCP
import time
import signal
import sys
from tavily import TavilyClient
from langchain_community.tools.tavily_search import TavilySearchResults
import logging
import asyncio
from chatrequest import ChatRequest
import os

logger = logging.getLogger(__name__)

def signal_handler(sig, frame):
    print("Signal handler called with signal:", sig)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

mcp = FastMCP(
    name="soql-add",
    port=80,
    timeout=30,
    debug=True
)

os.environ["TAVILY_API_KEY"] = "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"

@mcp.tool()
def tool_tavily(query: str, tool_params: ChatRequest) -> str:
    """
    Tool for performing web-based searches using Tavily. Use this tool compulsorily only when other tools in the
    system are unable to provide an answer, and the query requires retrieving information from the web.
   
    Ideal Use Cases:
    - When the user's query explicitly requires recent or internet-based information.
    - When other tools in the system, such as SQL or vector search, cannot answer the query adequately.
    - Queries that involve trending topics, recent news, or open-ended exploration.
 
    Examples:
    - "What are the latest advancements in AI?"
    - "Who won the 2024 FIFA World Cup?"
 
    Args:
        query (str): The user's search query.
        tool_params (dict): Parameters for configuring the tool, such as max results.
 
    Returns:
        str: A response summarizing the search results.
    """
    
    logger.info("Tavily search tool activated")
    print("tool_params intool tavily /*/*/*/", tool_params)

    max_results = tool_params.max_results  # Default to 5 results if not provided
    # Initialize the Tavily search tool with the specified max_results parameter
    # max_results = tool_params.get('max_results', 2)  # Default to 5 results if not provided
    tavily_tool = TavilySearchResults(max_results=max_results)
 
    # Perform the search
    try:
        search_results = tavily_tool.run(query)
       
        print("Search results:", search_results)
 
        # Format the results into a readable response
       
        return search_results
 
    except Exception as e:
        logger.error(f"Error performing Tavily search: {e}")
        return f"An error occurred during the search: {str(e)}"
    

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='sse')