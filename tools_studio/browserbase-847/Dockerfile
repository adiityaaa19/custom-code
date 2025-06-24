# Use a base image with Node.js (since Supergateway is a Node.js tool)
FROM node:18-alpine
 
# Install Supergateway
RUN npm install -g supergateway
 
# Copy the Tavily MCP tool (assuming we're building from the original)
# Alternatively, we could just use the existing image as a base
COPY --from=ghcr.io/metorial/mcp-container--browserbase--mcp-server-browserbase--browserbase /app /app
 
# Set up the working directory
WORKDIR /app
 
# The command that will run when the container starts
CMD ["sh", "-c", "supergateway --stdio \"node cli.js\" --sse --port 8080"]