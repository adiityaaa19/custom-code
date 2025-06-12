FROM node:18-alpine3.21

# Install MCP Inspector
RUN npm install -g @modelcontextprotocol/inspector

# Expose both frontend and backend ports
EXPOSE 6274 6277

# Run the inspector
CMD ["npx", "@modelcontextprotocol/inspector"]
