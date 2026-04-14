import os
import json
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv
from fastmcp import FastMCP
import signal

# Load environment variables from .env file
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

mcp = FastMCP(
    name="hi_by",
    host='0.0.0.0',
    port=8000,
    debug=True
)

@mcp.tool()
def run(input_data: dict) -> dict:
    """
    Custom Tool: Groq AI Generator Tool (with .env)

    Args:
        input_data (dict):
            {
                "query": "latest AI trends"
            }

    Returns:
        dict: Structured response
    """

    try:
        query = input_data.get("query", "")

        if not query:
            return {
                "status": "error",
                "message": "Query is required"
            }

        if not os.getenv("GROQ_API_KEY"):
            return {
                "status": "error",
                "message": "GROQ_API_KEY not found in environment variables"
            }

        # Call Groq API
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": """
You are a creative Kids Story Writer.

Your task:
- Write a fun, engaging, and imaginative story for children based on the user’s input
- Keep the language simple, friendly, and easy to understand
- Include characters, a small adventure, and a positive moral

STRICT OUTPUT RULE:
- ALWAYS return the output in clean format
- DO NOT return plain text or markdown

STYLE GUIDELINES:
- Make it colorful and fun 
- Keep tone playful and suitable for kids (age 5–10)
- Story length: medium (300–600 words)

"""
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            temperature=0.9,
            max_tokens=1000
        )

        ai_output = response.choices[0].message.content

        return {
            "status": "success",
            "tool_name": "Groq AI Tool (.env)",
            "query": query,
            "timestamp": datetime.utcnow().isoformat(),
            "result": ai_output
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def signal_handler(sig, frame):
    print("Shutting down MCP server...")
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    mcp.run(transport="http", path="/mcp")  # STDIO for local protocol