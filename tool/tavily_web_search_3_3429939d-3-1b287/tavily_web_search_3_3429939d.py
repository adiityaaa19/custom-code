from langchain_community.tools.tavily_search import TavilySearchResults
from mcp.server.fastmcp import FastMCP
import logging
from dotenv import load_dotenv
import os

load_dotenv()
logger = logging.getLogger(__name__)
Tavily_API_KEY = os.getenv("TAVILY_API_KEY", "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")

from signal import signal, SIGINT, SIGTERM
import sys

def signal_handler(sig, frame):
    logger.info("Signal received, shutting down gracefully...")
    sys.exit(0)

signal(SIGINT, signal_handler)
signal(SIGTERM, signal_handler)

mcp = FastMCP(
    name="tavily",
    port=80,
    timeout=30,
    debug=True
)

@mcp.tool()
def tool_tavily(query: str) -> str:
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
 
    Returns:
        str: A response summarizing the search results.
    """
   
    logger.info("Tavily search tool activated")
   
    # Initialize the Tavily search tool with the specified max_results parameter  # Default to 5 results if not provided
    tavily_tool = TavilySearchResults()
 
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
    mcp.run(transport='sse')  # STDIO for local protocol