from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="addtool",
    port=80,
    timeout=30,
    debug=True
)

@mcp.tool()
async def add_numbers(a: float, b: float) -> float:
    """
    Adds two numbers and returns the sum.

    Args:
        a (float): The first number
        b (float): The second number

    Returns:
        float: The sum of a and b
    """
    return a + b

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='sse')